'use client'

import { useState } from 'react'
import Header from '../components/Header'
import InputForm from '../components/InputForm'
import WebsitePreview from '../components/WebsitePreview'

export default function Home() {
  const [generatedWebsite, setGeneratedWebsite] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleWebsiteGeneration = async (prompt: string) => {
    setIsLoading(true)
    setError(null)

    try {
      const response = await fetch('/api/generate-website', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt }),
      })

      if (!response.ok) {
        throw new Error('Failed to generate website')
      }

      const data = await response.json()
      setGeneratedWebsite(data)
    } catch (error) {
      console.error('Error generating website:', error)
      setError(error instanceof Error ? error.message : 'An unknown error occurred')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <Header />
      <main className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <InputForm onSubmit={handleWebsiteGeneration} isLoading={isLoading} />
          <WebsitePreview website={generatedWebsite} error={error} />
        </div>
      </main>
    </div>
  )
}