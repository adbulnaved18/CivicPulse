import React, { useEffect, useState } from "react";
import {
  submitComplaint,
  updateComplaintStatus,
  checkDuplicate,
} from "../services/apiClient";

function SubmitComplaint() {
  const [form, setForm] = useState({
    description: "",
    category: "",
    location: "",
    language: "en",
  });

  const [message, setMessage] = useState("");
  const [complaints, setComplaints] = useState([]);
  const [duplicateMatches, setDuplicateMatches] = useState([]);

  useEffect(() => {
    loadComplaints();
  }, []);

  async function loadComplaints() {
    try {
      const response = await fetch(
        "http://127.0.0.1:8000/complaints/"
      );

      if (!response.ok) {
        throw new Error("Failed to load complaints");
      }

      const data = await response.json();

      setComplaints(data);
    } catch (error) {
      console.error("Failed to load complaints:", error);
      setMessage("Failed to load complaints.");
    }
  }

  function handleChange(event) {
    setForm({
      ...form,
      [event.target.name]: event.target.value,
    });
  }

  async function handleSubmit(event) {
    event.preventDefault();

    setMessage("");
    setDuplicateMatches([]);

    try {
      const duplicateResult = await checkDuplicate(
        form.category,
        form.location,
        form.description
      );

      if (duplicateResult.is_duplicate) {
        setDuplicateMatches(
          duplicateResult.matches || []
        );

        setMessage(
          "A similar complaint already exists. Please support the existing complaint instead of creating a duplicate."
        );

        return;
      }

      await submitComplaint(form);

      setMessage("Complaint submitted successfully.");

      setDuplicateMatches([]);

      setForm({
        description: "",
        category: "",
        location: "",
        language: "en",
      });

      await loadComplaints();
    } catch (error) {
      console.error("Failed to submit complaint:", error);

      setMessage("Failed to submit complaint.");
    }
  }

  async function handleVote(complaintId) {
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/complaints/${complaintId}/vote?voter_id=citizen_002`,
        {
          method: "POST",
        }
      );

      const data = await response.json();

      if (!response.ok) {
        setMessage("Failed to support this complaint.");
        return;
      }

      if (
        data.message ===
        "You have already voted for this complaint"
      ) {
        setMessage(
          "You have already supported this complaint."
        );
        return;
      }

      setMessage(
        "Thanks! Your support has been added to this complaint."
      );

      await loadComplaints();
    } catch (error) {
      console.error("Failed to vote:", error);

      setMessage("Failed to support this complaint.");
    }
  }

  async function handleStatusChange(
    complaintId,
    newStatus
  ) {
    try {
      await updateComplaintStatus(
        complaintId,
        newStatus
      );

      setMessage("Complaint status updated successfully.");

      await loadComplaints();
    } catch (error) {
      console.error(
        "Failed to update complaint status:",
        error
      );

      setMessage(
        "Failed to update complaint status."
      );
    }
  }

  function getStatusColor(status) {
    if (status === "Resolved") {
      return "green";
    }

    if (status === "In Progress") {
      return "blue";
    }

    return "orange";
  }

  function getPriorityLabel(priority = 0) {
    if (priority >= 5) {
      return "High";
    }

    if (priority >= 2) {
      return "Medium";
    }

    return "Low";
  }

  function getPriorityColor(priority = 0) {
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
      <h1>Submit a Complaint</h1>

      {/* Complaint Form */}
      <form onSubmit={handleSubmit}>
        <div>
          <label>Description</label>
          <br />

          <textarea
            name="description"
            value={form.description}
            onChange={handleChange}
            placeholder="Describe the issue"
            required
          />
        </div>

        <br />

        <div>
          <label>Category</label>
          <br />

          <input
            name="category"
            value={form.category}
            onChange={handleChange}
            placeholder="Electrical"
            required
          />
        </div>

        <br />

        <div>
          <label>Location</label>
          <br />

          <input
            name="location"
            value={form.location}
            onChange={handleChange}
            placeholder="Gate 2, Main Road"
            required
          />
        </div>

        <br />

        <div>
          <label>Language</label>
          <br />

          <select
            name="language"
            value={form.language}
            onChange={handleChange}
          >
            <option value="en">English</option>
            <option value="hi">Hindi</option>
          </select>
        </div>

        <br />

        <button type="submit">
          Submit Complaint
        </button>
      </form>

      {/* General Message */}
      {message && <p>{message}</p>}

      {/* Duplicate Complaints */}
      {duplicateMatches.length > 0 && (
        <div>
          <h3>Existing Similar Complaints</h3>

          {duplicateMatches.map((complaint) => (
            <div
              key={complaint.id}
              style={{
                border: "1px solid #ccc",
                padding: "15px",
                marginBottom: "10px",
                borderRadius: "8px",
              }}
            >
              <p>
                <strong>ID:</strong> {complaint.id}
              </p>

              <p>
                <strong>Description:</strong>{" "}
                {complaint.description}
              </p>

              <p>
                <strong>Category:</strong>{" "}
                {complaint.category}
              </p>

              <p>
                <strong>Location:</strong>{" "}
                {complaint.location}
              </p>

              <p>
                <strong>Status:</strong>{" "}
                <span
                  style={{
                    fontWeight: "bold",
                    color: getStatusColor(
                      complaint.status
                    ),
                  }}
                >
                  {complaint.status}
                </span>
              </p>

              <p>
                <strong>Votes:</strong>{" "}
                {complaint.votes ?? 0}
              </p>

              {complaint.similarity !== undefined && (
                <p>
                  <strong>Similarity:</strong>{" "}
                  {complaint.similarity}
                </p>
              )}

              <button
                type="button"
                onClick={() =>
                  handleVote(complaint.id)
                }
              >
                +1 Support this issue
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Submitted Complaints */}
      <h2>Submitted Complaints</h2>

      {complaints.length === 0 ? (
        <p>No complaints submitted yet.</p>
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
              <strong>Description:</strong>{" "}
              {complaint.description}
            </p>

            <p>
              <strong>Category:</strong>{" "}
              {complaint.category}
            </p>

            <p>
              <strong>Location:</strong>{" "}
              {complaint.location}
            </p>

            <p>
              <strong>Language:</strong>{" "}
              {complaint.language}
            </p>

            {/* Status */}
            <p>
              <strong>Status:</strong>{" "}
              <span
                style={{
                  fontWeight: "bold",
                  color: getStatusColor(
                    complaint.status
                  ),
                }}
              >
                {complaint.status}
              </span>
            </p>

            {/* Votes */}
            <p>
              <strong>Votes:</strong>{" "}
              {complaint.votes ?? 0}
            </p>

            {/* Priority */}
            <p>
              <strong>Priority:</strong>{" "}
              <span
                style={{
                  fontWeight: "bold",
                  color: getPriorityColor(
                    complaint.priority ?? 0
                  ),
                }}
              >
                {getPriorityLabel(
                  complaint.priority ?? 0
                )}
              </span>{" "}
              ({complaint.priority ?? 0})
            </p>

            {/* Vote Button */}
            <button
              type="button"
              onClick={() =>
                handleVote(complaint.id)
              }
            >
              +1 Support this issue
            </button>

            {" "}

            {/* Status Dropdown */}
            <select
              value={complaint.status}
              onChange={(event) =>
                handleStatusChange(
                  complaint.id,
                  event.target.value
                )
              }
            >
              <option value="Pending">
                Pending
              </option>

              <option value="In Progress">
                In Progress
              </option>

              <option value="Resolved">
                Resolved
              </option>
            </select>
          </div>
        ))
      )}
    </div>
  );
}

export default SubmitComplaint;