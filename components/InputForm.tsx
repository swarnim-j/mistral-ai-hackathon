'use client'

import React, { useState } from 'react'

interface InputFormProps {
  onSubmit: (prompt: string) => void
  isLoading: boolean
}

const InputForm: React.FC<InputFormProps> = ({ onSubmit, isLoading }) => {
  const [prompt, setPrompt] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(prompt)
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold mb-4 text-gray-800">Generate Website</h2>
      <form onSubmit={handleSubmit}>
        <textarea
          className="w-full p-3 bg-gray-100 text-gray-800 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all duration-300"
          rows={6}
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Describe your event..."
          disabled={isLoading}
        />
        <button
          type="submit"
          className={`mt-4 bg-gradient-to-r from-blue-500 to-purple-500 text-white px-6 py-3 rounded-md hover:from-blue-600 hover:to-purple-600 transition-all duration-300 ${
            isLoading ? 'opacity-50 cursor-not-allowed' : ''
          }`}
          disabled={isLoading}
        >
          {isLoading ? 'Generating...' : 'Generate Website'}
        </button>
      </form>
    </div>
  )
}

export default InputForm