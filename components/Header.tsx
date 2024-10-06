import React from 'react'

const Header: React.FC = () => {
  return (
    <header className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6 shadow-md">
      <div className="container mx-auto">
        <h1 className="text-3xl font-bold">Mistral AI Hackathon</h1>
        <p className="text-sm text-blue-100">Website Generator</p>
      </div>
    </header>
  )
}

export default Header