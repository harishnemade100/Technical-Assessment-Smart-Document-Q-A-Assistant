import axios from 'axios'

export const API_BASE_URL = "http://127.0.0.1:8000/api";

// Upload document
export async function uploadDocument(file: File) {
  const formData = new FormData()
  formData.append('file', file)
  const res = await axios.post(`${API_BASE_URL}/documents/upload`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return res.data
}

// Get all uploaded documents
export async function getDocuments() {
  const res = await axios.get(`${API_BASE_URL}/documents`)
  return res.data
}

// Delete a document
export async function deleteDocument(id: string) {
  const res = await axios.delete(`${API_BASE_URL}/documents/${id}`)
  return res.data
}

// Query a document (ask a question)
export async function queryDocument(id: string, question: string) {
  const res = await axios.post(`${API_BASE_URL}/documents/query`, { id, question })
  return res.data
}