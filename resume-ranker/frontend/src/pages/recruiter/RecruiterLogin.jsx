import { useState } from "react"
import { useNavigate } from "react-router-dom"

export default function RecruiterLogin(){

  const [email,setEmail] = useState("")
  const [password,setPassword] = useState("")
  const navigate = useNavigate()

  const login = async () => {

    const res = await fetch("http://localhost:8000/auth/login",{
      method:"POST",
      headers:{
        "Content-Type":"application/json"
      },
      body:JSON.stringify({
        email,
        password
      })
    })

    const data = await res.json()

    if(data.role === "recruiter"){
      localStorage.setItem("recruiter",email)
      navigate("/recruiter/dashboard")
    }else{
      alert("Not a recruiter account")
    }

  }

  return(

    <div style={{padding:40}}>

      <h2>Recruiter Login</h2>

      <input
        placeholder="Email"
        onChange={(e)=>setEmail(e.target.value)}
      />

      <br/><br/>

      <input
        type="password"
        placeholder="Password"
        onChange={(e)=>setPassword(e.target.value)}
      />

      <br/><br/>

      <button onClick={login}>
        Login
      </button>

    </div>

  )

}