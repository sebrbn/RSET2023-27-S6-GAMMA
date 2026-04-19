import { useState } from "react"
import { useParams } from "react-router-dom"
import api from "../../services/api"

export default function UploadResume(){

  const { id } = useParams()

  const [file,setFile] = useState(null)

  const email = localStorage.getItem("candidate_email")

  const upload = async () => {

    if(!file){
      alert("Select resume")
      return
    }

    const formData = new FormData()

    formData.append("file",file)
    formData.append("email",email)
    formData.append("opening_id",id)

    try{

      const res = await api.post("/resumes/upload", formData)

      alert("Resume uploaded successfully")

      console.log(res.data)

    }catch(err){

      console.log(err)

      alert("Upload failed")

    }

  }

  return(

    <div className="min-h-screen bg-gradient-to-br from-indigo-100 via-purple-100 to-blue-100 flex justify-center items-center">
    
    <div className="bg-white shadow-2xl rounded-xl p-10 w-[500px]">
    
    <h1 className="text-3xl font-bold text-indigo-700 mb-6">
    Upload Resume
    </h1>
    
    <input
    type="file"
    onChange={(e)=>setFile(e.target.files[0])}
    className="border p-3 rounded-lg w-full mb-4"
    />
    
    <p className="text-gray-600 mb-6">
    Applying as: <span className="font-semibold">{email}</span>
    </p>
    
    <button
    onClick={upload}
    className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg transition"
    >
    Submit
    </button>
    
    </div>
    
    </div>
    
    )

}