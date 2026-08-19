const API_URL = "http://127.0.0.1:8000";

export async function submitComplaint(complaint) {
  const response = await fetch(`${API_URL}/complaints/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(complaint),
  });

  if (!response.ok) {
    throw new Error("Failed to submit complaint");
  }

  return response.json();
}

export async function getComplaints() {
  const response = await fetch(`${API_URL}/complaints/`);

  if (!response.ok) {
    throw new Error("Failed to fetch complaints");
  }

  return response.json();
}
export async function updateComplaintStatus(id, status) {
  const response = await fetch(
    `http://127.0.0.1:8000/complaints/${id}/status?status=${encodeURIComponent(status)}`,
    {
      method: "PATCH",
    }
  );

  if (!response.ok) {
    throw new Error("Failed to update complaint status");
  }

  return response.json();
}
export async function checkDuplicate(category, location, description) {
  const params = new URLSearchParams({
    category,
    location,
    description,
  });

  const response = await fetch(
    `http://127.0.0.1:8000/complaints/check-duplicate?${params.toString()}`
  );

  if (!response.ok) {
    throw new Error("Failed to check duplicate complaint");
  }

  return response.json();
}