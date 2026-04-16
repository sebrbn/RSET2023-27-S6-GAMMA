import React, { useEffect, useState } from "react";
import "../App.css";
import {
BarChart,
Bar,
XAxis,
YAxis,
CartesianGrid,
Tooltip,
ResponsiveContainer,
Cell
} from "recharts";

function Profit() {

const [predictedCrop,setCrop] = useState("");
const [yieldValue,setYield] = useState(0);
const [profitValue,setProfit] = useState(0);
const [data,setData] = useState([]);

useEffect(()=>{

fetch("http://127.0.0.1:8000/data/rest")
.then(res=>res.json())
.then(res=>{

const api = res.data;

setCrop(api.profit_crop);
setYield(api.estimated_yield);
setProfit(api.estimated_profit);

/* create chart from top 3 predicted crops */
const chartData = api.profit_comparison.map(c => ({
  crop: c.label,
  profit: c.estimated_profit
}));

setData(chartData);

})
.catch(err=>console.log("Profit fetch error:",err));

},[])

const COLORS = ["#047857", "#3b82f6", "#f59e0b"];

return(

<div className="profit-page">

<h2 className="section-title">Profit Analysis</h2>

{/* Summary cards */}

<div className="profit-summary">

<div className="profit-card">
<h3>Recommended Crop</h3>
<p>{predictedCrop}</p>
</div>

<div className="profit-card">
<h3>Estimated Yield</h3>
<p>{yieldValue} tons / acre</p>
</div>

<div className="profit-card highlight">
<h3>Estimated Profit</h3>
<p>₹{profitValue}</p>
</div>

</div>


{/* Chart */}

<div className="profit-chart-card">

<h3>Crop Profit Comparison</h3>

<ResponsiveContainer width="100%" height={350}>

<BarChart data={data}>

<CartesianGrid strokeDasharray="3 3" />

<XAxis dataKey="crop" />

<YAxis />

<Tooltip />

<Bar dataKey="profit" radius={[8,8,0,0]}>

{data.map((entry,index)=>(
<Cell key={`cell-${index}`} fill={COLORS[index]} />
))}

</Bar>

</BarChart>

</ResponsiveContainer>

</div>

</div>

)

}

export default Profit;