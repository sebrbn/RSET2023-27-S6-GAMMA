import { useNavigate } from "react-router-dom";

export default function Dashboard(){

const email = localStorage.getItem("candidate_email")
const navigate = useNavigate()

return(

<div className="p-8 bg-gray-50 min-h-screen">

<h1 className="text-3xl font-bold text-gray-800 mb-2">
Welcome to Candidate Portal
</h1>

<p className="text-gray-500 mb-8">
Manage your resumes and track your job applications easily.
</p>


<div className="grid grid-cols-1 md:grid-cols-2 gap-6">

{/* Browse Jobs */}
<div className="bg-white shadow-md rounded-xl p-6 hover:shadow-lg transition">

<h3 className="text-xl font-semibold text-gray-700 mb-2">
Browse Jobs
</h3>

<p className="text-gray-500 text-sm">
Explore available job openings that match your skills.
</p>

<button
onClick={()=>navigate("/candidate/jobs")}
className="mt-4 bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition"
>
Browse Jobs
</button>

</div>



{/* My Applications */}
<div className="bg-white shadow-md rounded-xl p-6 hover:shadow-lg transition">

<h3 className="text-xl font-semibold text-gray-700 mb-2">
My Applications
</h3>

<p className="text-gray-500 text-sm">
Track and manage the jobs you have applied for.
</p>

<button
onClick={()=>navigate("/candidate/applications")}
className="mt-4 bg-purple-500 hover:bg-purple-600 text-white px-4 py-2 rounded-lg transition"
>
View Applications
</button>

</div>

</div>

</div>

)
}