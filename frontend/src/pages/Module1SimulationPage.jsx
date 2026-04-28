import { useState } from 'react'
import { mapUrl, runModule1 } from '../services/simulationApi'

export default function Module1SimulationPage() {
  const [userPreference, setUserPreference] = useState('I love exploring historical forts and beaches, interested in nature waterfalls, but not interested in nightlife or shopping')
  const [useLlmInterests, setUseLlmInterests] = useState(false)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const submit = async (e) => {
    e.preventDefault()
    setLoading(true)
    const data = await runModule1({
      user_preference: userPreference,
      min_rating: 3.0,
      use_llm_interests: useLlmInterests
    })
    setResult(data.data)
    setLoading(false)
  }

  return (
    <div>
      <form className="card" onSubmit={submit}>
        <h2>Module 1 - Preference Filtering</h2>
        <textarea rows="4" value={userPreference} onChange={(e) => setUserPreference(e.target.value)} />
        <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
          <input
            type="checkbox"
            checked={useLlmInterests}
            onChange={(e) => setUseLlmInterests(e.target.checked)}
          />
          Use Groq to interpret interests (requires GROQ_API_KEY on server)
        </label>
        <button type="submit" disabled={loading}>{loading ? 'Running...' : 'Simulate Module 1'}</button>
      </form>

      {result && (
        <>
          <div className="card">
            <p><b>Original:</b> {result.counts.original} | <b>Filtered:</b> {result.counts.filtered}</p>
            <p><b>Interests source:</b> {result.interests_source || '—'}</p>
            <p><b>Positive:</b> {(result.positive_interests || []).join(', ') || '—'}</p>
            <p><b>Negative:</b> {(result.negative_interests || []).join(', ') || '—'}</p>
            {result.preference_extraction && (
              <pre style={{ fontSize: '0.85em', overflow: 'auto' }}>{JSON.stringify(result.preference_extraction, null, 2)}</pre>
            )}
            <p><b>Generated:</b> {result.generated_files.csv}, {result.generated_files.json}</p>
          </div>
          <div className="card">
            <h3>Map Output</h3>
            <iframe src={mapUrl(result.generated_files.map)} title="module1-map" />
          </div>
        </>
      )}
    </div>
  )
}
