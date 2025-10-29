"use client";

import React, { useState } from "react";
import axios from "axios";
import { Button } from "../components/ui/button";
import { Loader2, Send } from "lucide-react";
import { Card, CardContent } from "../components/ui/card";
import { useToast } from "../components/ui/use-toast";

const API_URL = "http://127.0.0.1:8000/api/qa/query";

export default function AskQuestionBox({ selectedDocId }: { selectedDocId?: string | null }) {
  const [documentId, setDocumentId] = useState("");
  const [question, setQuestion] = useState("");
  const [response, setResponse] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const handleAsk = async () => {
    if (!documentId || !question) {
      toast({
        title: "Missing fields",
        description: "Please enter both document ID and question.",
        variant: "destructive",
      });
      return;
    }

    try {
      setLoading(true);
      const res = await axios.post(`${API_URL}?document_id=${documentId}&question=${encodeURIComponent(question)}`);
      setResponse(res.data);
      toast({ title: "Answer received", description: "Your question was processed successfully!" });
    } catch (err) {
      console.error(err);
      toast({
        title: "Error",
        description: "Failed to fetch answer from backend.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="w-full max-w-3xl mx-auto mt-6 p-6 shadow-md border border-gray-200 bg-white">
      <h2 className="text-lg font-semibold text-gray-800 mb-3">💬 Ask a Question</h2>
      <CardContent className="space-y-4">
        <input
          type="text"
          value={documentId}
          onChange={(e) => setDocumentId(e.target.value)}
          placeholder="Enter Document ID"
          className="w-full border rounded-lg p-2 text-gray-700"
        />
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Type your question here..."
          rows={3}
          className="w-full border rounded-lg p-2 text-gray-700"
        />
        <Button
          onClick={handleAsk}
          disabled={loading}
          className="bg-green-600 hover:bg-green-700 text-white font-medium"
        >
          {loading ? <Loader2 className="animate-spin w-4 h-4 mr-2" /> : <Send className="w-4 h-4 mr-2" />}
          {loading ? "Asking..." : "Ask Question"}
        </Button>

        {response && (
          <div className="mt-4 border-t pt-4">
            <h3 className="font-semibold text-gray-800">Answer:</h3>
            <p className="text-gray-700 mt-1">{response.answer}</p>

            <h4 className="font-medium text-gray-800 mt-4">Sources:</h4>
            <ul className="list-disc list-inside text-gray-600 text-sm">
              {response.sources?.map((src: any, idx: number) => (
                <li key={idx}>{src.chunk_text}</li>
              ))}
            </ul>

            <p className="text-xs text-gray-500 mt-2">
              ⏱ {response.processing_time_seconds}s | Doc ID: {response.document_id}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
