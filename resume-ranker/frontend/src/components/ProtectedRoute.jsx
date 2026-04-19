import { Navigate } from "react-router-dom"

export default function ProtectedRoute({ children }) {

  const role = localStorage.getItem("user_role")

  let email = null

  if(role === "candidate"){
    email = localStorage.getItem("candidate_email")
  }

  if(role === "recruiter"){
    email = localStorage.getItem("recruiter_email")
  }


  if (!email) {
    return <Navigate to="/login" />
  }

  return children
}