import { useState, useRef, useEffect } from 'react'
import { sendChatMessage } from '../services/chatApi'

export default function ChatPanel({ placeNames = [] }) {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, open])

  const sendMessage = async () => {
    const text = input.trim()
    if (!text || loading) return

    const userMsg = { role: 'user', content: text }
    const updatedMessages = [...messages, userMsg]
    setMessages(updatedMessages)
    setInput('')
    setLoading(true)

    try {
      const res = await sendChatMessage(text, messages, placeNames)
      const reply = res?.data?.reply || 'Sorry, something went wrong.'
      const grounded = res?.data?.grounded_places || []
      setMessages([...updatedMessages, { role: 'assistant', content: reply, grounded_places: grounded }])
    } catch {
      setMessages([...updatedMessages, { role: 'assistant', content: 'Failed to connect to the chat service.' }])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  if (!open) {
    return (
      <button
        className="chat-toggle"
        onClick={() => setOpen(true)}
        title="Chat with WanderWise AI"
      >
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
        </svg>
      </button>
    )
  }

  return (
    <div className="chat-panel">
      <div className="chat-header">
        <span>WanderWise AI</span>
        <button className="chat-close" onClick={() => setOpen(false)} title="Minimize">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
        </button>
      </div>
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="chat-empty">
            <p>Ask me about places in your itinerary!</p>
            {placeNames.length > 0 && (
              <p className="chat-grounded-hint">
                I have data for {placeNames.length} place{placeNames.length > 1 ? 's' : ''} in your route.
              </p>
            )}
          </div>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`chat-bubble chat-bubble-${msg.role}`}>
            <div className="chat-bubble-content">{msg.content}</div>
            {msg.grounded_places && msg.grounded_places.length > 0 && (
              <div className="chat-grounded-badge">
                Grounded: {msg.grounded_places.join(', ')}
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="chat-bubble chat-bubble-assistant">
            <div className="chat-typing">
              <span /><span /><span />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>
      <div className="chat-input-area">
        <textarea
          className="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about your itinerary..."
          rows={1}
          disabled={loading}
        />
        <button
          className="chat-send"
          onClick={sendMessage}
          disabled={loading || !input.trim()}
          title="Send"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="22" y1="2" x2="11" y2="13" />
            <polygon points="22 2 15 22 11 13 2 9 22 2" />
          </svg>
        </button>
      </div>
    </div>
  )
}
