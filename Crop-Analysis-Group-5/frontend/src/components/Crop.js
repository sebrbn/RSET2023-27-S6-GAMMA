import React, { useState, useEffect } from "react";import "../App.css";

function Crop({ setPage }) {

const [predictions,setPredictions] = useState([]);

useEffect(()=>{

fetch("http://127.0.0.1:8000/data/rest")
.then(res => res.json())
.then(res => {

if(res.data && res.data.ml_predictions){
setPredictions(res.data.ml_predictions)
}

})
.catch(err => console.log("Error fetching predictions:", err));

},[])

const cropImages = {

rice:"/crops/rice.jpg",
maize:"/crops/maize.jpg",
kidneybeans:"/crops/kidneybeans.jpg",
chickpea:"/crops/chickpea.jpg",
lentil:"/crops/lentil.jpg",
pigeonpeas:"/crops/pigeonpeas.jpg",
mothbeans:"/crops/mothbeans.jpg",
mungbean:"/crops/mungbean.jpg",
blackgram:"/crops/blackgram.jpg",
pomegranate:"/crops/pomegranate.jpg",
banana:"/crops/banana.jpg",
mango:"/crops/mango.jpg",
grapes:"/crops/grapes.jpg",
watermelon:"/crops/watermelon.jpg",
muskmelon:"/crops/muskmelon.jpg",
apple:"/crops/apple.jpg",
orange:"/crops/orange.jpg",
papaya:"/crops/papaya.jpg",
coconut:"/crops/coconut.jpg",
cotton:"/crops/cotton.jpg",
jute:"/crops/jute.jpg",
coffee:"/crops/coffee.jpg"

}

const cropDescriptions = {

rice: "Thrives in warm climates with high rainfall and flooded soil.",
maize: "A versatile cereal crop suitable for moderate rainfall regions.",
kidneybeans: "Protein-rich legume that grows well in warm, well-drained soil.",
chickpea: "Drought-tolerant pulse crop ideal for dry climates.",
lentil: "Cool-season legume rich in protein and soil-improving nutrients.",
pigeonpeas: "Hardy legume crop suitable for semi-arid regions.",
mothbeans: "Drought-resistant crop grown in dry sandy soils.",
mungbean: "Fast-growing legume crop that improves soil fertility.",
blackgram: "Important pulse crop used widely in Indian cuisine.",
pomegranate: "Fruit crop suitable for dry climates with well-drained soil.",
banana: "Tropical fruit crop needing high moisture and warm temperature.",
mango: "Popular tropical fruit tree suited for warm climates.",
grapes: "Climbing fruit crop thriving in warm and dry climates.",
watermelon: "Summer fruit crop that grows well in sandy soil.",
muskmelon: "Warm-season fruit crop requiring well-drained soil.",
apple: "Temperate fruit tree needing cool climates.",
orange: "Citrus fruit crop requiring moderate rainfall and sunshine.",
papaya: "Fast-growing tropical fruit plant.",
coconut: "Coastal tropical crop that thrives in humid climates.",
cotton: "Cash crop used for textile production.",
jute: "Fiber crop grown in humid tropical regions.",
coffee: "High-value plantation crop grown in shaded hill regions."

}

return(

<div className="prediction-page">

<h2>Predicted Crops</h2>

<div className="prediction-container">

{predictions.map((crop,index)=>(

<div className={`crop-card rank-${index+1}`} key={index}>

<div className="rank-badge">

{index===0 && "🥇"}
{index===1 && "🥈"}
{index===2 && "🥉"}

</div>

<div className="crop-image">
<img src={cropImages[crop.crop]} alt={crop.crop}/>
</div>

<div className="crop-info">
<h3>{crop.crop}</h3>
{index===0 && <p className="confidence best">Best Match</p>}
{index===1 && <p className="confidence good">Good Alternative</p>}
{index===2 && <p className="confidence possible">Possible Crop</p>}

<p>{cropDescriptions[crop.crop]}</p>
</div>

</div>

))}

</div>

<div className="recommend-btn">

<button
className="action-btn"
onClick={() => setPage("recommendation")}
>
Get Recommended Crop
</button>

</div>

</div>

)

}

export default Crop;