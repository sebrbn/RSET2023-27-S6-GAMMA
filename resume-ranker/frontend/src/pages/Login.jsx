import { useState } from "react"
import { useNavigate, Link } from "react-router-dom"
import api from "../services/api"

export default function Login(){

  const [email,setEmail] = useState("")
  const [password,setPassword] = useState("")

  const navigate = useNavigate()

  const login = async () => {

    if(!email || !password){
      alert("Fill all fields")
      return
    }

    try{

      const res = await api.post("/auth/login", {email: email, password: password})

      console.log(res.data)

      const role = res.data.role

      // Save logged in user
      localStorage.setItem(role + "_email", email)
      localStorage.setItem("user_role", role)

      // Redirect based on role
      if(role === "candidate"){
        navigate("/candidate/dashboard")
      }

      if(role === "recruiter"){
        navigate("/recruiter/dashboard")
      }

    }catch(err){

      alert("Invalid credentials")

    }

  }

  return(

    <div className="min-h-screen bg-gradient-to-br from-indigo-200 via-purple-200 to-blue-200 flex items-center justify-center">

    <div className="bg-white shadow-2xl rounded-xl p-10 w-[420px]">

    <h2 className="text-3xl font-bold text-indigo-700 text-center mb-6">
    Login
    </h2>

    <input
    placeholder="Email"
    onChange={(e)=>setEmail(e.target.value)}
    className="border p-3 rounded-lg w-full mb-4"
    />

    <input
    type="password"
    placeholder="Password"
    onChange={(e)=>setPassword(e.target.value)}
    className="border p-3 rounded-lg w-full mb-6"
    />

    <button
    onClick={login}
    className="bg-indigo-600 hover:bg-indigo-700 text-white w-full py-3 rounded-lg transition"
    >
    Login
    </button>

    <p className="text-center text-gray-600 mt-6">
    New user? 
    <Link
    to="/register"
    className="text-indigo-600 font-semibold ml-1"
    >
    Register
    </Link>
    </p>

    </div>

    </div>

  )

}
