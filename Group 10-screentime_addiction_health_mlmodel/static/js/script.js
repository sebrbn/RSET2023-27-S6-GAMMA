function validateForm(){

let phone=document.querySelector("input[name='phone']").value;

if(phone.length!=10){

alert("Phone number must be 10 digits");

return false;

}

return true;

}



function sendMessage(){

let input=document.getElementById("userInput").value;

let chat=document.getElementById("chatbox");

chat.innerHTML+= "<p><b>You:</b> "+input+"</p>";

fetch("/chat",{

method:"POST",

headers:{

"Content-Type":"application/json"

},

body:JSON.stringify({message:input})

})

.then(res=>res.json())

.then(data=>{

chat.innerHTML+= "<p><b>AI:</b> "+data.reply+"</p>";

})

}