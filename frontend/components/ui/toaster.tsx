"use client";

import { Toaster as Sonner } from "sonner";

export function Toaster() {
  return (
    <Sonner
      position="top-right"
      toastOptions={{
        style: { background: "white", border: "1px solid #ddd" },
        className: "shadow-lg rounded-xl font-medium",
      }}
    />
  );
}