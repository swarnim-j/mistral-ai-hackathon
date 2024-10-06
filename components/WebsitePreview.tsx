import React, { useState } from 'react'

interface WebsitePreviewProps {
  website: any
  error: string | null
}

const WebsitePreview: React.FC<WebsitePreviewProps> = ({ website, error }) => {
  const [selectedPage, setSelectedPage] = useState(0)

  if (error) {
    return (
      <div className="glass-morphism p-4 h-full flex flex-col">
        <h2 className="text-2xl font-bold mb-4">Website Preview</h2>
        <p className="text-red-400 flex-grow">Error: {error}</p>
      </div>
    )
  }

  if (!website || !website.pages || website.pages.length === 0) {
    return (
      <div className="glass-morphism p-4 h-full flex flex-col">
        <h2 className="text-2xl font-bold mb-4">Website Preview</h2>
        <p className="text-gray-400 flex-grow">No website generated yet.</p>
      </div>
    )
  }

  const { theme, pages } = website

  const getDisplayName = (pageName: string) => {
    if (pageName === 'index.html') return 'Home'
    return pageName.replace('.html', '').charAt(0).toUpperCase() + pageName.replace('.html', '').slice(1)
  }

  return (
    <div className="glass-morphism p-4 h-full flex flex-col">
      <h2 className="text-2xl font-bold mb-4">Website Preview</h2>
      <div className="mb-4 flex flex-wrap gap-2">
        {pages.map((page: any, index: number) => (
          <button
            key={index}
            className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
              selectedPage === index
                ? 'bg-white bg-opacity-10 text-white'
                : 'text-gray-400 hover:text-white'
            }`}
            onClick={() => setSelectedPage(index)}
          >
            {getDisplayName(page.name)}
          </button>
        ))}
      </div>
      <div className="flex-grow bg-white rounded-lg overflow-hidden">
        {pages[selectedPage] && pages[selectedPage].content ? (
          <iframe
            srcDoc={`
              <html>
                <head>
                  <style>${theme.css}</style>
                  <style>
                    body { margin: 0; padding: 0; height: 100vh; overflow: auto; }
                    * { box-sizing: border-box; }
                  </style>
                </head>
                <body>${pages[selectedPage].content}</body>
              </html>
            `}
            className="w-full h-full border-0"
            title={`Generated ${getDisplayName(pages[selectedPage].name)}`}
          />
        ) : (
          <p className="text-gray-500 p-4">No content available for this page.</p>
        )}
      </div>
    </div>
  )
}

export default WebsitePreview