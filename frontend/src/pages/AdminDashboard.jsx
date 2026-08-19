import React, { useEffect, useState } from "react";
import { updateComplaintStatus } from "../services/apiClient";

function AdminDashboard() {
  const [complaints, setComplaints] = useState([]);

  useEffect(() => {
    loadComplaints();
  }, []);

  async function loadComplaints() {
    try {
      const response = await fetch("http://127.0.0.1:8000/complaints/");
      const data = await response.json();

      // Highest priority complaints appear first
      data.sort((a, b) => b.priority - a.priority);

      setComplaints(data);
    } catch (error) {
      console.error("Failed to load complaints:", error);
    }
  }

  async function handleStatusChange(complaintId, newStatus) {
    try {
      await updateComplaintStatus(complaintId, newStatus);
      await loadComplaints();
    } catch (error) {
      console.error("Failed to update complaint status:", error);
    }
  }

  const totalComplaints = complaints.length;

  const pendingComplaints = complaints.filter(
    (complaint) => complaint.status === "Pending"
  ).length;

  const inProgressComplaints = complaints.filter(
    (complaint) => complaint.status === "In Progress"
  ).length;

  const resolvedComplaints = complaints.filter(
    (complaint) => complaint.status === "Resolved"
  ).length;

  const highPriorityComplaints = complaints.filter(
    (complaint) => complaint.priority >= 5
  ).length;

  function getPriorityLabel(priority) {
    if (priority >= 5) {
      return "High";
    }

    if (priority >= 2) {
      return "Medium";
    }

    return "Low";
  }

  function getPriorityColor(priority) {
    if (priority >= 5) {
      return "red";
    }

    if (priority >= 2) {
      return "orange";
    }

    return "green";
  }

  return (
    <div>
      <h1>Admin Dashboard</h1>

      <p>Manage and prioritize civic complaints.</p>

      {/* Dashboard Summary */}
      <div
        style={{
          display: "flex",
          gap: "15px",
          flexWrap: "wrap",
          marginBottom: "25px",
        }}
      >
        <div
          style={{
            border: "1px solid #ccc",
            padding: "15px",
            borderRadius: "8px",
            minWidth: "130px",
          }}
        >
          <strong>Total</strong>
          <h2>{totalComplaints}</h2>
        </div>

        <div
          style={{
            border: "1px solid #ccc",
            padding: "15px",
            borderRadius: "8px",
            minWidth: "130px",
          }}
        >
          <strong>Pending</strong>
          <h2>{pendingComplaints}</h2>
        </div>

        <div
          style={{
            border: "1px solid #ccc",
            padding: "15px",
            borderRadius: "8px",
            minWidth: "130px",
          }}
        >
          <strong>In Progress</strong>
          <h2>{inProgressComplaints}</h2>
        </div>

        <div
          style={{
            border: "1px solid #ccc",
            padding: "15px",
            borderRadius: "8px",
            minWidth: "130px",
          }}
        >
          <strong>Resolved</strong>
          <h2>{resolvedComplaints}</h2>
        </div>

        <div
          style={{
            border: "1px solid #ccc",
            padding: "15px",
            borderRadius: "8px",
            minWidth: "130px",
          }}
        >
          <strong>High Priority</strong>
          <h2>{highPriorityComplaints}</h2>
        </div>
      </div>

      <h2>Complaints</h2>

      {complaints.length === 0 ? (
        <p>No complaints available.</p>
      ) : (
        complaints.map((complaint) => (
          <div
            key={complaint.id}
            style={{
              border:
                complaint.priority >= 5
                  ? "2px solid red"
                  : "1px solid #ccc",
              padding: "15px",
              marginBottom: "10px",
              borderRadius: "8px",
            }}
          >
            <p>
              <strong>ID:</strong> {complaint.id}
            </p>

            <p>
              <strong>Description:</strong> {complaint.description}
            </p>

            <p>
              <strong>Category:</strong> {complaint.category}
            </p>

            <p>
              <strong>Location:</strong> {complaint.location}
            </p>

            <p>
              <strong>Votes:</strong> {complaint.votes}
            </p>

            <p>
              <strong>Priority:</strong>{" "}
              <span
                style={{
                  fontWeight: "bold",
                  color: getPriorityColor(complaint.priority),
                }}
              >
                {getPriorityLabel(complaint.priority)}
              </span>{" "}
              ({complaint.priority})
            </p>

            <p>
              <strong>Status:</strong> {complaint.status}
            </p>

            <select
              value={complaint.status}
              onChange={(event) =>
                handleStatusChange(
                  complaint.id,
                  event.target.value
                )
              }
            >
              <option value="Pending">Pending</option>
              <option value="In Progress">In Progress</option>
              <option value="Resolved">Resolved</option>
            </select>
          </div>
        ))
      )}
    </div>
  );
}

export default AdminDashboard;