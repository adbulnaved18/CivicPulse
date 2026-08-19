import "./App.css";
import React from "react";
import ReactDOM from "react-dom/client";
import SubmitComplaint from "./pages/SubmitComplaint";
import AdminDashboard from "./pages/AdminDashboard";

function App() {
  const isAdmin = window.location.pathname === "/admin";

  return isAdmin ? <AdminDashboard /> : <SubmitComplaint />;
}

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);