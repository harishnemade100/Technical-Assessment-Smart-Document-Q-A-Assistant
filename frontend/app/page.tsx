"use client";

import { useState, useEffect } from "react";
import UploadBox from "@/components/UploadBox";
import DocumentList from "@/components/DocumentList";
import AskQuestionBox from "@/components/AskQuestionBox";
import ThemeToggle from "@/components/ThemeToggle";
import AuthModal from "@/components/AuthModal";
import { Toaster, toast } from "sonner";

export default function Page() {
  const [activeTab, setActiveTab] = useState("upload");
  const [isAuth, setIsAuth] = useState(false);
  const [username, setUsername] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("token");
    const user = localStorage.getItem("username");
    if (token) {
      setIsAuth(true);
      if (user) setUsername(user);
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    setIsAuth(false);
    toast.success("Logged out successfully!");
  };

  if (!isAuth) return <AuthModal onAuthSuccess={() => setIsAuth(true)} />;

  return (
    <div className="min-h-screen bg-gray-950 text-gray-200 flex flex-col items-center py-10 px-4">
      <div className="w-full max-w-5xl">
        {/* Header */}
        <header className="flex items-center justify-between mb-10">
          <h1 className="text-3xl font-bold text-indigo-400 tracking-wide">
            ⚡ Smart Document Q&A Assistant
          </h1>

          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-400">
              👤 {username || "User"}
            </span>
            <button
              onClick={handleLogout}
              className="px-4 py-1 text-sm bg-red-600 hover:bg-red-700 rounded-lg font-medium transition-all"
            >
              Logout
            </button>
            <ThemeToggle />
          </div>
        </header>

        {/* Navigation Tabs */}
        <nav className="flex justify-center gap-4 mb-8">
          {["upload", "list", "ask"].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-5 py-2 rounded-xl text-sm font-semibold transition-all ${
                activeTab === tab
                  ? "bg-indigo-600 text-white shadow-lg"
                  : "bg-gray-800 text-gray-400 hover:bg-gray-700"
              }`}
            >
              {tab === "upload"
                ? "📁 Upload"
                : tab === "list"
                ? "📜 Documents"
                : "❓ Ask Question"}
            </button>
          ))}
        </nav>

        {/* Main Content */}
        <main className="bg-gray-900/70 backdrop-blur-xl border border-gray-800 rounded-2xl p-8 shadow-2xl">
          {activeTab === "upload" && (
            <UploadBox onUpload={() => setActiveTab("list")} />
          )}
          {activeTab === "list" && <DocumentList />}
          {activeTab === "ask" && <AskQuestionBox />}
        </main>
      </div>

      <Toaster position="top-right" />
    </div>
  );
}