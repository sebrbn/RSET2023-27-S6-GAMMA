import { useEffect,useState } from "react"
import { useNavigate } from "react-router-dom"
import api from "../../services/api"

export default function Jobs(){

const [jobs,setJobs] = useState([])

const navigate = useNavigate()

useEffect(()=>{

loadJobs()

},[])

const loadJobs = async()=>{

const email = localStorage.getItem("recruiter_email")    

const res = await api.get(`/recruiter/jobs/${email}`)

setJobs(res.data)

}

return(

    <div className="min-h-screen bg-gradient-to-br from-indigo-100 via-purple-100 to-blue-100 p-10">
    
    <h2 className="text-4xl font-bold text-indigo-700 mb-10">
    Job Openings
    </h2>
    
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    
    {jobs && jobs.map(job=>(
    
    <div
    key={job.id}
    className="bg-white shadow-xl rounded-xl p-6 hover:shadow-2xl transition transform hover:-translate-y-1"
    >
    
    <h3 className="text-2xl font-semibold text-indigo-600 mb-2">
    {job.title}
    </h3>
    
    <p className="text-gray-500 mb-1">
    Department: {job.department}
    </p>
    
    <p className="text-gray-400 mb-4">
    Job ID: {job.id}
    </p>
    
    <button
    onClick={()=>navigate(`/recruiter/job/${job.id}`)}
    className="bg-indigo-600 text-white px-5 py-2 rounded-lg hover:bg-indigo-700 transition"
    >
    View Applicants
    </button>
    
    </div>
    
    ))}
    
    </div>
    
    </div>
    
    )

}