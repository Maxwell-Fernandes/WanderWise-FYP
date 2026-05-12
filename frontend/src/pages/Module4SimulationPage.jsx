import { useEffect, useState } from 'react'
import { geoapifyAutocomplete, geoapifyReverseGeocode, isWithinGoa } from '../services/geoapify'
import { mapUrl, narrateModule4Day, runModule4 } from '../services/simulationApi'
import ChatPanel from '../components/ChatPanel'

export default function Module4SimulationPage() {
  const [numDays, setNumDays] = useState(4)
  const [travelType, setTravelType] = useState('solo')
  const [travelDistance, setTravelDistance] = useState('more')
  const [hotelQuery, setHotelQuery] = useState('')
  const [hotelSuggestions, setHotelSuggestions] = useState([])
  const [hotelSelection, setHotelSelection] = useState(null)
  const [hotelLoading, setHotelLoading] = useState(false)
  const [hotelError, setHotelError] = useState('')
  const [region, setRegion] = useState('')
  const [useLlmFitnessProfile, setUseLlmFitnessProfile] = useState(false)
  const [useLlmInterests, setUseLlmInterests] = useState(false)
  const [includeGaHistory, setIncludeGaHistory] = useState(false)
  const [useLlmItineraryQa, setUseLlmItineraryQa] = useState(false)
  const [useLlmItineraryRetry, setUseLlmItineraryRetry] = useState(false)
  const [useLlmSecondaryItineraryQa, setUseLlmSecondaryItineraryQa] = useState(false)
  const [populationSize, setPopulationSize] = useState(120)
  const [maxGenerations, setMaxGenerations] = useState(90)
  const [earlyStoppingPatience, setEarlyStoppingPatience] = useState(40)
  const [userPreference, setUserPreference] = useState('I love exploring historical forts and beaches, interested in nature waterfalls, but not interested in nightlife or shopping')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [formError, setFormError] = useState('')
  const [selectedRankByDay, setSelectedRankByDay] = useState({})
  const [selectedSecondaryRankByDay, setSelectedSecondaryRankByDay] = useState({})
  const [narrationByKey, setNarrationByKey] = useState({})
  const [narratingByKey, setNarratingByKey] = useState({})

  useEffect(() => {
    let isActive = true
    const trimmed = hotelQuery.trim()
    const selectionLabel = hotelSelection?.formatted || hotelSelection?.name || ''

    if (!trimmed) {
      setHotelSuggestions([])
      setHotelLoading(false)
      return () => {}
    }

    if (hotelSelection && trimmed === selectionLabel) {
      setHotelSuggestions([])
      setHotelLoading(false)
      return () => {}
    }

    setHotelLoading(true)
    setHotelError('')

    const timer = setTimeout(async () => {
      try {
        const results = await geoapifyAutocomplete(trimmed)
        if (!isActive) return
        setHotelSuggestions(results)
      } catch (err) {
        if (!isActive) return
        setHotelSuggestions([])
        setHotelError('Geoapify search failed. Check the API key and try again.')
      } finally {
        if (isActive) setHotelLoading(false)
      }
    }, 350)

    return () => {
      isActive = false
      clearTimeout(timer)
    }
  }, [hotelQuery, hotelSelection])

  const selectHotel = (item) => {
    setHotelSelection(item)
    setHotelQuery(item.formatted || item.name || '')
    setHotelSuggestions([])
    setHotelError('')
  }

  const clearHotel = () => {
    setHotelSelection(null)
    setHotelQuery('')
    setHotelSuggestions([])
    setHotelError('')
  }

  const useCurrentLocation = () => {
    if (!navigator.geolocation) {
      setHotelError('Geolocation is not supported in this browser.')
      return
    }
    setHotelLoading(true)
    setHotelError('')
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const lat = pos.coords.latitude
        const lon = pos.coords.longitude
        if (!isWithinGoa(lat, lon)) {
          setHotelLoading(false)
          setHotelError('Current location is outside Goa bounds.')
          return
        }
        try {
          const result = await geoapifyReverseGeocode(lat, lon)
          if (result) {
            selectHotel(result)
          } else {
            setHotelError('Reverse geocoding returned no results.')
          }
        } catch (err) {
          setHotelError('Reverse geocoding failed. Check the API key and try again.')
        } finally {
          setHotelLoading(false)
        }
      },
      () => {
        setHotelLoading(false)
        setHotelError('Unable to access your location.')
      },
      { enableHighAccuracy: true, timeout: 10000 }
    )
  }

  const submit = async (e) => {
    e.preventDefault()
    setFormError('')
    const hasHotelSelection = Number.isFinite(hotelSelection?.lat) && Number.isFinite(hotelSelection?.lon)
    if (travelDistance === 'less' && !hasHotelSelection && !region) {
      setFormError('Select a hotel location or choose a region for travel less.')
      return
    }
    setLoading(true)
    const data = await runModule4({
      num_days: Number(numDays),
      travel_type: travelType,
      travel_distance: travelDistance,
      hotel_location: null,
      hotel_address: hasHotelSelection ? (hotelSelection.formatted || hotelSelection.name || null) : null,
      hotel_lat: hasHotelSelection ? hotelSelection.lat : null,
      hotel_lon: hasHotelSelection ? hotelSelection.lon : null,
      region: region || null,
      user_preference: userPreference,
      min_rating: 3.0,
      min_reviews: 1,
      population_size: Number(populationSize),
      max_generations: Number(maxGenerations),
      mutation_rate: 0.2,
      crossover_rate: 0.7,
      early_stopping_patience: Number(earlyStoppingPatience),
      random_state: 42,
      use_osrm: true,
      use_llm_fitness_profile: useLlmFitnessProfile,
      use_llm_interests: useLlmInterests,
      include_ga_history: includeGaHistory,
      use_llm_itinerary_qa: useLlmItineraryQa,
      use_llm_itinerary_retry: useLlmItineraryRetry,
      use_llm_secondary_itinerary_qa: useLlmSecondaryItineraryQa
    })
    setResult(data.data)
    const defaults = {}
    Object.entries(data.data.routes || {}).forEach(([dayKey, dayData]) => {
      defaults[dayKey] = (dayData.alternatives?.[0]?.rank) || 1
    })
    setSelectedRankByDay(defaults)
    const secondaryDefaults = {}
    Object.entries(data.data.routes || {}).forEach(([dayKey, dayData]) => {
      secondaryDefaults[dayKey] = (dayData.secondary_itinerary?.alternatives?.[0]?.rank) || 1
    })
    setSelectedSecondaryRankByDay(secondaryDefaults)
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

  const generateNarration = async (dayData, chosen) => {
    const key = `${dayData.day}-${chosen.rank}`
    setNarratingByKey((prev) => ({ ...prev, [key]: true }))
    try {
      const res = await narrateModule4Day({
        day: Number(dayData.day),
        rank: Number(chosen.rank),
        user_preference: userPreference,
        route: chosen.route || []
      })
      setNarrationByKey((prev) => ({ ...prev, [key]: res.data }))
    } finally {
      setNarratingByKey((prev) => ({ ...prev, [key]: false }))
    }
  }

  const hasHotelSelection = Number.isFinite(hotelSelection?.lat) && Number.isFinite(hotelSelection?.lon)

  const routePlaceNames = result ? (() => {
    const names = new Set()
    Object.values(result.routes || {}).forEach((dayData) => {
      if (!dayData || typeof dayData !== 'object') return
      const recRoute = dayData.recommended_route?.route || dayData.alternatives?.[0]?.route || []
      recRoute.forEach((stop) => {
        if (stop?.name) names.add(stop.name)
      })
    })
    return [...names]
  })() : []

  return (
    <div>
      <form className="card" onSubmit={submit}>
        <h2>Module 4 - Genetic Algorithm Route Optimization</h2>
        <label>Number of Days</label>
        <input type="number" min="1" max="10" value={numDays} onChange={(e) => setNumDays(e.target.value)} />
        <label>Travel type</label>
        <select value={travelType} onChange={(e) => setTravelType(e.target.value)}>
          <option value="solo">Solo</option>
          <option value="duo">Duo</option>
          <option value="couple">Couple</option>
          <option value="friends">Friends</option>
          <option value="group">Group</option>
          <option value="family">Family</option>
        </select>
        <label>Travel distance</label>
        <select value={travelDistance} onChange={(e) => setTravelDistance(e.target.value)}>
          <option value="more">Willing to travel more</option>
          <option value="less">Prefer shorter distances</option>
        </select>
        <label>Hotel location (optional)</label>
        <div style={{ position: 'relative' }}>
          <input
            type="text"
            placeholder="Search for your hotel in Goa"
            value={hotelQuery}
            onChange={(e) => {
              setHotelQuery(e.target.value)
              setHotelSelection(null)
            }}
          />
          {hotelSuggestions.length > 0 && (
            <div
              style={{
                position: 'absolute',
                left: 0,
                right: 0,
                top: '100%',
                background: 'white',
                border: '1px solid #e2e8f0',
                borderRadius: '8px',
                padding: '6px',
                zIndex: 10
              }}
            >
              {hotelSuggestions.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => selectHotel(item)}
                  style={{
                    display: 'block',
                    width: '100%',
                    textAlign: 'left',
                    padding: '6px 8px',
                    background: 'transparent',
                    border: 'none',
                    cursor: 'pointer'
                  }}
                >
                  <div style={{ fontWeight: 600 }}>{item.name || item.formatted}</div>
                  <div style={{ fontSize: '0.85em', color: '#475569' }}>{item.formatted}</div>
                </button>
              ))}
            </div>
          )}
        </div>
        <div style={{ display: 'flex', gap: '8px', marginTop: '8px', alignItems: 'center' }}>
          <button type="button" onClick={useCurrentLocation} disabled={hotelLoading}>
            {hotelLoading ? 'Locating...' : 'Use current location'}
          </button>
          <button type="button" onClick={clearHotel} disabled={hotelLoading || (!hotelQuery && !hotelSelection)}>
            Clear
          </button>
          {hotelSelection && (
            <span style={{ fontSize: '0.85em', color: '#475569' }}>
              Selected: {hotelSelection.formatted || hotelSelection.name}
            </span>
          )}
        </div>
        {hotelError && (
          <p style={{ color: '#b45309', margin: '6px 0 0' }}>{hotelError}</p>
        )}
        {travelDistance === 'less' && !hasHotelSelection && (
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
        {formError && (
          <p style={{ color: '#b91c1c', margin: '6px 0 0' }}>{formError}</p>
        )}
        <label>GA population size</label>
        <input type="number" min="20" max="300" value={populationSize} onChange={(e) => setPopulationSize(e.target.value)} />
        <label>GA max generations</label>
        <input type="number" min="10" max="300" value={maxGenerations} onChange={(e) => setMaxGenerations(e.target.value)} />
        <label>Early stopping patience (gens without improvement)</label>
        <input type="number" min="5" max="200" value={earlyStoppingPatience} onChange={(e) => setEarlyStoppingPatience(e.target.value)} />
        <label>User Preference</label>
        <textarea rows="4" value={userPreference} onChange={(e) => setUserPreference(e.target.value)} />
        <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
          <input
            type="checkbox"
            checked={useLlmFitnessProfile}
            onChange={(e) => setUseLlmFitnessProfile(e.target.checked)}
          />
          Use Groq LLM fitness profile (requires GROQ_API_KEY on server)
        </label>
        <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
          <input
            type="checkbox"
            checked={useLlmInterests}
            onChange={(e) => setUseLlmInterests(e.target.checked)}
          />
          Use Groq for Module 1 interest filtering (candidate POIs)
        </label>
        <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
          <input
            type="checkbox"
            checked={includeGaHistory}
            onChange={(e) => setIncludeGaHistory(e.target.checked)}
          />
          Include GA best-fitness history (rank 1 only; larger JSON)
        </label>
        <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
          <input
            type="checkbox"
            checked={useLlmItineraryQa}
            onChange={(e) => setUseLlmItineraryQa(e.target.checked)}
          />
          Use Groq itinerary QA on rank-1 route per day (GROQ_API_KEY)
        </label>
        <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
          <input
            type="checkbox"
            checked={useLlmItineraryRetry}
            onChange={(e) => setUseLlmItineraryRetry(e.target.checked)}
          />
          If QA fails, one GA retry with stronger wrong-time penalty (requires QA enabled)
        </label>
        <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
          <input
            type="checkbox"
            checked={useLlmSecondaryItineraryQa}
            onChange={(e) => setUseLlmSecondaryItineraryQa(e.target.checked)}
          />
          Use Groq itinerary QA for secondary rank-1 (extra Groq call per day)
        </label>
        <button type="submit" disabled={loading}>{loading ? 'Running...' : 'Simulate Module 4'}</button>
      </form>

      {result && (
        <>
          <div className="card">
            <p><b>Days:</b> {result.num_days}</p>
            <p><b>Travel type:</b> {result.travel_type || travelType}</p>
            <p><b>Travel distance:</b> {result.travel_distance || travelDistance}</p>
            <p><b>Fitness profile source:</b> {result.fitness_profile_source || '—'}</p>
            <p><b>Module 1 interests source:</b> {result.module1_interests_source || '—'}</p>
            {result.preference_extraction && (
              <p style={{ whiteSpace: 'pre-wrap', fontSize: '0.9em' }}>
                <b>Preference extraction:</b> {JSON.stringify(result.preference_extraction, null, 2)}
              </p>
            )}
            <p><b>Module chain:</b> module1_run_id={result.module1_run_id}, module2_run_id={result.module2_run_id}</p>
            {result.module2_radius_filter?.enabled && (
              <div style={{ marginTop: '8px', padding: '10px', background: '#f8fafc', borderRadius: '8px' }}>
                <p style={{ margin: '0 0 4px' }}><b>Travel radius filter</b> ({result.module2_radius_filter.travel_distance || 'less'})</p>
                <p style={{ margin: 0 }}>
                  <b>Radius:</b> {result.module2_radius_filter.radius_km?.toFixed?.(1)} km (base {result.module2_radius_filter.base_radius_km} · max {result.module2_radius_filter.max_radius_km})
                </p>
                <p style={{ margin: 0 }}>
                  <b>Anchor:</b> {result.module2_radius_filter.anchor?.label || 'dataset mean'} ({result.module2_radius_filter.anchor?.source || 'dataset_mean'})
                </p>
                <p style={{ margin: 0 }}>
                  <b>Within radius:</b> {result.module2_radius_filter.within_radius} · <b>Exceptions:</b> {result.module2_radius_filter.exceptions_added}
                </p>
                {result.module2_radius_filter.anchor_warning && (
                  <p style={{ margin: 0, color: '#92400e' }}>
                    <b>Anchor warning:</b> {result.module2_radius_filter.anchor_warning}
                  </p>
                )}
                {result.module2_radius_filter.fallback_reason && (
                  <p style={{ margin: 0, color: '#92400e' }}>
                    <b>Fallback:</b> {result.module2_radius_filter.fallback_reason}
                  </p>
                )}
              </div>
            )}
            <p><b>Generated:</b> {result.generated_files.optimized_routes}</p>
          </div>
          {Object.entries(result.routes).map(([dayKey, dayData]) => (
            <div className="card" key={dayKey}>
              <h3>{dayKey} - Top Alternatives</h3>
              {dayData.itinerary_qa && (
                <div style={{ marginBottom: '12px', padding: '10px', background: '#f0fdf4', borderRadius: '8px', fontSize: '0.9em' }}>
                  <p style={{ margin: '0 0 6px' }}><b>Itinerary QA</b> ({dayData.itinerary_qa.source}){dayData.itinerary_retry_attempted ? ' · retried GA once' : ''}</p>
                  <p style={{ margin: 0 }}><b>OK:</b> {String(dayData.itinerary_qa.ok)} — {dayData.itinerary_qa.summary}</p>
                  {(dayData.itinerary_qa.problematic_places || []).length > 0 && (
                    <p style={{ margin: '6px 0 0', color: '#166534' }}>
                      <b>Flagged for replan:</b>{' '}
                      {(dayData.itinerary_qa.problematic_places || [])
                        .map((x) => (typeof x === 'object' && x !== null ? (x.name || '') : String(x)))
                        .filter(Boolean)
                        .join('; ')}
                    </p>
                  )}
                  {dayData.itinerary_retry_details && (
                    <p style={{ margin: '6px 0 0', color: '#14532d', fontSize: '0.85em' }}>
                      <b>Retry:</b> {dayData.itinerary_retry_details.strategy}
                      {Array.isArray(dayData.itinerary_retry_details.resolved_flagged_places) && dayData.itinerary_retry_details.resolved_flagged_places.length > 0 && (
                        <> — resolved {dayData.itinerary_retry_details.resolved_flagged_places.map((r) => r.matched_name || r.place_id).join(', ')}</>
                      )}
                    </p>
                  )}
                  {(dayData.itinerary_qa.issues || []).length > 0 && (
                    <ul style={{ margin: '6px 0 0', paddingLeft: '1.2rem' }}>
                      {dayData.itinerary_qa.issues.map((issue, i) => (
                        <li key={i}>{issue}</li>
                      ))}
                    </ul>
                  )}
                </div>
              )}
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
              {(dayData.secondary_itinerary?.alternatives || []).length > 0 && (
                <div style={{ display: 'flex', gap: '8px', marginBottom: '12px', flexWrap: 'wrap' }}>
                  {(dayData.secondary_itinerary.alternatives || []).map((alt) => (
                    <button
                      type="button"
                      key={`sec-${alt.rank}`}
                      onClick={() => setSelectedSecondaryRankByDay((prev) => ({ ...prev, [dayKey]: alt.rank }))}
                      style={{ width: 'auto', background: selectedSecondaryRankByDay[dayKey] === alt.rank ? '#1d4ed8' : '#64748b' }}
                    >
                      Secondary Rank {alt.rank}
                    </button>
                  ))}
                </div>
              )}
              {(dayData.alternatives || []).map((alt) => (
                <p key={`s-${alt.rank}`}>
                  Rank {alt.rank}: fitness={alt.fitness_score?.toFixed?.(6)} | POIs={alt.route?.length || 0}
                  {alt.exclusive_must_visit_name && (
                    <> | Must-visit: {alt.exclusive_must_visit_name}</>
                  )}
                </p>
              ))}
              {(dayData.secondary_itinerary?.alternatives || []).map((alt) => (
                <p key={`s2-${alt.rank}`}>
                  Secondary Rank {alt.rank}: fitness={alt.fitness_score?.toFixed?.(6)} | POIs={alt.route?.length || 0}
                  {alt.exclusive_must_visit_name && (
                    <> | Must-visit: {alt.exclusive_must_visit_name}</>
                  )}
                </p>
              ))}
              {(() => {
                const chosen = (dayData.alternatives || []).find((x) => x.rank === selectedRankByDay[dayKey]) || dayData.alternatives?.[0]
                const rank1 = (dayData.alternatives || []).find((x) => x.rank === 1) || dayData.alternatives?.[0]
                const diffPct = routeSetDiffPercent(rank1?.route || [], chosen?.route || [])
                const key = `${dayData.day}-${chosen?.rank || 1}`
                const narration = narrationByKey[key]
                const narrating = narratingByKey[key]
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
                      {chosen.exclusive_must_visit_name && (
                        <p>
                          <b>Exclusive must-visit:</b> {chosen.exclusive_must_visit_name}
                        </p>
                      )}
                    </div>
                    {chosen.fitness_breakdown && (
                      <details style={{ marginBottom: '12px', padding: '10px', background: '#f8fafc', borderRadius: '8px' }}>
                        <summary style={{ cursor: 'pointer', fontWeight: 600 }}>Fitness breakdown (formula: {chosen.fitness_breakdown.formula})</summary>
                        <p style={{ margin: '8px 0 4px', fontSize: '0.9em' }}>
                          <b>fitness</b> = total_reward / (1 + delta) →{' '}
                          {chosen.fitness_breakdown.fitness?.toFixed?.(6)} = {chosen.fitness_breakdown.total_reward?.toFixed?.(4)} / (1 + {chosen.fitness_breakdown.delta?.toFixed?.(4)})
                        </p>
                        {Array.isArray(chosen.ga_convergence) && chosen.ga_convergence.length > 0 && (
                          <p style={{ margin: '0 0 8px', fontSize: '0.85em', color: '#475569' }}>
                            <b>GA best fitness trace</b> (gen 0…{chosen.ga_convergence.length - 1}):{' '}
                            {chosen.ga_convergence.slice(0, 6).map((x) => Number(x).toFixed(4)).join(' → ')}
                            {chosen.ga_convergence.length > 6 ? ' …' : ''}
                          </p>
                        )}
                        <pre style={{ margin: 0, fontSize: '0.75rem', overflow: 'auto', maxHeight: '240px' }}>
                          {JSON.stringify({ weights: chosen.fitness_breakdown.weights, raw_components: chosen.fitness_breakdown.raw_components }, null, 2)}
                        </pre>
                      </details>
                    )}
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
                    <div style={{ marginBottom: '12px' }}>
                      <button type="button" onClick={() => generateNarration(dayData, chosen)} disabled={narrating}>
                        {narrating ? 'Generating narration...' : 'Generate Day Narration'}
                      </button>
                    </div>
                    {narration && (
                      <div style={{ background: '#eef2ff', padding: '12px', borderRadius: '8px', marginBottom: '12px' }}>
                        <p><b>AI Day Narration</b> ({narration.provider})</p>
                        <p style={{ whiteSpace: 'pre-wrap' }}>{narration.narration_text}</p>
                      </div>
                    )}
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
              {(() => {
                const secondary = dayData.secondary_itinerary
                if (!secondary || !(secondary.alternatives || []).length) return null
                const secondaryChosen = (secondary.alternatives || []).find((x) => x.rank === selectedSecondaryRankByDay[dayKey]) || secondary.alternatives?.[0]
                const primaryRank1 = (dayData.alternatives || []).find((x) => x.rank === 1) || dayData.alternatives?.[0]
                const secondaryDiffPct = routeSetDiffPercent(primaryRank1?.route || [], secondaryChosen?.route || [])
                const secondaryQa = secondary.itinerary_qa
                return secondaryChosen ? (
                  <>
                    <div style={{ background: '#f1f5f9', padding: '12px', borderRadius: '8px', marginBottom: '10px' }}>
                      <p><b>SECONDARY ITINERARY — Rank {secondaryChosen.rank}</b></p>
                      <p>
                        <b>Fitness:</b> {secondaryChosen.fitness_score?.toFixed?.(3)} |{' '}
                        <b>POI Value:</b> {secondaryChosen.poi_value_sum?.toFixed?.(3)} |{' '}
                        <b>Travel:</b> {secondaryChosen.total_distance_km?.toFixed?.(1)} km ({secondaryChosen.total_travel_time_min?.toFixed?.(0)} min) |{' '}
                        <b>Time:</b> {(secondaryChosen.total_time_hours || (secondaryChosen.total_time_min ? secondaryChosen.total_time_min / 60 : null))?.toFixed?.(2)} hours
                      </p>
                      <p>
                        <b>Difference vs Primary Rank 1:</b> {secondaryDiffPct.toFixed(1)}% |{' '}
                        <b>Disjoint from primary:</b> {String(secondary.disjoint_from_primary)}
                      </p>
                      {secondaryChosen.exclusive_must_visit_name && (
                        <p>
                          <b>Exclusive must-visit:</b> {secondaryChosen.exclusive_must_visit_name}
                        </p>
                      )}
                    </div>
                    {secondaryQa && (
                      <div style={{ marginBottom: '12px', padding: '10px', background: '#f0fdf4', borderRadius: '8px', fontSize: '0.9em' }}>
                        <p style={{ margin: '0 0 6px' }}><b>Secondary Itinerary QA</b> ({secondaryQa.source || 'groq'})</p>
                        <p style={{ margin: 0 }}><b>OK:</b> {String(secondaryQa.ok)} — {secondaryQa.summary}</p>
                        {(secondaryQa.problematic_places || []).length > 0 && (
                          <p style={{ margin: '6px 0 0', color: '#166534' }}>
                            <b>Flagged for replan:</b>{' '}
                            {(secondaryQa.problematic_places || [])
                              .map((x) => (typeof x === 'object' && x !== null ? (x.name || '') : String(x)))
                              .filter(Boolean)
                              .join('; ')}
                          </p>
                        )}
                        {(secondaryQa.issues || []).length > 0 && (
                          <ul style={{ margin: '6px 0 0', paddingLeft: '1.2rem' }}>
                            {secondaryQa.issues.map((issue, i) => (
                              <li key={i}>{issue}</li>
                            ))}
                          </ul>
                        )}
                      </div>
                    )}
                    {secondaryChosen.fitness_breakdown && (
                      <details style={{ marginBottom: '12px', padding: '10px', background: '#f8fafc', borderRadius: '8px' }}>
                        <summary style={{ cursor: 'pointer', fontWeight: 600 }}>Secondary fitness breakdown (formula: {secondaryChosen.fitness_breakdown.formula})</summary>
                        <p style={{ margin: '8px 0 4px', fontSize: '0.9em' }}>
                          <b>fitness</b> = total_reward / (1 + delta) →{' '}
                          {secondaryChosen.fitness_breakdown.fitness?.toFixed?.(6)} = {secondaryChosen.fitness_breakdown.total_reward?.toFixed?.(4)} / (1 + {secondaryChosen.fitness_breakdown.delta?.toFixed?.(4)})
                        </p>
                        {Array.isArray(secondaryChosen.ga_convergence) && secondaryChosen.ga_convergence.length > 0 && (
                          <p style={{ margin: '0 0 8px', fontSize: '0.85em', color: '#475569' }}>
                            <b>GA best fitness trace</b> (gen 0…{secondaryChosen.ga_convergence.length - 1}):{' '}
                            {secondaryChosen.ga_convergence.slice(0, 6).map((x) => Number(x).toFixed(4)).join(' → ')}
                            {secondaryChosen.ga_convergence.length > 6 ? ' …' : ''}
                          </p>
                        )}
                        <pre style={{ margin: 0, fontSize: '0.75rem', overflow: 'auto', maxHeight: '240px' }}>
                          {JSON.stringify({ weights: secondaryChosen.fitness_breakdown.weights, raw_components: secondaryChosen.fitness_breakdown.raw_components }, null, 2)}
                        </pre>
                      </details>
                    )}
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
                          {(secondaryChosen.route || []).map((stop, idx) => (
                            <tr key={`s-${dayKey}-${secondaryChosen.rank}-${stop.sequence}`}>
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
                      <p><b>Nearby Places You Can Also Consider (secondary)</b></p>
                      {(secondaryChosen.route || []).map((stop) => (
                        <div key={`n2-${dayKey}-${secondaryChosen.rank}-${stop.poi_id}`} style={{ marginBottom: '8px' }}>
                          <p style={{ margin: 0 }}><b>{stop.sequence}. {stop.name}</b></p>
                          <p style={{ margin: 0, color: '#475569' }}>
                            {(stop.nearby_suggestions || []).length
                              ? stop.nearby_suggestions.map((n) => `${n.name} (${n.distance_km} km, WPI ${n.wpi})`).join(' | ')
                              : 'No nearby suggestions in this day cluster'}
                          </p>
                        </div>
                      ))}
                    </div>
                    {secondaryChosen.map && <iframe src={mapUrl(secondaryChosen.map)} title={`${dayKey}-secondary-map-rank-${secondaryChosen.rank}`} />}
                  </>
                ) : null
              })()}
            </div>
          ))}
        </>
      )}
      <ChatPanel placeNames={routePlaceNames} />
    </div>
  )
}
