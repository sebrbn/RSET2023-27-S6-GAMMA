import { useEffect,useState } from "react"
import { useParams } from "react-router-dom"
import api from "../../services/api"

export default function JobApplicants(){

const {id} = useParams()

const [candidates,setCandidates] = useState([])

const [selected,setSelected] = useState(null)

useEffect(()=>{

loadRanking()

},[])

const loadRanking = async()=>{

const res = await api.get(`/ranking/opening/${id}`)

console.log("Ranking Data:", res.data)

setCandidates(res.data)

}

/* ADDED FUNCTION */
const updateStatus = async (appId,status)=>{

await api.put(`/recruiter/update_status/${appId}?status=${status}`)

alert("Status updated")

loadRanking()

}

return(

<div className="p-10">

<h2 className="text-4xl font-bold text-indigo-700 mb-6">
Applicants for Job {id}
</h2>


<hr/>

{candidates.map((c,index)=>(

<div
key={c.id}
className="bg-white rounded-xl shadow-lg p-6 mb-6 border border-gray-200 hover:shadow-2xl transition"
>


<b>Rank #{c.rank}</b>

<br/>

Candidate: {c.email}

<br/>

Score: {c.score}

<br/>

Skill Match: {c.skill_match} %

<br/>

Experience Match: {c.experience_match} %

<br/><br/>

<b>Missing Skills:</b>

<br/>

{c.missing_skills}

<br/><br/>

<button
className="bg-blue-500 text-white px-3 py-1 rounded-lg hover:bg-blue-600 transition"
onClick={()=>setSelected(c)}
>
Explain Match
</button>

&nbsp;

<button
className="bg-gray-500 text-white px-3 py-1 rounded-lg hover:bg-gray-600 transition"
onClick={()=>window.open(`http://localhost:8000/resumes/view/${c.email}`)}
>
View Resume
</button>


&nbsp;

<button
className="bg-green-500 text-white px-3 py-1 rounded-lg hover:bg-green-600 transition"
onClick={() => updateStatus(c.id, "accepted")}
>
Accept
</button>

<button
className="bg-red-500 text-white px-3 py-1 rounded-lg hover:bg-red-600 transition"
onClick={() => updateStatus(c.id, "rejected")}
>
Reject
</button>

</div>

))}

{selected && (

<div className="bg-indigo-50 border-l-4 border-indigo-500 p-6 rounded-lg mt-10 shadow">


<h3 className="text-2xl font-bold text-indigo-700 mb-4">
🤖 AI Explanation
</h3>

<pre>
{selected.rag_explanation}
</pre>

</div>

)}

</div>

)

}