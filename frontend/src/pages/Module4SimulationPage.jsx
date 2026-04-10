import { useState } from 'react'
import { mapUrl, runModule4 } from '../services/simulationApi'

export default function Module4SimulationPage() {
  const [numDays, setNumDays] = useState(4)
  const [userPreference, setUserPreference] = useState('I love exploring historical forts and beaches, interested in nature waterfalls, but not interested in nightlife or shopping')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [selectedRankByDay, setSelectedRankByDay] = useState({})

  const submit = async (e) => {
    e.preventDefault()
    setLoading(true)
    const data = await runModule4({
      num_days: Number(numDays),
      user_preference: userPreference,
      min_rating: 3.0,
      min_reviews: 1,
      population_size: 100,
      max_generations: 50,
      mutation_rate: 0.2,
      crossover_rate: 0.7,
      random_state: 42,
      use_osrm: true
    })
    setResult(data.data)
    const defaults = {}
    Object.entries(data.data.routes || {}).forEach(([dayKey, dayData]) => {
      defaults[dayKey] = (dayData.alternatives?.[0]?.rank) || 1
    })
    setSelectedRankByDay(defaults)
    setLoading(false)
  }

  const routeSetDiffPercent = (aRoute = [], bRoute = []) => {
    const a = new Set(aRoute.map((x) => x.poi_id || x.name))
    const b = new Set(bRoute.map((x) => x.poi_id || x.name))
    const union = new Set([...a, ...b])
    if (union.size === 0) return 0
    let inter = 0
    union.forEach((id) => {
      if (a.has(id) && b.has(id)) inter += 1
    })
    return ((1 - inter / union.size) * 100)
  }

  return (
    <div>
      <form className="card" onSubmit={submit}>
        <h2>Module 4 - Genetic Algorithm Route Optimization</h2>
        <label>Number of Days</label>
        <input type="number" min="1" max="10" value={numDays} onChange={(e) => setNumDays(e.target.value)} />
        <label>User Preference</label>
        <textarea rows="4" value={userPreference} onChange={(e) => setUserPreference(e.target.value)} />
        <button type="submit" disabled={loading}>{loading ? 'Running...' : 'Simulate Module 4'}</button>
      </form>

      {result && (
        <>
          <div className="card">
            <p><b>Days:</b> {result.num_days}</p>
            <p><b>Module chain:</b> module1_run_id={result.module1_run_id}, module2_run_id={result.module2_run_id}</p>
            <p><b>Generated:</b> {result.generated_files.optimized_routes}</p>
          </div>
          {Object.entries(result.routes).map(([dayKey, dayData]) => (
            <div className="card" key={dayKey}>
              <h3>{dayKey} - Top Alternatives</h3>
              <div style={{ display: 'flex', gap: '8px', marginBottom: '12px' }}>
                {(dayData.alternatives || []).map((alt) => (
                  <button
                    type="button"
                    key={alt.rank}
                    onClick={() => setSelectedRankByDay((prev) => ({ ...prev, [dayKey]: alt.rank }))}
                    style={{ width: 'auto', background: selectedRankByDay[dayKey] === alt.rank ? '#1d4ed8' : '#64748b' }}
                  >
                    Rank {alt.rank}
                  </button>
                ))}
              </div>
              {(dayData.alternatives || []).map((alt) => (
                <p key={`s-${alt.rank}`}>Rank {alt.rank}: fitness={alt.fitness_score?.toFixed?.(6)} | POIs={alt.route?.length || 0}</p>
              ))}
              {(() => {
                const chosen = (dayData.alternatives || []).find((x) => x.rank === selectedRankByDay[dayKey]) || dayData.alternatives?.[0]
                const rank1 = (dayData.alternatives || []).find((x) => x.rank === 1) || dayData.alternatives?.[0]
                const diffPct = routeSetDiffPercent(rank1?.route || [], chosen?.route || [])
                return chosen ? (
                  <>
                    <div style={{ background: '#f8fafc', padding: '12px', borderRadius: '8px', marginBottom: '10px' }}>
                      <p><b>DAY {dayData.day} OPTIMIZED ROUTE — Rank {chosen.rank}</b></p>
                      <p>
                        <b>Fitness:</b> {chosen.fitness_score?.toFixed?.(3)} |{' '}
                        <b>POI Value:</b> {chosen.poi_value_sum?.toFixed?.(3)} |{' '}
                        <b>Travel:</b> {chosen.total_distance_km?.toFixed?.(1)} km ({chosen.total_travel_time_min?.toFixed?.(0)} min) |{' '}
                        <b>Time:</b> {(chosen.total_time_hours || (chosen.total_time_min ? chosen.total_time_min / 60 : null))?.toFixed?.(2)} hours
                      </p>
                      <p>
                        <b>Difference vs Rank 1:</b> {diffPct.toFixed(1)}% |{' '}
                        <b>Nearby Suggestions:</b> {chosen.nearby_suggestions_total || 0}
                      </p>
                    </div>
                    <div style={{ overflowX: 'auto', marginBottom: '12px' }}>
                      <table style={{ width: '100%', borderCollapse: 'collapse', background: 'white' }}>
                        <thead>
                          <tr>
                            <th style={{ textAlign: 'left', borderBottom: '1px solid #ddd', padding: '8px' }}>#</th>
                            <th style={{ textAlign: 'left', borderBottom: '1px solid #ddd', padding: '8px' }}>Place</th>
                            <th style={{ textAlign: 'left', borderBottom: '1px solid #ddd', padding: '8px' }}>Arrive</th>
                            <th style={{ textAlign: 'left', borderBottom: '1px solid #ddd', padding: '8px' }}>Visit</th>
                            <th style={{ textAlign: 'left', borderBottom: '1px solid #ddd', padding: '8px' }}>Duration</th>
                            <th style={{ textAlign: 'left', borderBottom: '1px solid #ddd', padding: '8px' }}>WPI</th>
                          </tr>
                        </thead>
                        <tbody>
                          {(chosen.route || []).map((stop, idx) => (
                            <tr key={`${dayKey}-${chosen.rank}-${stop.sequence}`}>
                              <td style={{ borderBottom: '1px solid #f1f5f9', padding: '8px' }}>{idx + 1}</td>
                              <td style={{ borderBottom: '1px solid #f1f5f9', padding: '8px' }}>{stop.name}</td>
                              <td style={{ borderBottom: '1px solid #f1f5f9', padding: '8px' }}>{stop.arrival_time}</td>
                              <td style={{ borderBottom: '1px solid #f1f5f9', padding: '8px' }}>{stop.visit_start} - {stop.visit_end}</td>
                              <td style={{ borderBottom: '1px solid #f1f5f9', padding: '8px' }}>{stop.visit_duration_min} min</td>
                              <td style={{ borderBottom: '1px solid #f1f5f9', padding: '8px' }}>{stop.wpi_score?.toFixed?.(3)}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                    <div style={{ background: '#fff7ed', padding: '10px', borderRadius: '8px', marginBottom: '12px' }}>
                      <p><b>Nearby Places You Can Also Consider (outside this route)</b></p>
                      {(chosen.route || []).map((stop) => (
                        <div key={`n-${dayKey}-${chosen.rank}-${stop.poi_id}`} style={{ marginBottom: '8px' }}>
                          <p style={{ margin: 0 }}><b>{stop.sequence}. {stop.name}</b></p>
                          <p style={{ margin: 0, color: '#475569' }}>
                            {(stop.nearby_suggestions || []).length
                              ? stop.nearby_suggestions.map((n) => `${n.name} (${n.distance_km} km, WPI ${n.wpi})`).join(' | ')
                              : 'No nearby suggestions in this day cluster'}
                          </p>
                        </div>
                      ))}
                    </div>
                    {chosen.map && <iframe src={mapUrl(chosen.map)} title={`${dayKey}-map-rank-${chosen.rank}`} />}
                  </>
                ) : null
              })()}
            </div>
          ))}
        </>
      )}
    </div>
  )
}
