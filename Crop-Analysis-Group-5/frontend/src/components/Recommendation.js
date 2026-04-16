import React, { useEffect, useState } from "react";
import "../App.css";

function Recommendation({ setPage }) {

const [crop,setCrop] = useState(null);

useEffect(()=>{

fetch("http://127.0.0.1:8000/data/rest")
.then(res => res.json())
.then(res => {

if(res.data && res.data.profit_crop){

setCrop({
name: res.data.profit_crop,
image: `/crops/${res.data.profit_crop}.jpg`,
description: "Most profitable crop based on soil, weather, and market price.",
temperature: `${res.data.weather_data.temperature} °C`,
ph: `${res.data.sensor_data.ph}`,
rainfall: `${res.data.weather_data.seasonal_rainfall} mm`,
moisture: `${res.data.sensor_data.soil_moisture}`

})

}

})
.catch(err => console.log("Recommendation fetch error:",err))

},[])

if(!crop) return <h2>Loading recommendation...</h2>

return(

<div className="recommendation-page">

<h2 className="section-title">Recommended Crop</h2>

<div className="recommendation-container">

<div className="recommendation-image-card">
<img src={crop.image} alt={crop.name}/>
</div>

<div className="recommendation-info-card">

<h2>{crop.name}</h2>

<p>{crop.description}</p>

<div className="crop-conditions">

<p><b>Current Field Conditions</b></p>

<p>Temperature: {crop.temperature}</p>

<p>Soil pH: {crop.ph}</p>

<p>Rainfall: {crop.rainfall}</p>

<p>Moisture: {crop.moisture}</p>

</div>

</div>

</div>

<div className="recommendation-btn">

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

export default Recommendation;