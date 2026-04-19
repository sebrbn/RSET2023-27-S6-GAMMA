import Sidebar from "../components/Sidebar"

export default function CandidateLayout({ children }) {

  return (

    <div style={{display:"flex"}}>

      <Sidebar role="candidate" />

      <div style={{
        flex:1,
        padding:"40px"
      }}>

        {children}

      </div>

    </div>

  )

}