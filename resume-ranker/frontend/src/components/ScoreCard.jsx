export default function ScoreCard({ result }) {

  return (

    <div className="bg-white mt-8 p-6 rounded-xl shadow">

      <h2 className="text-xl font-bold mb-4">
        Score: {result.score}%
      </h2>

      <p className="text-green-600">
        Skill Match: {result.skill_match}%
      </p>

      <p className="text-blue-600">
        Experience Match: {result.experience_match}%
      </p>

      <p className="text-red-600 mt-4">
        Missing Skills: {result.missing_skills}
      </p>

      {/* NEW SECTION FOR AI FEEDBACK */}

      {result.llm_feedback && (

        <div className="mt-6 p-4 bg-gray-100 rounded-lg">

          <h3 className="font-bold mb-2">
            AI Resume Advice
          </h3>

          <p className="text-gray-700">
            {result.llm_feedback}
          </p>

        </div>

      )}

    </div>

  )

}
