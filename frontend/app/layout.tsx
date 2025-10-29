'use client';

import './globals.css';
import { Toaster } from 'react-hot-toast';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50 text-gray-900">
        <Toaster position="top-right" reverseOrder={false} />
        <main className="max-w-4xl mx-auto p-4">{children}</main>
      </body>
    </html>
  );
}