import React from 'react'

const Header: React.FC = () => {
  return (
    <header className="bg-transparent text-white py-8">
      <div className="container mx-auto flex justify-center items-center">
        <h1 className="text-6xl font-bold logo-hover">
          <span className="gradient-text">UI</span>
          <span className="text-white">xtral</span>
        </h1>
      </div>
    </header>
  )
}

export default Header