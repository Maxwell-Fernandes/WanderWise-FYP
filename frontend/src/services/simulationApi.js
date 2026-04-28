const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

export async function runModule1(payload) {
  const res = await fetch(`${API_BASE}/module1/simulate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  return res.json()
}

export async function runModule2(payload) {
  const res = await fetch(`${API_BASE}/module2/simulate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  return res.json()
}

export async function runModule4(payload) {
  const res = await fetch(`${API_BASE}/module4/simulate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  return res.json()
}

export async function narrateModule4Day(payload) {
  const res = await fetch(`${API_BASE}/module4/narrate-day`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  return res.json()
}

export function mapUrl(mapRelPath) {
  const name = mapRelPath?.split('/').pop()
  return name ? `${API_BASE}/maps/${name}` : null
}
