import { useParams, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import api from "../../services/api";

export default function JobDetails() {

  const { id } = useParams();
  const navigate = useNavigate();

  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {

    const fetchJob = async () => {
      try {

        const res = await api.get(`/openings/${id}`);

        console.log("Job:", res.data);

        setJob(res.data);

      } catch (err) {

        console.error("Error fetching job:", err);

      } finally {
        setLoading(false);
      }
    };

    fetchJob();

  }, [id]);

  if (loading) {
    return <p>Loading...</p>;
  }

  if (!job) {
    return <p>Job not found</p>;
  }

  return (

    <div className="min-h-screen bg-gradient-to-br from-indigo-100 via-purple-100 to-blue-100 flex justify-center items-center">
    
    <div className="bg-white shadow-2xl rounded-xl p-10 w-[600px]">
    
    <h1 className="text-4xl font-bold text-indigo-700 mb-4">
    {job.title}
    </h1>
    
    <p className="text-gray-500 text-lg mb-2">
    Department: {job.department}
    </p>
    
    <hr className="my-4"/>
    
    <p className="text-gray-700 mb-6 leading-relaxed">
    {job.description}
    </p>
    
    <button
    onClick={()=>navigate(`/candidate/apply/${job.id}`)}
    className="bg-green-500 hover:bg-green-600 text-white px-8 py-3 rounded-lg text-lg transition"
    >
    Apply Now
    </button>
    
    </div>
    
    </div>
    
    );
}