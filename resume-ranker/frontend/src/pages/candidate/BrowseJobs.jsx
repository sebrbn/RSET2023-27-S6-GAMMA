

import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../services/api";

export default function BrowseJobs() {

  const [jobs, setJobs] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    fetchJobs();
  }, []);

  const fetchJobs = async () => {
    try {
      const res = await api.get("/openings/all");
      console.log("Jobs:", res.data); // debug
      setJobs(res.data);
    } catch (err) {
      console.error("Error fetching jobs:", err);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-100 via-blue-100 to-purple-100 p-10">
      <h1 className="text-3xl font-bold mb-6">
        Browse Jobs
      </h1>

      {jobs.length === 0 ? (
        <p>No jobs available</p>
      ) : (
        jobs.map((job) => (
          <div
            key={job.id}
            className="bg-white rounded-xl shadow-lg p-6 mb-6 hover:shadow-2xl transition transform hover:-translate-y-1"
          >
            <h2 className="text-2xl font-bold text-indigo-700 mb-2">
            {job.title}
            </h2>



            <p className="text-gray-500 italic mb-2">
              {job.department}
            </p>

            <p className="text-gray-700 mb-3">
              {job.description}
            </p>

            <p className="font-medium text-gray-800">
             <b>Experience Required:</b> {job.experience_required} years
            </p>

            <p className="mt-2 font-medium">
             <b>Skills Required:</b> {job.required_skills.join(",")}
            </p>

            <button
              onClick={() => navigate(`/candidate/jobs/${job.id}`)}
              className="mt-4 bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition"
            >
              View Details
            </button>
          </div>
        ))
      )}
    </div>
  );
}
