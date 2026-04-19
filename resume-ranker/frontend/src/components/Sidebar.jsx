import { Link, useNavigate } from "react-router-dom"

export default function Sidebar({ role }) {

  const navigate = useNavigate()

  const logout = () => {
    localStorage.removeItem("candidate_email")
    navigate("/login")
  }

  const email = localStorage.getItem("candidate_email")

  

  return(

  <div className="w-64 bg-gray-900 text-white min-h-screen p-6">

  <h2 className="text-2xl font-bold mb-6">
  AI Resume Ranker
  </h2>

  <p className="text-sm text-gray-300">
  Logged in as:
  </p>

  <p className="mb-8 text-gray-200 break-words">
  {email}
  </p>
  
  <button
            onClick={logout}
            style={{
              marginTop:"20px",
              background:"#ef4444",
              color:"white",
              border:"none",
              padding:"8px",
              cursor:"pointer"
            }}
          >
            Logout
          </button>


  </div>

  )
  }


