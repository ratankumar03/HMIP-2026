// File Location: frontend/src/components/Map/LiveMap.jsx

import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import useWebSocket from '../../hooks/useWebSocket';

const LiveMap = ({ permissionId, autoUpdate, showPredictions }) => {
  const [location, setLocation] = useState(null);
  const { sendMessage, lastMessage } = useWebSocket('ws://localhost:8000/ws/location/');

  useEffect(() => {
    if (lastMessage) {
      const data = JSON.parse(lastMessage.data);
      setLocation({
        lat: data.latitude,
        lng: data.longitude
      });
    }
  }, [lastMessage]);

  if (!location) {
    return <div>Loading map...</div>;
  }

  return (
    <MapContainer 
      center={[location.lat, location.lng]} 
      zoom={13} 
      style={{ height: '100vh', width: '100%' }}
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; OpenStreetMap contributors'
      />
      <Marker position={[location.lat, location.lng]}>
        <Popup>Current Location</Popup>
      </Marker>
    </MapContainer>
  );
};

export default LiveMap;