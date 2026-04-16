import React, { useState, useRef, useEffect } from "react";

function getBotResponse(message,data){

message = message.toLowerCase();

/* greetings */

if(message.includes("hello") || message.includes("hi")){
return "Hello! I am your agriculture assistant. Ask me about soil, crops, weather or profit.";
}

/* soil ph */

if(message.includes("ph") && message.includes("ideal")){
return "Ideal soil pH for most crops is between 6 and 7.";
}

if(message.includes("my ph") || message.includes("soil ph")){
if(data)
return `Your current soil pH is ${data.sensor_data.ph}.`;
}

/* moisture */

if(message.includes("moisture")){
if(data)
return `Current soil moisture is ${data.sensor_data.soil_moisture}.`;
return "Soil moisture indicates how much water is present in soil.";
}

/* temperature */

if(message.includes("temperature")){
if(data)
return `Current temperature is ${data.weather_data.temperature} °C.`;
}

/* humidity */

if(message.includes("humidity")){
if(data)
return `Current humidity is ${data.weather_data.humidity}%.`;
}

/* rainfall */

if(message.includes("rain")){
if(data)
return `Seasonal rainfall in your location is ${data.weather_data.seasonal_rainfall} mm.`;
}

/* predicted crops */

if(message.includes("predicted") || message.includes("prediction")){
if(data && data.ml_predictions){

let crops = data.ml_predictions.map(c=>c.crop).join(", ");
return `Top predicted crops are: ${crops}.`;
}

}

/* best crop */

if(message.includes("best crop") || message.includes("recommend") || message.includes("recommend")){
if(data)
return `Most profitable crop for your field is ${data.profit_crop}.`;
}

/* profit */

if(message.includes("profit")){
if(data)
return `Estimated profit for ${data.profit_crop} is ₹${data.estimated_profit}.`;
}

/* yield */

if(message.includes("yield")){
if(data)
return `Estimated yield for ${data.profit_crop} is ${data.estimated_yield} tons per acre.`;
}

/* soil advice */

if(message.includes("improve")){
return "You can improve soil health by adding compost, crop rotation and proper irrigation.";
}

/* fertilizer */

if(message.includes("fertilizer")){
return "Nitrogen fertilizers improve leaf growth while phosphorus helps root development.";
}

/* irrigation */

if(message.includes("irrigation")){
return "Irrigate early morning or evening to reduce evaporation.";
}

/* rice */

if(message.includes("rice")){
return "Rice grows best in high rainfall areas with slightly acidic soil.";
}

/* maize */

if(message.includes("maize")){
return "Maize grows well in warm climates with moderate rainfall.";
}

/* cotton */

if(message.includes("cotton")){
return "Cotton requires warm temperatures and well drained soil.";
}

/* thanks */

if(message.includes("thanks")){
return "You're welcome! Let me know if you need more farming advice.";
}

/* fallback */

return "I can help with soil pH, crop prediction, weather, profit or irrigation advice.";

}

function Chatbot() {

const [farmData,setFarmData] = useState(null);

useEffect(()=>{
fetch("http://127.0.0.1:8000/data/rest")
.then(res=>res.json())
.then(res=>{
if(res.data){
setFarmData(res.data);
}
})
.catch(err=>console.log("Chatbot data error:",err));
},[]);


const [messages,setMessages] = useState([
{
sender:"bot",
text:"Hello! Ask me about crops, soil, yield or profit.",
time:new Date().toLocaleTimeString()
}
]);

const [input,setInput] = useState("");
const [typing,setTyping] = useState(false);

const messagesEndRef = useRef(null);

useEffect(()=>{
messagesEndRef.current?.scrollIntoView({behavior:"smooth"});
},[messages]);

const sendMessage = () => {

if(!input.trim()) return;

const userMessage = {
sender:"user",
text:input,
time:new Date().toLocaleTimeString()
};

setMessages(prev => [...prev,userMessage]);
setInput("");

setTyping(true);

setTimeout(()=>{

const botReply = {
sender:"bot",
text:getBotResponse(input,farmData),
time:new Date().toLocaleTimeString()
};

setMessages(prev => [...prev,botReply]);
setTyping(false);

},800);

};

const handleKeyPress = (e)=>{
if(e.key==="Enter"){
sendMessage();
}
};

return(

<div className="chat-page">

<div className="chat-card">

<div className="chat-title">
🌱 Agriculture Assistant
</div>

<div className="chat-messages">

{messages.map((msg,index)=>(
<div key={index} className="message-row">

<div className={msg.sender==="bot"?"avatar bot":"avatar user"}>
{msg.sender==="bot"?"🤖":"👨"}
</div>

<div className={msg.sender==="user"?"message user":"message bot"}>

<div>{msg.text}</div>

<span className="time">{msg.time}</span>

</div>

</div>
))}

{typing && <div className="typing">Bot is typing...</div>}

<div ref={messagesEndRef}></div>

</div>

<div className="chat-input-area">

<input
value={input}
onChange={(e)=>setInput(e.target.value)}
onKeyDown={handleKeyPress}
placeholder="Ask about crops, soil, yield..."
/>

<button onClick={sendMessage}>
Send
</button>

</div>

</div>

</div>

);

}

export default Chatbot;