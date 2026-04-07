# OSRM API Reference

Base URL: `http://localhost:5000`

---

## 1. Route API — Get directions
```bash
curl "http://localhost:5000/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?steps=true"
```
**Example (Panaji to Margao):**
```bash
curl "http://localhost:5000/route/v1/driving/73.8278,15.4989;73.9557,15.2993?steps=true&overview=full&geometries=geojson"
```

---

## 2. Nearest API — Snap to nearest road
```bash
curl "http://localhost:5000/nearest/v1/driving/{lon},{lat}?number=3"
```
**Example:**
```bash
curl "http://localhost:5000/nearest/v1/driving/73.8278,15.4989?number=3"
```

---

## 3. Table API — Duration/Distance matrix
```bash
curl "http://localhost:5000/table/v1/driving/{lon1},{lat1};{lon2},{lat2};{lon3},{lat3}?annotations=duration,distance"
```
**Example:**
```bash
curl "http://localhost:5000/table/v1/driving/73.8278,15.4989;73.9557,15.2993;74.0134,15.5524?annotations=duration,distance"
```

---

## 4. Trip API — Optimal visit order (TSP)
```bash
curl "http://localhost:5000/trip/v1/driving/{lon1},{lat1};{lon2},{lat2};{lon3},{lat3}?roundtrip=true"
```
**Example:**
```bash
curl "http://localhost:5000/trip/v1/driving/73.8278,15.4989;73.9557,15.2993;74.0134,15.5524?roundtrip=true&steps=true"
```

---

## 5. Match API — Snap GPS trace to roads
```bash
curl "http://localhost:5000/match/v1/driving/{lon1},{lat1};{lon2},{lat2};{lon3},{lat3}?geometries=geojson"
```
**Example:**
```bash
curl "http://localhost:5000/match/v1/driving/73.8278,15.4989;73.8300,15.5000;73.8350,15.5020?geometries=geojson"
```

---

## 6. Tile API — Vector map tiles
```bash
curl "http://localhost:5000/tile/v1/car/tile({x},{y},{zoom}).mvt"
```

---

## Common Query Parameters

| Parameter | Options | Description |
|---|---|---|
| `steps` | `true/false` | Turn-by-turn instructions |
| `geometries` | `geojson`, `polyline` | Route shape format |
| `overview` | `full`, `simplified`, `false` | Route geometry detail |
| `alternatives` | `true/false` | Get alternative routes |
| `annotations` | `duration`, `distance`, `speed` | Extra per-segment data |

---

## Notes
- All coordinates are in **longitude, latitude** order
- Default profile: `driving`
- Other profiles: `bicycle`, `foot`