'use client'

import React, { useState, useEffect } from 'react'

interface InputFormProps {
  onSubmit: (prompt: string) => void
  isLoading: boolean
}

const InputForm: React.FC<InputFormProps> = ({ onSubmit, isLoading }) => {
  const [prompt, setPrompt] = useState('')
  const [elapsedTime, setElapsedTime] = useState(0)

  useEffect(() => {
    let interval: NodeJS.Timeout | null = null;
    if (isLoading) {
      setElapsedTime(0)
      interval = setInterval(() => {
        setElapsedTime((prevTime) => prevTime + 1)
      }, 1000)
    } else if (interval) {
      clearInterval(interval)
    }
    return () => {
      if (interval) clearInterval(interval)
    }
  }, [isLoading])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(prompt)
  }

  return (
    <div className="glass-morphism p-6">
      <form onSubmit={handleSubmit} className="flex flex-col">
        <textarea
          className="w-full p-4 bg-white bg-opacity-5 text-white border border-white border-opacity-10 rounded-lg focus:ring-2 focus:ring-primary-color focus:border-primary-color outline-none transition-all duration-300 mb-4"
          rows={4}
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Describe your website..."
          disabled={isLoading}
        />
        <div className="flex items-center justify-between">
          {isLoading && (
            <div className="flex items-center space-x-2">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              <span className="text-sm text-white">{elapsedTime}s</span>
            </div>
          )}
          <button
            type="submit"
            className={`gradient-bg text-white px-6 py-3 rounded-lg font-medium transition-all duration-300 ${
              isLoading ? 'opacity-50 cursor-not-allowed' : 'hover:opacity-90'
            }`}
            disabled={isLoading}
          >
            {isLoading ? 'Generating...' : 'Generate Website'}
          </button>
        </div>
      </form>
    </div>
  )
}

export default InputForm