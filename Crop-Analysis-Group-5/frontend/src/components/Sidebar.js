import React from "react";

function Sidebar({ setPage }) {
  return (
    <div className="sidebar">
      <nav>

        <button onClick={() => setPage("dashboard")}>
          Dashboard
        </button>

        <button onClick={() => setPage("prediction")}>
          Crop Prediction
        </button>

        <button onClick={() => setPage("recommendation")}>
          Crop Recommendation
        </button>

        <button onClick={() => setPage("profit")}>
          Profit Analysis
        </button>

        <button onClick={() => setPage("chatbot")}>
          Chat Service
        </button>

      </nav>
    </div>
  );
}

export default Sidebar;