"use client";

import React, { useEffect, useState } from "react";
import axios from "axios";
import { Loader2, Trash2, RefreshCcw } from "lucide-react";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";

const API_BASE_URL = "http://127.0.0.1:8000/api/documents/";

export default function DocumentListBox() {
  const [documents, setDocuments] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const fetchDocuments = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await axios.get(API_BASE_URL, {
        headers: { accept: "application/json" },
      });
      setDocuments(res.data);
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.detail || "Failed to load documents");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (documentId: string) => {
    if (!confirm("Are you sure you want to delete this document?")) return;
    try {
      await axios.delete(`${API_BASE_URL}${documentId}`);
      setDocuments((prev) => prev.filter((d) => d.document_id !== documentId));
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.detail || "Failed to delete document");
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  return (
    <Card className="w-full max-w-3xl mx-auto mt-6 p-6 shadow-md border border-gray-200">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-gray-800">Uploaded Documents</h2>
        <Button
          variant="outline"
          size="sm"
          onClick={fetchDocuments}
          disabled={loading}
        >
          <RefreshCcw className={`w-4 h-4 mr-2 ${loading ? "animate-spin" : ""}`} />
          Refresh
        </Button>
      </div>

      <CardContent>
        {loading ? (
          <div className="flex justify-center items-center h-20">
            <Loader2 className="animate-spin w-6 h-6 text-gray-500" />
          </div>
        ) : error ? (
          <p className="text-red-500 text-center">{error}</p>
        ) : documents.length === 0 ? (
          <p className="text-gray-500 text-center">No documents found.</p>
        ) : (
          <div className="space-y-3">
            {documents.map((doc) => (
              <div
                key={doc.document_id}
                className="flex flex-col md:flex-row md:items-center justify-between border p-3 rounded-md bg-gray-50 hover:bg-gray-100 transition"
              >
                <div>
                  <p className="font-medium text-gray-800">{doc.filename}</p>
                  <p className="text-xs text-gray-600">
                    <strong>ID:</strong> {doc.document_id}
                  </p>
                  <p className="text-xs text-gray-600">
                    <strong>Status:</strong> {doc.status} |{" "}
                    <strong>Chunks:</strong> {doc.chunks_created}
                  </p>
                  <p className="text-xs text-gray-500">
                    <strong>Uploaded:</strong>{" "}
                    {new Date(doc.uploaded_at).toLocaleString()}
                  </p>
                </div>

                <Button
                  variant="destructive"
                  size="sm"
                  className="mt-2 md:mt-0"
                  onClick={() => handleDelete(doc.document_id)}
                >
                  <Trash2 className="w-4 h-4 mr-1" /> Delete
                </Button>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
