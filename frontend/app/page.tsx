"use client";

import React, { useState } from "react";
import {Toaster } from "../components/ui/toaster";
// import { Toaster } from "@/components/ui/sonner";
import UploadBox from "../components/UploadBox";
import DocumentListBox from "../components/DocumentList";
import AskQuestionBox from "../components/AskQuestionBox";

export default function Page() {
  const [selectedDocId, setSelectedDocId] = useState<string | null>(null);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-100 flex flex-col items-center p-6 space-y-8">
      {/* 🌟 Header */}
      <header className="text-center mt-6">
        <h1 className="text-4xl font-extrabold text-gray-800 tracking-tight">
          Smart Document Q&A Assistant
        </h1>
        <p className="text-gray-600 mt-2">
          Upload a document, view all your files, and ask questions instantly.
        </p>
      </header>

      {/* 📂 Upload Section */}
      <section className="w-full max-w-3xl">
        <UploadBox onUploadSuccess={() => window.location.reload()} />
      </section>

      {/* 📜 Documents List */}
      <section className="w-full max-w-3xl">
        <DocumentListBox />
      </section>

      {/* 💬 Ask Question */}
      <section className="w-full max-w-3xl">
        <AskQuestionBox selectedDocId={selectedDocId} />
      </section>

      <Toaster />
    </div>
  );
}