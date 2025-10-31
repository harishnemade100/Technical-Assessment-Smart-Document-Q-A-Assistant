"use client";

import { useEffect, useState } from "react";
import axios from "axios";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import Spinner from "@/components/ui/spinner";
import { Search, Copy } from "lucide-react";

const API_BASE_URL = "http://127.0.0.1:8000/api/documents/";

interface Document {
  document_id: string;
  filename: string;
  status: string;
  chunks_created: number;
  uploaded_at: string;
}

export default function DocumentList() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState("");

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      const res = await axios.get(API_BASE_URL);
      setDocuments(res.data);
    } catch {
      toast.error("❌ Failed to fetch documents");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await axios.delete(`${API_BASE_URL}${id}`);
      toast.success("🗑️ Document deleted");
      fetchDocuments();
    } catch {
      toast.error("Delete failed");
    }
  };

  const handleCopyId = (id: string) => {
    navigator.clipboard.writeText(id);
    toast.success("📋 Document ID copied!");
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const filteredDocs = documents.filter((doc) =>
    doc.filename.toLowerCase().includes(search.toLowerCase())
  );

  if (loading) return <Spinner />;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <h2 className="text-2xl font-semibold text-white">
          📜 Document List{" "}
          <span className="text-indigo-400 text-lg font-normal">
            ({filteredDocs.length} Document
            {filteredDocs.length !== 1 ? "s" : ""})
          </span>
        </h2>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-3 text-gray-500 w-5 h-5" />
          <input
            type="text"
            placeholder="Search documents..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="bg-gray-800 text-gray-200 pl-10 pr-3 py-2 rounded-lg border border-gray-700 focus:ring-2 focus:ring-indigo-600 outline-none"
          />
        </div>
      </div>

      {/* Document List */}
      {filteredDocs.length === 0 ? (
        <p className="text-gray-400 text-center py-8">
          No matching documents found.
        </p>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {filteredDocs.map((doc) => (
            <div
              key={doc.document_id}
              className="bg-gray-800/70 border border-gray-700 rounded-xl p-5 flex flex-col justify-between hover:bg-gray-800 transition-all shadow-md"
            >
              <div>
                <p className="font-medium text-indigo-300 text-lg">
                  {doc.filename}
                </p>
                <div className="flex items-center gap-2 mt-1">
                  <p className="text-xs text-gray-500 break-all">
                    🆔 {doc.document_id}
                  </p>
                  <button
                    onClick={() => handleCopyId(doc.document_id)}
                    className="text-gray-400 hover:text-indigo-400 transition"
                    title="Copy Document ID"
                  >
                    <Copy size={14} />
                  </button>
                </div>
                <p className="text-sm text-gray-400 mt-2">
                  Status:{" "}
                  <span
                    className={`${
                      doc.status === "processed"
                        ? "text-green-400"
                        : "text-yellow-400"
                    } font-medium`}
                  >
                    {doc.status}
                  </span>{" "}
                  • Chunks: {doc.chunks_created}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  Uploaded: {new Date(doc.uploaded_at).toLocaleString()}
                </p>
              </div>

              <Button
                variant="outline"
                onClick={() => handleDelete(doc.document_id)}
                className="mt-4 border-gray-600 text-gray-200 hover:bg-red-600 hover:text-white transition"
              >
                Delete
              </Button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
