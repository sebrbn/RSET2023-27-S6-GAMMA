import { useState } from "react"
import api from "../../services/api"

export default function CreateJob(){

  const [title,setTitle] = useState("")
  const [department,setDepartment] = useState("")
  const [description,setDescription] = useState("")
  const [skills,setSkills] = useState("")
  const [experience,setExperience] = useState("")

  const email = localStorage.getItem("recruiter_email")

  const createJob = async () => {

    try {
  
      await api.post(
        "/openings/add",
        {
          title: title,
          department: department,
          description: description,
          required_skills: skills.split(","),
          experience_required: parseInt(experience),
          recruiter_email: email
        },
        {
          headers: {
            "Content-Type": "application/json"
          }
        }
      )
  
      alert("Job Created Successfully")
  
      navigate("/recruiter/jobs")
  
    } catch (err) {
  
      console.error(err)
      alert("Error creating job")
  
    }
  
  }
  return(

    <div className="flex justify-center items-center min-h-screen">

    <div className="bg-white p-8 rounded-xl shadow-xl w-[420px]">

      <h2 className="text-3xl font-bold text-purple-700 mb-6">
      Create Job Opening
      </h2>

      <input placeholder="Title" onChange={(e)=>setTitle(e.target.value)} />
      <br/><br/>

      <input placeholder="Department" onChange={(e)=>setDepartment(e.target.value)} />
      <br/><br/>

      <textarea placeholder="Description" onChange={(e)=>setDescription(e.target.value)} />
      <br/><br/>

      <input placeholder="Skills (comma separated)" onChange={(e)=>setSkills(e.target.value)} />
      <br/><br/>

      <input placeholder="Experience Required" onChange={(e)=>setExperience(e.target.value)} />
      <br/><br/>

      <button className="bg-purple-600 text-white px-4 py-2 rounded-lg w-full hover:bg-purple-700 transition" onClick={createJob}>
        Create Job
      </button>

    </div>

    </div>

  )

}
