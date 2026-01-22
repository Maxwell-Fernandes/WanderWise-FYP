import { useEffect, useRef, useState } from 'react';
import { Box, Paper, Typography } from '@mui/material';
import Map, { Marker, Popup } from 'react-map-gl';
import { LocationOn } from '@mui/icons-material';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';

const InteractiveMap = ({ pois = [], clusters = [], selectedDay = null }) => {
  const mapRef = useRef();

  // Default view (Goa, India)
  const [viewport, setViewport] = useState({
    latitude: 15.2993,
    longitude: 74.124,
    zoom: 10,
  });

  const [selectedPOI, setSelectedPOI] = useState(null);

  // Colors for different day clusters
  const CLUSTER_COLORS = [
    '#FF6B6B', // Red
    '#4ECDC4', // Teal
    '#45B7D1', // Blue
    '#FFA07A', // Orange
    '#98D8C8', // Mint
    '#F7DC6F', // Yellow
    '#BB8FCE', // Purple
  ];

  // Fit map to show all POIs
  useEffect(() => {
    if (pois.length > 0 && mapRef.current) {
      const bounds = pois.reduce(
        (bounds, poi) => {
          return bounds.extend([poi.longitude, poi.latitude]);
        },
        new maplibregl.LngLatBounds([pois[0].longitude, pois[0].latitude], [pois[0].longitude, pois[0].latitude])
      );

      mapRef.current.fitBounds(bounds, {
        padding: 50,
        duration: 1000,
      });
    }
  }, [pois]);

  // Filter POIs by selected day if clusters are provided
  const displayPOIs = selectedDay !== null && clusters.length > 0
    ? pois.filter(poi => poi.cluster_label === selectedDay)
    : pois;

  return (
    <Paper elevation={3} sx={{ height: '500px', overflow: 'hidden' }}>
      <Map
        ref={mapRef}
        {...viewport}
        onMove={(evt) => setViewport(evt.viewState)}
        mapStyle="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
        style={{ width: '100%', height: '100%' }}
      >
        {/* POI Markers */}
        {displayPOIs.map((poi, index) => (
          <Marker
            key={poi.id || index}
            latitude={poi.latitude}
            longitude={poi.longitude}
            anchor="bottom"
            onClick={(e) => {
              e.originalEvent.stopPropagation();
              setSelectedPOI(poi);
            }}
          >
            <Box
              sx={{
                cursor: 'pointer',
                color: poi.cluster_label !== undefined
                  ? CLUSTER_COLORS[poi.cluster_label % CLUSTER_COLORS.length]
                  : '#FF6B6B',
                fontSize: '32px',
                filter: 'drop-shadow(0px 2px 4px rgba(0,0,0,0.3))',
                '&:hover': {
                  transform: 'scale(1.2)',
                },
                transition: 'transform 0.2s',
              }}
            >
              <LocationOn fontSize="inherit" />
            </Box>
          </Marker>
        ))}

        {/* Popup for selected POI */}
        {selectedPOI && (
          <Popup
            latitude={selectedPOI.latitude}
            longitude={selectedPOI.longitude}
            onClose={() => setSelectedPOI(null)}
            closeButton={true}
            closeOnClick={false}
            offsetTop={-30}
          >
            <Box sx={{ p: 1 }}>
              <Typography variant="subtitle1" fontWeight="bold">
                {selectedPOI.name}
              </Typography>
              {selectedPOI.category && (
                <Typography variant="body2" color="text.secondary">
                  {selectedPOI.category}
                </Typography>
              )}
              {selectedPOI.popularity_score && (
                <Typography variant="caption">
                  Rating: {selectedPOI.popularity_score}/10
                </Typography>
              )}
            </Box>
          </Popup>
        )}
      </Map>
    </Paper>
  );
};

export default InteractiveMap;
