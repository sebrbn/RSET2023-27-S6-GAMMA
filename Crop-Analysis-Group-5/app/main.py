import json
from fastapi.middleware.cors import CORSMiddleware
import joblib
import pandas as pd
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import paho.mqtt.client as mqtt
from datetime import datetime, timedelta

MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "agriculture/crop_data"

last_rest_response = {"message": "No REST data processed yet"}
last_mqtt_response = {"message": "No MQTT data processed yet"}

MODEL = joblib.load("model/crop_prediction_model.pkl")
CROP_DF = pd.read_csv("datasets/crop_recommendation_with_yield_simple.csv")
PRICE_DF = pd.read_csv("datasets/CropPrice.csv")

app = FastAPI(title="Smart Agriculture API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------ WEATHER FUNCTIONS ------------------

def get_coordinates(location):
    try:
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1"
        res = requests.get(url, timeout=10).json()
        if "results" in res:
            return res["results"][0]["latitude"], res["results"][0]["longitude"]
    except:
        pass
    return None, None


def get_rainfall(lat, lon, days):
    try:
        end = datetime.today() - timedelta(days=1)
        start = end - timedelta(days=days)

        url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start.strftime('%Y-%m-%d')}&end_date={end.strftime('%Y-%m-%d')}&daily=precipitation_sum&timezone=auto"

        data = requests.get(url, timeout=10).json()

        if "daily" in data:
            return round(sum(data["daily"]["precipitation_sum"]), 2)

    except:
        pass

    return 0


def get_current_weather(lat, lon):

    try:

        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=relativehumidity_2m"

        data = requests.get(url, timeout=10).json()

        temp = data["current_weather"]["temperature"]
        humidity = data["hourly"]["relativehumidity_2m"][0]

        return {
            "temperature": temp,
            "humidity": humidity
        }

    except Exception as e:

        print("Weather API Error:", e)

        return {
            "temperature": 0,
            "humidity": 0
        }


# ------------------ SOIL MOISTURE ANALYSIS ------------------

def analyze_moisture(moisture):

    if moisture < 1750:
        return {
            "status": "Too Wet",
            "advice": "Soil too wet, delay planting"
        }

    elif moisture > 3200:
        return {
            "status": "Too Dry",
            "advice": "Soil too dry, irrigation required"
        }

    else:
        return {
            "status": "Ideal",
            "advice": "Soil moisture is suitable for planting"
        }


# ------------------ CORE PROCESSING ------------------

def process_recommendation(data_dict):

    location = data_dict['location']

    try:
        lat, lon = map(float, location.split(","))
    except:
        lat, lon = get_coordinates(location)

        if lat is None:
            return {"error": "Location not found"}

    seasonal_rain = get_rainfall(lat, lon, 120)
    weather_now = get_current_weather(lat, lon)

    moisture_result = analyze_moisture(data_dict['moisture'])

    input_df = pd.DataFrame(
        [[data_dict['temp'], data_dict['hum'], seasonal_rain, data_dict['ph']]],
        columns=['temperature', 'humidity', 'rainfall', 'ph']
    )

    # Get prediction probabilities
    probs = MODEL.predict_proba(input_df)[0]

    # Get crop labels
    labels = MODEL.classes_

    # Create dataframe of probabilities
    pred_df = pd.DataFrame({
      "crop": labels,
      "probability": probs
    })

    # Sort and get top 3
    top3 = pred_df.sort_values(by="probability", ascending=False).head(3)

    top3_predictions = top3.to_dict(orient="records")
    top3_labels = top3["crop"].tolist()

    ideal = CROP_DF.groupby("label")[['temperature','humidity','rainfall','ph']].mean().reset_index()
    merged = pd.merge(ideal, PRICE_DF, on="label")

    # keep only top3 predicted crops
    merged = merged[merged["label"].isin(top3_labels)]

    def calc_suitability(row):

        s = [
            max(0, 1 - abs(data_dict['temp'] - row["temperature"]) / 20),
            max(0, 1 - abs(data_dict['hum'] - row["humidity"]) / 50),
            max(0, 1 - abs(seasonal_rain - row["rainfall"]) / 200),
            max(0, 1 - abs(data_dict['ph'] - row["ph"]) / 3)
        ]

        return sum(s) / 4

    merged["Suitability"] = merged.apply(calc_suitability, axis=1)

    # calculate estimated yield using suitability
    merged["estimated_yield"] = merged["base_yield"] * merged["Suitability"]

    # calculate profit
    merged["estimated_profit"] = (merged["estimated_yield"] * merged["price_per_ton_inr"]).round(0)
    top_profit = merged[["label","estimated_profit"]].to_dict(orient="records")

    # choose crop with highest profit
    best = merged.loc[merged["estimated_profit"].idxmax()]

    return {

        "timestamp": datetime.now().isoformat(),

        "sensor_data": {
            "temperature": data_dict['temp'],
            "humidity": data_dict['hum'],
            "soil_moisture": data_dict['moisture'],
            "ph": data_dict['ph']
        },

        "weather_data": {
            "temperature": weather_now["temperature"],
            "humidity": weather_now["humidity"],
            "seasonal_rainfall": seasonal_rain
        },

        "ml_predictions": top3_predictions, #Used to be ml_crop when single crop was predicted (Now top 3)

        "profit_crop": best['label'],
        "estimated_yield": round(best["estimated_yield"], 2),
        "estimated_profit": round(best["estimated_profit"], 0),
        "suitability": round(best['Suitability'], 3),
        "profit_comparison": top_profit,
        "moisture_analysis": moisture_result
    }


# ------------------ MQTT ------------------

def on_connect(client, userdata, flags, rc):

    print(f"Connected to MQTT Broker with result code {rc}")
    client.subscribe(MQTT_TOPIC)


def on_message(client, userdata, msg):

    global last_mqtt_response

    try:

        payload = json.loads(msg.payload.decode())

        # MQTT messages don't contain location
        if "location" not in payload:
            last_mqtt_response = {
                "sensor_data":{
                    "temperature":payload["temp"],
                    "humidity":payload["hum"],
                    "soil_moisture":payload["moisture"],
                    "ph":payload["ph"]
                }
            }

        else:
            result = process_recommendation(payload)
            last_mqtt_response = result

        print("MQTT Data Updated")

    except Exception as e:
        print(f"MQTT Processing Error: {e}")


mqtt_client = mqtt.Client()

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

mqtt_client.loop_start()


# ------------------ REST API ------------------

class PredictionRequest(BaseModel):

    location: str
    


@app.post("/predict")
async def predict_via_rest(req: PredictionRequest):

    global last_rest_response

    sensor = last_mqtt_response.get("sensor_data")

    if not sensor:
        raise HTTPException(status_code=400, detail="No sensor data available")

    data = {
        "location": req.location,
        "temp": sensor["temperature"],
        "hum": sensor["humidity"],
        "ph": sensor["ph"],
        "moisture": sensor["soil_moisture"]
    }

    result = process_recommendation(data)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    last_rest_response = result

    return result


@app.get("/data/rest")
async def get_last_rest():

    return {"source": "REST API", "data": last_rest_response}


@app.get("/data/mqtt")
async def get_last_mqtt():

    return {"source": "MQTT EMQX", "data": last_mqtt_response}


# ------------------ SERVER START ------------------

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)