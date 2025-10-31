'use client'

import React from 'react'
import { queryDocument } from '../lib/api'
import Spinner from './Spinner'
import { pushToast } from './Toast'

interface QueryModalProps {
  doc: { id: string; filename?: string; name?: string } | null
  onClose: () => void
}

export default function QueryModal({ doc, onClose }: QueryModalProps) {
  const [question, setQuestion] = React.useState('')
  const [answer, setAnswer] = React.useState<string | null>(null)
  const [loading, setLoading] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)

  if (!doc) return null

  // Handle "Ask Question" logic
  async function handleAsk() {
    setError(null)
    setAnswer(null)

    if (!question.trim()) {
      setError('Please type a question')
      return
    }

    setLoading(true)
    try {
      const res = await queryDocument(doc.id, question)
      // assuming backend returns { answer }
      setAnswer(res.answer ?? JSON.stringify(res))
      pushToast('Answer ready', 'success')
    } catch (err: any) {
      console.error(err)
      setError(err?.response?.data?.message || 'Failed to get answer')
      pushToast('Query failed', 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center">
      {/* Overlay background */}
      <div
        className="absolute inset-0 bg-black/40 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal content */}
      <div className="relative z-50 w-full max-w-2xl p-6 bg-white rounded-lg shadow-lg animate-fadeIn">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div>
            <h3 className="text-lg font-semibold">
              Ask about: {doc.filename ?? doc.name ?? 'Untitled'}
            </h3>
            <p className="text-sm text-gray-500">Document ID: {doc.id}</p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 transition"
          >
            ✕
          </button>
        </div>

        {/* Input & actions */}
        <div className="mt-4">
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            rows={4}
            className="w-full p-3 border rounded focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
            placeholder="Type your question about this document..."
          />

          <div className="mt-3 flex items-center gap-2">
            <button
              onClick={handleAsk}
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2 rounded bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50 transition"
            >
              {loading ? (
                <>
                  <Spinner size={16} /> Asking...
                </>
              ) : (
                'Ask'
              )}
            </button>

            <button
              onClick={() => {
                setQuestion('')
                setAnswer(null)
                setError(null)
              }}
              className="px-4 py-2 rounded border hover:bg-gray-100 transition"
            >
              Reset
            </button>
          </div>

          {/* Loading */}
          {loading && (
            <div className="mt-3 flex justify-center">
              <Spinner />
            </div>
          )}

          {/* Error */}
          {error && <div className="mt-3 text-red-600 text-sm">{error}</div>}

          {/* Answer */}
          {answer && (
            <div className="mt-4 p-4 bg-gray-50 rounded border">
              <h4 className="font-medium text-gray-800">Answer</h4>
              <div className="mt-2 text-gray-700 whitespace-pre-wrap text-sm">
                {answer}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
