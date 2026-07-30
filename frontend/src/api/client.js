import axios from "axios";

export const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

const client = axios.create({ baseURL: `${API_BASE}/api` });

// Score pasted resume text against a JD.
export const analyzeText = (payload) => client.post("/analyze", payload).then((r) => r.data);

// Upload PDF/DOCX/TXT resume files, scan + score them.
export const analyzeUpload = (formData) =>
  client.post("/upload-analyze", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  }).then((r) => r.data);

// Company skill profile CRUD (customization).
export const listProfiles = () => client.get("/skill-profiles").then((r) => r.data);
export const createProfile = (payload) => client.post("/skill-profiles", payload).then((r) => r.data);
export const updateProfile = (id, payload) => client.put(`/skill-profiles/${id}`, payload).then((r) => r.data);
export const deleteProfile = (id) => client.delete(`/skill-profiles/${id}`).then((r) => r.data);

// History.
export const listHistory = () => client.get("/history").then((r) => r.data);
export const getHistoryRun = (id) => client.get(`/history/${id}`).then((r) => r.data);

export default client;
