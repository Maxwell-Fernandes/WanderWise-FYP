import { useState } from 'react'
import { mapUrl, runModule2 } from '../services/simulationApi'

export default function Module2SimulationPage() {
  const [numDays, setNumDays] = useState(4)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const submit = async (e) => {
    e.preventDefault()
    setLoading(true)
    const data = await runModule2({ num_days: Number(numDays), min_reviews: 1, random_state: 42 })
    setResult(data.data)
    setLoading(false)
  }

  return (
    <div>
      <form className="card" onSubmit={submit}>
        <h2>Module 2 - Clustering + Normalization</h2>
        <label>Number of Days / Clusters (K)</label>
        <input type="number" min="1" max="10" value={numDays} onChange={(e) => setNumDays(e.target.value)} />
        <button type="submit" disabled={loading}>{loading ? 'Running...' : 'Simulate Module 2'}</button>
      </form>

      {result && (
        <>
          <div className="card">
            <p><b>Cluster counts:</b> {JSON.stringify(result.cluster_counts)}</p>
            <p><b>Generated:</b> {result.generated_files.csv}, {result.generated_files.json}</p>
          </div>
          <div className="card">
            <h3>Map Output</h3>
            <iframe src={mapUrl(result.generated_files.map)} title="module2-map" />
          </div>
        </>
      )}
    </div>
  )
}
