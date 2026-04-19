import { useEffect, useState } from "react"
import api from "../../services/api"

export default function Applications(){

  const [applications,setApplications] = useState([])

  const fetchApplications = async () => {

    const email = localStorage.getItem("candidate_email")

    const res = await api.get(`/applications/candidate/${email}`)

    console.log(res.data)

    setApplications(res.data)

  }

  useEffect(()=>{
    fetchApplications()
  },[])

  return(

    <div className="min-h-screen bg-gradient-to-br from-indigo-100 via-purple-100 to-blue-100 p-10">

      <h1 className="text-4xl font-bold text-indigo-700 mb-10">
        My Applications
      </h1>

      <div className="mt-6 space-y-4">

        {applications.length === 0 && (
          <p>No applications found</p>
        )}

        {applications.map((app, index) => (

          <div key={index} className="bg-white shadow-xl rounded-xl p-6 mb-6 hover:shadow-2xl transition transform hover:-translate-y-1">

            <p className="text-2xl font-semibold text-indigo-600 mb-2"><strong>Job:</strong> {app.job_title}</p>

            <p className="text-gray-500 italic mb-2"><strong>Department:</strong> {app.department}</p>

            <span
                  className={
                  `px-3 py-1 rounded-full text-white text-sm font-semibold ${
                  app.status === "accepted"
                  ? "bg-green-500"
                  : app.status === "rejected"
                  ? "bg-red-500"
                  : "bg-yellow-500"
                  }`
                  }
                  >
                  {app.status}
                  </span>

            <p className="mt-3 font-medium">
                          Skill Match: <span className="text-indigo-600">{app.skill_match}%</span>
            </p>


            <p className="font-medium">
            Experience Match: <span className="text-indigo-600">{app.experience_match}%</span>
            </p>

            <p className="mt-3 font-medium text-red-500"><strong>Missing Skills:</strong> {app.missing_skills}</p>

            {app.score && (
              <p  className="mt-2 font-semibold text-lg text-purple-700"><strong>Rank Score:</strong> {app.score}</p>
            )}
            
            {app.llm_feedback && (

            <div className="mt-6 bg-indigo-50 border-l-4 border-indigo-500 p-4 rounded">

            <h4 className="text-lg font-semibold text-indigo-700 mb-2">
            🤖 AI Resume Advice
            </h4>

            <p className="text-gray-700 leading-relaxed">
            {app.llm_feedback}
            </p>

            </div>

            )}

          </div>

        ))}

      </div>


    </div>

  )

}