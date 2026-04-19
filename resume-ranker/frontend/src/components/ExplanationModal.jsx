export default function ExplanationModal({ explanation }) {

  if (!explanation) return null;

  return (
    <div className="bg-white mt-6 p-6 rounded-xl shadow">

      <h3 className="font-bold mb-4">
        AI Explanation
      </h3>

      <pre className="whitespace-pre-wrap text-sm text-gray-700">
        {explanation}
      </pre>

    </div>
  );
}