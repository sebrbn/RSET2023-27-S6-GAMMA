import React, { useState } from "react";
import Sidebar from "./components/Sidebar";
import Header from "./components/Header";
import Dashboard from "./components/Dashboard";
import Recommendation from "./components/Recommendation";
import Crop from "./components/Crop";
import Chatbot from "./components/Chatbot";
import "./App.css";
import Profit from "./components/Profit";
import Charts from "./components/Charts";

function App() {

  const [page, setPage] = useState("dashboard");

  const renderPage = () => {
  switch(page){

    case "dashboard":
      return <Dashboard setPage={setPage}/>

    case "recommendation":
      return <Recommendation setPage={setPage}/>

     case "prediction":
      return <Crop setPage={setPage}/>


    case "profit":
      return <Profit/>

    case "chatbot":
      return <Chatbot/>

    default:
      return <Dashboard setPage={setPage}/>

  }
};

  return (
    <div className="app">

      <Sidebar setPage={setPage} />

      <div className="main">

        <Header />

        <div className="content">
          {renderPage()}
        </div>

      </div>

    </div>
  );
}

export default App;