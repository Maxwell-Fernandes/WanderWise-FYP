import { useState } from 'react'
import { mapUrl, runModule2 } from '../services/simulationApi'

export default function Module2SimulationPage() {
  const [numDays, setNumDays] = useState(4)
  const [travelDistance, setTravelDistance] = useState('more')
  const [hotelLocation, setHotelLocation] = useState('')
  const [region, setRegion] = useState('')
  const [userPreference, setUserPreference] = useState('')
  const [formError, setFormError] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const submit = async (e) => {
    e.preventDefault()
    setFormError('')
    if (travelDistance === 'less' && !hotelLocation && !region) {
      setFormError('Select a hotel location or choose a region for travel less.')
      return
    }
    setLoading(true)
    const data = await runModule2({
      num_days: Number(numDays),
      min_reviews: 1,
      random_state: 42,
      travel_distance: travelDistance,
      hotel_location: hotelLocation || null,
      region: region || null,
      user_preference: userPreference || null
    })
    setResult(data.data)
    setLoading(false)
  }

  return (
    <div>
      <form className="card" onSubmit={submit}>
        <h2>Module 2 - Clustering + Normalization</h2>
        <label>Number of Days / Clusters (K)</label>
        <input type="number" min="1" max="10" value={numDays} onChange={(e) => setNumDays(e.target.value)} />
        <label>Travel distance</label>
        <select value={travelDistance} onChange={(e) => setTravelDistance(e.target.value)}>
          <option value="more">Willing to travel more</option>
          <option value="less">Prefer shorter distances</option>
        </select>
        <label>Hotel location (optional)</label>
        <select value={hotelLocation} onChange={(e) => setHotelLocation(e.target.value)}>
          <option value="">No hotel selected</option>
          <option value="panjim">Panjim</option>
          <option value="margao">Margao</option>
          <option value="mapusa">Mapusa</option>
          <option value="canacona">Canacona</option>
        </select>
        {travelDistance === 'less' && !hotelLocation && (
          <>
            <label>Region (required for travel less)</label>
            <select value={region} onChange={(e) => setRegion(e.target.value)}>
              <option value="">Select a region</option>
              <option value="north">North Goa</option>
              <option value="central">Central Goa</option>
              <option value="south">South Goa</option>
            </select>
          </>
        )}
        <label>User preference (optional)</label>
        <textarea rows="3" value={userPreference} onChange={(e) => setUserPreference(e.target.value)} />
        {formError && (
          <p style={{ color: '#b91c1c', margin: '6px 0 0' }}>{formError}</p>
        )}
        <button type="submit" disabled={loading}>{loading ? 'Running...' : 'Simulate Module 2'}</button>
      </form>

      {result && (
        <>
          <div className="card">
            <p><b>Cluster counts:</b> {JSON.stringify(result.cluster_counts)}</p>
            <p><b>Generated:</b> {result.generated_files.csv}, {result.generated_files.json}</p>
            {result.radius_filter?.enabled && (
              <div style={{ marginTop: '8px', padding: '10px', background: '#f8fafc', borderRadius: '8px' }}>
                <p style={{ margin: '0 0 4px' }}><b>Travel radius filter</b> ({result.radius_filter.travel_distance || 'less'})</p>
                <p style={{ margin: 0 }}>
                  <b>Radius:</b> {result.radius_filter.radius_km?.toFixed?.(1)} km (base {result.radius_filter.base_radius_km} · max {result.radius_filter.max_radius_km})
                </p>
                <p style={{ margin: 0 }}>
                  <b>Anchor:</b> {result.radius_filter.anchor?.label || 'dataset mean'} ({result.radius_filter.anchor?.source || 'dataset_mean'})
                </p>
                <p style={{ margin: 0 }}>
                  <b>Within radius:</b> {result.radius_filter.within_radius} · <b>Exceptions:</b> {result.radius_filter.exceptions_added}
                </p>
                {result.radius_filter.anchor_warning && (
                  <p style={{ margin: 0, color: '#92400e' }}>
                    <b>Anchor warning:</b> {result.radius_filter.anchor_warning}
                  </p>
                )}
                {result.radius_filter.fallback_reason && (
                  <p style={{ margin: 0, color: '#92400e' }}>
                    <b>Fallback:</b> {result.radius_filter.fallback_reason}
                  </p>
                )}
              </div>
            )}
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
