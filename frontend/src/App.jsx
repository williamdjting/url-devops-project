import { useMemo, useState } from 'react'

const defaultApiBase = 'http://localhost:8000'

function App() {
  const apiBase = useMemo(() => import.meta.env.VITE_API_BASE ?? defaultApiBase, [])
  const [url, setUrl] = useState('')
  const [customCode, setCustomCode] = useState('')
  const [shortUrl, setShortUrl] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (event) => {
    event.preventDefault()
    setIsLoading(true)
    setError('')
    setShortUrl('')

    // Normalize inputs
    const trimmedUrl = url.trim()
    const trimmedCustomCode = customCode.trim()

    // Basic validation
    if (!trimmedUrl) {
      setError('Please enter a URL')
      setIsLoading(false)
      return
    }

    try {
      const response = await fetch(`${apiBase}/shorten`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          url: trimmedUrl, 
          custom_code: trimmedCustomCode || undefined 
        }),
      })

      if (!response.ok) {
        const data = await response.json().catch(() => ({}))
        // Handle Pydantic validation errors
        if (data.detail && Array.isArray(data.detail)) {
          const errors = data.detail.map(err => {
            const field = err.loc?.join('.') || 'field'
            return `${field}: ${err.msg}`
          }).join(', ')
          throw new Error(errors)
        }
        throw new Error(data.detail || `Failed to shorten URL (${response.status})`)
      }

      const payload = await response.json()
      setShortUrl(payload.short_url)
    } catch (err) {
      // Handle network errors
      if (err instanceof TypeError && err.message.includes('fetch')) {
        setError(`Network error: Could not connect to backend at ${apiBase}. Make sure the backend is running.`)
      } else {
        setError(err.message || 'An unexpected error occurred')
      }
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <main className="app-shell">
      <section className="card">
        <h1>Simple URL Shortener</h1>
        <form onSubmit={handleSubmit}>
          <label>
            Long URL
            <input
              type="url"
              placeholder="https://example.com/very/long/link"
              value={url}
              onChange={(event) => setUrl(event.target.value)}
              required
            />
          </label>

          <label>
            Custom code (optional)
            <input
              type="text"
              placeholder="my-alias"
              value={customCode}
              onChange={(event) => setCustomCode(event.target.value)}
              minLength={4}
              maxLength={16}
            />
          </label>

          <button type="submit" disabled={isLoading}>
            {isLoading ? 'Working…' : 'Shorten'}
          </button>
        </form>

        {error && <p className="error">{error}</p>}
        {shortUrl && (
          <p className="result">
            Short link: <a href={shortUrl}>{shortUrl}</a>
          </p>
        )}
      </section>
    </main>
  )
}

export default App
