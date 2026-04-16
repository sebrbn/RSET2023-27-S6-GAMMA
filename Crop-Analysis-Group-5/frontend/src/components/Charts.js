import React from "react"
import { Bar } from "react-chartjs-2"
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from "chart.js"

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

function Charts({data}){

if(!data) return <p>No ML data available</p>

const chartData = {

labels:["Rainfall","Suitability"],

datasets:[{

label:"Prediction Metrics",

data:[data.rainfall, data.suitability * 100],

backgroundColor:["#3b82f6","#10b981"]

}]

}

return(

<div className="card">

<h3>Prediction Analytics</h3>

<Bar data={chartData}/>

</div>

)

}

export default Charts