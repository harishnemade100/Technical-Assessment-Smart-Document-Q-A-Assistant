"use client";

import { useState } from "react";
import axios from "axios";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Loader2, MessageSquare } from "lucide-react";

const API_BASE_URL = "http://127.0.0.1:8000/api/qa/query";

export default function AskQuestionBox() {
  const [documentId, setDocumentId] = useState("");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleAsk = async () => {
    if (!documentId || !question) {
      toast.error("Please enter both Document ID and your question!");
      return;
    }

    try {
      setLoading(true);
      setAnswer(null);
      const res = await axios.post(
        `${API_BASE_URL}?document_id=${documentId}&question=${encodeURIComponent(question)}`
      );

      setAnswer(res.data.answer);
      toast.success("✅ Question answered!");
    } catch (error: any) {
      console.error(error);
      toast.error("❌ Failed to get answer!");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-gray-800/70 border border-gray-700 p-6 rounded-2xl shadow-lg text-center space-y-4">
      <h2 className="text-xl font-semibold text-white">💬 Ask a Question</h2>

      <input
        type="text"
        placeholder="Enter Document ID"
        value={documentId}
        onChange={(e) => setDocumentId(e.target.value)}
        className="w-full bg-gray-800 border border-gray-600 text-gray-200 rounded-lg p-2 
                   focus:ring-2 focus:ring-indigo-600 outline-none"
      />

      <textarea
        placeholder="Type your question..."
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        className="w-full bg-gray-800 border border-gray-600 text-gray-200 rounded-lg p-2 
                   focus:ring-2 focus:ring-indigo-600 outline-none h-24 resize-none"
      />

      <Button
        onClick={handleAsk}
        disabled={loading}
        className="w-full flex justify-center items-center gap-2 bg-indigo-600 hover:bg-indigo-700"
      >
        {loading ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" /> Searching...
          </>
        ) : (
          <>
            <MessageSquare className="w-5 h-5" /> Ask Question
          </>
        )}
      </Button>

      {answer && (
        <div className="mt-4 p-4 bg-gray-900/60 border border-gray-700 rounded-xl text-left text-gray-300">
          <h3 className="font-semibold text-indigo-400 mb-2">Answer:</h3>
          <p>{answer}</p>
        </div>
      )}
    </div>
  );
}
