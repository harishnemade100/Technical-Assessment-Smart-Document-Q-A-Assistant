"use client";

import { useState } from "react";
import { toast } from "sonner";
import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8000/api/auth/login";

export default function AuthModal({ onAuthSuccess }) {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleAuth = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      if (isLogin) {
        // LOGIN
        const response = await axios.post(API_BASE_URL, new URLSearchParams({
          username,
          password,
        }));
        localStorage.setItem("token", response.data.access_token);
        toast.success("Login successful!");
        onAuthSuccess();
      } else {
        // REGISTER
        await api.post("/auth/register", { username, password });
        toast.success("Registered successfully! You can now login.");
        setIsLogin(true);
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || "Authentication failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <form
        onSubmit={handleAuth}
        className="bg-white shadow-lg rounded-2xl p-6 w-full max-w-sm"
      >
        <h2 className="text-2xl font-semibold text-center mb-4">
          {isLogin ? "Login" : "Register"}
        </h2>
        <input
          type="text"
          placeholder="Username"
          className="w-full p-2 border rounded mb-3"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <input
          type="password"
          placeholder="Password"
          className="w-full p-2 border rounded mb-3"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
        >
          {loading ? "Please wait..." : isLogin ? "Login" : "Register"}
        </button>
        <p
          className="text-center text-sm text-gray-600 mt-3 cursor-pointer"
          onClick={() => setIsLogin(!isLogin)}
        >
          {isLogin
            ? "Don't have an account? Register"
            : "Already registered? Login"}
        </p>
      </form>
    </div>
  );
}