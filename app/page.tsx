'use client'

import { useState } from 'react'
import Header from '../components/Header'
import InputForm from '../components/InputForm'
import WebsitePreview from '../components/WebsitePreview'
import Footer from '../components/Footer'

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
    <div className="flex flex-col min-h-screen bg-[rgb(var(--background-rgb))]">
      <Header />
      <main className="flex-grow container mx-auto px-4 py-8 flex flex-col lg:flex-row">
        <div className="lg:w-1/3 lg:pr-8 mb-8 lg:mb-0">
          <h2 className="text-4xl font-bold mb-6 leading-tight">
            <span className="gradient-text">Elevate</span> Your Web <span className="gradient-text">Presence</span>
          </h2>
          <p className="text-xl mb-8 text-gray-300">Create stunning, relevant and functional websites with a single prompt in minutes.</p>
          <InputForm onSubmit={handleWebsiteGeneration} isLoading={isLoading} />
        </div>
        <div className="lg:w-2/3 flex-grow overflow-hidden">
          <div className="h-[600px] lg:h-[700px]">
            <WebsitePreview website={generatedWebsite} error={error} />
          </div>
        </div>
      </main>
      <Footer />
    </div>
  )
}