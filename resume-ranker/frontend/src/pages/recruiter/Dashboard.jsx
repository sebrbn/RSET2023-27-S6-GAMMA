import { Link,useNavigate } from "react-router-dom"

export default function Dashboard(){

const navigate = useNavigate()

return(

    <div className="min-h-screen bg-gradient-to-br from-indigo-100 via-purple-100 to-blue-100 p-10">
    
    <h1 className="text-4xl font-bold text-indigo-700 mb-10">
    Recruiter Dashboard
    </h1>
    
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
    
    {/* Manage Jobs Card */}
    <div
    className="bg-white rounded-xl shadow-lg p-8 hover:shadow-2xl transition cursor-pointer"
    onClick={()=>navigate("/recruiter/jobs")}
    >
    <h2 className="text-xl font-semibold text-indigo-600 mb-2">
    📂 Manage Job Openings
    </h2>
    
    <p className="text-gray-500">
    View and manage all job postings
    </p>
    </div>
    
    
    {/* Create Job Card */}
    <div
    className="bg-white rounded-xl shadow-lg p-8 hover:shadow-2xl transition cursor-pointer"
    onClick={()=>navigate("/recruiter/create-job")}
    >
    <h2 className="text-xl font-semibold text-green-600 mb-2">
    ➕ Create Job Opening
    </h2>
    
    <p className="text-gray-500">
    Add a new job role for candidates
    </p>
    </div>
    
    
    {/* Logout Card */}
    <div
    className="bg-white rounded-xl shadow-lg p-8 hover:shadow-2xl transition cursor-pointer"
    onClick={()=>{
    localStorage.clear()
    navigate("/login")
    }}
    >
    <h2 className="text-xl font-semibold text-red-600 mb-2">
    🚪 Logout
    </h2>
    
    <p className="text-gray-500">
    Sign out of recruiter account
    </p>
    </div>
    
    </div>
    
    </div>
    
    )
}