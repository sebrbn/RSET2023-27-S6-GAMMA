import { useState } from "react"
import { useNavigate } from "react-router-dom"
import api from "../services/api"

export default function Register(){

  const [email,setEmail] = useState("")
  const [password,setPassword] = useState("")
  const [role,setRole] = useState("candidate")

  const navigate = useNavigate()

  const register = async () => {

    if(!email || !password){
      alert("Fill all fields")
      return
    }

    try{

      await api.post("/auth/signup", {email, password , role})
      alert("Registration Successful")

      navigate("/login")

    }catch(err){

      alert(err.response?.data?.detail || "Registration failed")

    }

  }

  return(

    <div className="min-h-screen bg-gradient-to-br from-indigo-200 via-purple-200 to-blue-200 flex items-center justify-center">

    <div className="bg-white shadow-2xl rounded-xl p-10 w-[420px]">

    <h2 className="text-3xl font-bold text-indigo-700 text-center mb-6">
    Register
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
    className="border p-3 rounded-lg w-full mb-4"
    />

    <select
    onChange={(e)=>setRole(e.target.value)}
    className="border p-3 rounded-lg w-full mb-6"
    >

    <option value="candidate">Candidate</option>
    <option value="recruiter">Recruiter</option>

    </select>

    <button
    onClick={register}
    className="bg-indigo-600 hover:bg-indigo-700 text-white w-full py-3 rounded-lg transition"
    >
    Register
    </button>

    </div>

    </div>

  )

}

