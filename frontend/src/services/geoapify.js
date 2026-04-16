const GEOAPIFY_BASE = 'https://api.geoapify.com/v1/geocode'
const GEOAPIFY_KEY = import.meta.env.VITE_GEOAPIFY_API_KEY

const GOA_BOUNDS = {
  minLat: 14.8,
  maxLat: 15.9,
  minLon: 73.6,
  maxLon: 74.4
}

function requireKey() {
  if (!GEOAPIFY_KEY) {
    throw new Error('Missing VITE_GEOAPIFY_API_KEY')
  }
}

function buildRectFilter(bounds = GOA_BOUNDS) {
  return `rect:${bounds.minLon},${bounds.minLat},${bounds.maxLon},${bounds.maxLat}`
}

function normalizeAutocompleteResults(payload) {
  if (!payload) return []
  if (Array.isArray(payload.results)) {
    return payload.results.map((item, idx) => ({
      id: item.place_id || `${item.formatted}-${idx}`,
      formatted: item.formatted || item.address_line1 || item.address_line2 || '',
      name: item.name || '',
      lat: Number(item.lat),
      lon: Number(item.lon),
      city: item.city || '',
      country: item.country || '',
      raw: item
    }))
  }

  if (Array.isArray(payload.features)) {
    return payload.features.map((feature, idx) => {
      const props = feature.properties || {}
      return {
        id: props.place_id || feature.id || `${props.formatted}-${idx}`,
        formatted: props.formatted || props.name || '',
        name: props.name || '',
        lat: Number(props.lat ?? feature.geometry?.coordinates?.[1]),
        lon: Number(props.lon ?? feature.geometry?.coordinates?.[0]),
        city: props.city || '',
        country: props.country || '',
        raw: props
      }
    })
  }

  return []
}

export async function geoapifyAutocomplete(query, options = {}) {
  const text = String(query || '').trim()
  if (!text) return []
  requireKey()

  const params = new URLSearchParams({
    text,
    apiKey: GEOAPIFY_KEY,
    limit: String(options.limit || 6),
    format: 'json',
    filter: buildRectFilter(),
    bias: buildRectFilter()
  })

  const res = await fetch(`${GEOAPIFY_BASE}/autocomplete?${params.toString()}`)
  if (!res.ok) {
    throw new Error('Geoapify autocomplete failed')
  }
  const data = await res.json()
  return normalizeAutocompleteResults(data)
}

export async function geoapifyReverseGeocode(lat, lon) {
  requireKey()
  const params = new URLSearchParams({
    lat: String(lat),
    lon: String(lon),
    apiKey: GEOAPIFY_KEY,
    format: 'json'
  })
  const res = await fetch(`${GEOAPIFY_BASE}/reverse?${params.toString()}`)
  if (!res.ok) {
    throw new Error('Geoapify reverse geocoding failed')
  }
  const data = await res.json()
  const results = normalizeAutocompleteResults(data)
  return results[0] || null
}

export function isWithinGoa(lat, lon) {
  const latNum = Number(lat)
  const lonNum = Number(lon)
  if (!Number.isFinite(latNum) || !Number.isFinite(lonNum)) return false
  return (
    latNum >= GOA_BOUNDS.minLat &&
    latNum <= GOA_BOUNDS.maxLat &&
    lonNum >= GOA_BOUNDS.minLon &&
    lonNum <= GOA_BOUNDS.maxLon
  )
}
