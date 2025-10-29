"use client";

import React, { useState } from "react";
import axios from "axios";
import { toast } from "react-hot-toast";

const API_BASE_URL = "http://127.0.0.1:8000/api";

export default function UploadBox() {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [response, setResponse] = useState<any | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      setFile(event.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      toast.error("Please select a file to upload!");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      setUploading(true);
      toast.loading("Uploading document...");

      const res = await axios.post(`${API_BASE_URL}/documents/upload`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      toast.dismiss();
      toast.success("Document uploaded successfully!");
      setResponse(res.data); // Save response body

    } catch (error: any) {
      toast.dismiss();
      toast.error("Upload failed! Please try again.");
      console.error("Upload Error:", error);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="p-6 bg-white rounded-2xl shadow-lg w-full max-w-xl mx-auto border">
      <h2 className="text-2xl font-semibold mb-4 text-center">📄 Upload Document</h2>

      <div className="flex flex-col items-center gap-3">
        <input
          type="file"
          accept=".pdf,.txt"
          onChange={handleFileChange}
          className="block w-full text-sm border border-gray-300 rounded-lg cursor-pointer p-2"
        />

        <button
          onClick={handleUpload}
          disabled={uploading}
          className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition-all duration-300"
        >
          {uploading ? "Uploading..." : "Upload"}
        </button>
      </div>

      {response && (
        <div className="mt-6 p-4 bg-gray-100 border rounded-lg text-sm">
          <h3 className="font-semibold text-gray-800 mb-2">✅ Upload Response:</h3>
          <pre className="bg-white p-3 rounded-md overflow-auto text-gray-700">
            {JSON.stringify(response, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}