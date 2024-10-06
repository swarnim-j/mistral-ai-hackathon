import React, { useState } from 'react'

interface WebsitePreviewProps {
  website: any
  error: string | null
}

const WebsitePreview: React.FC<WebsitePreviewProps> = ({ website, error }) => {
  const [selectedPage, setSelectedPage] = useState(0)

  if (error) {
    return (
      <div className="glass-morphism p-6">
        <h2 className="text-xl font-semibold mb-4 gradient-text">Website Preview</h2>
        <p className="text-red-500">Error: {error}</p>
      </div>
    )
  }

  if (!website || !website.pages || website.pages.length === 0) {
    return (
      <div className="glass-morphism p-6">
        <h2 className="text-xl font-semibold mb-4 gradient-text">Website Preview</h2>
        <p className="text-gray-400">No website generated yet.</p>
      </div>
    )
  }

  const { theme, pages } = website

  return (
    <div className="glass-morphism p-6">
      <h2 className="text-xl font-semibold mb-4 gradient-text">Website Preview</h2>
      <div className="mb-4">
        <select
          className="w-full p-3 bg-gray-800 text-white border border-gray-700 rounded-md focus:ring-2 focus:ring-primary-color outline-none transition-all duration-300"
          value={selectedPage}
          onChange={(e) => setSelectedPage(Number(e.target.value))}
        >
          {pages.map((page: any, index: number) => (
            <option key={index} value={index}>
              {page.name}
            </option>
          ))}
        </select>
      </div>
      <div className="border border-gray-700 rounded-md p-4 h-[600px] overflow-auto bg-white">
        {pages[selectedPage] && pages[selectedPage].content ? (
          <iframe
            srcDoc={`
              <html>
                <head>
                  <style>${theme.css}</style>
                </head>
                <body>${pages[selectedPage].content}</body>
              </html>
            `}
            className="w-full h-full"
            title={`Generated ${pages[selectedPage].name}`}
          />
        ) : (
          <p className="text-gray-500">No content available for this page.</p>
        )}
      </div>
    </div>
  )
}

export default WebsitePreview