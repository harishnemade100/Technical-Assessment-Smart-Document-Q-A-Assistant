"use client";

import { useState } from "react";
import axios from "axios";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Upload, Loader2 } from "lucide-react";

const API_BASE_URL = "http://127.0.0.1:8000/api/documents/upload";

export default function UploadBox() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [responseData, setResponseData] = useState<any | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) {
      toast.error("📄 Please select a file to upload!");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      setLoading(true);
      setResponseData(null); // clear old data
      const res = await axios.post(API_BASE_URL, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setResponseData(res.data); // ✅ Save backend response
      toast.success("File uploaded successfully!");
    } catch (error) {
      console.error(error);
      toast.error("Upload failed!");
    } finally {
      setLoading(false);
      setFile(null);
    }
  };

  return (
    <div className="bg-gray-800/70 border border-gray-700 p-6 rounded-2xl shadow-lg text-center space-y-4">
      <h2 className="text-xl font-semibold text-white">📤 Upload a Document</h2>

      <input
        type="file"
        accept=".pdf,.txt"
        onChange={handleFileChange}
        className="block w-full text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg 
                   file:border-0 file:text-sm file:font-semibold file:bg-indigo-600 
                   file:text-white hover:file:bg-indigo-700 mb-4"
      />

      <Button
        onClick={handleUpload}
        disabled={loading}
        className="w-full flex justify-center items-center gap-2 bg-indigo-600 hover:bg-indigo-700"
      >
        {loading ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" /> Uploading...
          </>
        ) : (
          <>
            <Upload className="w-5 h-5" /> Upload File
          </>
        )}
      </Button>

      {/* ✅ Display the response JSON */}
      {responseData && (
        <div className="mt-6 text-left bg-gray-900/60 border border-gray-700 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-indigo-400 mb-2">
            📦 Upload Response:
          </h3>
          <pre className="text-gray-300 text-sm overflow-x-auto whitespace-pre-wrap">
            {JSON.stringify(responseData, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
