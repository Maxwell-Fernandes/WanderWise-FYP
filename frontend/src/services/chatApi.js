const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

export async function sendChatMessage(message, history, placeNames) {
  const res = await fetch(`${API_BASE}/chat/message`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      history: history.map((m) => ({ role: m.role, content: m.content })),
      place_names: placeNames
    })
  })
  return res.json()
}
