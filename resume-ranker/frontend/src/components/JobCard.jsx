import { useNavigate } from "react-router-dom";

export default function JobCard({ job }) {

  const navigate = useNavigate();

  return (
    <div className="bg-white p-6 rounded-xl shadow hover:shadow-lg transition">

      <h2 className="text-xl font-bold mb-2">
        {job.title}
      </h2>

      <p className="text-gray-500 mb-2">
        {job.department}
      </p>

      <p className="text-sm text-gray-600 mb-4">
        {job.description}
      </p>

      <button
        onClick={() => navigate(`/candidate/jobs/${job.id}`)}
        className="bg-indigo-600 text-white px-4 py-2 rounded"
      >
        View Details
      </button>
    </div>
  );
}