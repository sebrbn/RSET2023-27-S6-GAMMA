import React, { useState, useEffect } from "react";
import { WiThermometer, WiHumidity, WiRain } from "react-icons/wi";
import { GiPlantRoots } from "react-icons/gi";
import { FaWater } from "react-icons/fa";
import { FiRefreshCw } from "react-icons/fi";
import LocationMap from "./LocationMap";

function Dashboard({ setPage }) {
const [moistureWarning,setMoistureWarning] = useState(null);
const [location, setLocation] = useState(null)

const [sensor,setSensor] = useState(null);
const [weather,setWeather] = useState(null);

useEffect(()=>{

const interval = setInterval(()=>{

// MQTT → sensors
fetch("http://127.0.0.1:8000/data/mqtt")
.then(res=>res.json())
.then(res=>{
if(res.data){
setSensor(res.data.sensor_data)
}
})

// REST → weather
fetch("http://127.0.0.1:8000/data/rest")
.then(res=>res.json())
.then(res=>{
if(res.data){
setWeather(res.data.weather_data)
}
if(res.data.moisture_analysis){
setMoistureWarning(res.data.moisture_analysis);
}

})

},5000)

return ()=>clearInterval(interval)

},[])

const refreshData = () => {

console.log("Refresh weather + sensor data")

}

const sendLocation = async () => {

if(!location) return;

const res=await fetch("http://127.0.0.1:8000/predict",{
method:"POST",
headers:{
"Content-Type":"application/json"
},
body:JSON.stringify({
location:`${location.lat},${location.lng}`
})
})

const data = await res.json();

setWeather(data.weather_data);
setSensor(data.sensor_data);

return data;

}

return (

<div className="dashboard">

{/* MAP CARD */}

<div className="map-card">

  <div className="map-card-header">

    <h2>Select Farm Location</h2>

    <button className="action-btn" onClick={()=>{
    sendLocation();
    }}>
    <FiRefreshCw style={{marginRight:"5px"}}/>
    Update Location
    </button>

  </div>

  <div className="map-container">
    <LocationMap setLocation={setLocation} />
  </div>

  {location && (
    <p className="map-coordinates">
      Lat: {location.lat.toFixed(4)} | Lon: {location.lng.toFixed(4)}
    </p>
  )}

</div>

{moistureWarning && moistureWarning.status !== "Ideal" && (

<div className="moisture-alert">

⚠️ <b>{moistureWarning.status}</b> — {moistureWarning.advice}

</div>

)}



{/* WEATHER + SENSOR */}

<div className="dashboard-row">

{/* WEATHER */}

<div className="dashboard-card">

<h2 className="section-title">
Weather Data (API)
</h2>

<div className="data-item">
<WiThermometer/>
<span className="label">Temperature</span>
<span className="value">{weather?.temperature}°C</span>
</div>

<div className="data-item">
<WiHumidity/>
<span className="label">Humidity</span>
<span className="value">{weather?.humidity}%</span>
</div>

<div className="data-item">
<WiRain/>
<span className="label">Rainfall</span>
<span className="value">{weather?.seasonal_rainfall} mm</span>
</div>

</div>

{/* SENSOR */}

<div className="dashboard-card">

<h2 className="section-title">
Field Sensors (IoT)
</h2>

<div className="data-item">
<GiPlantRoots/>
<span className="label">Soil pH</span>
<span className="value">{sensor?.ph}</span>
</div>

<div className="data-item">
<FaWater/>
<span className="label">Soil Moisture</span>
<span className="value">{sensor?.soil_moisture}</span>
</div>

<div className="data-item">
<WiThermometer/>
<span className="label">Soil Temperature</span>
<span className="value">{sensor?.temperature}°C</span>
</div>

<div className="data-item">
<WiHumidity/>
<span className="label">Air Humidity</span>
<span className="value">{sensor?.humidity}%</span>
</div>

</div>

</div>

{/* NAVIGATION BUTTONS */}

<div className="dashboard-buttons">

<button
className="action-btn"
onClick={async ()=>{
await sendLocation();
setPage("prediction");
}}
>
Prediction
</button>

<button
className="action-btn"
onClick={()=>setPage("recommendation")}
>
Recommendation
</button>

<button
className="action-btn"
onClick={()=>setPage("profit")}
>
Profit Analysis
</button>

</div>

</div>

)

}

export default Dashboard