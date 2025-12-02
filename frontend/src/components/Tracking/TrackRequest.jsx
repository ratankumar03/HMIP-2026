// File Location: frontend/src/components/Tracking/TrackRequest.jsx

import React, { useState } from 'react';
import { toast } from 'react-toastify';
import permissionService from '../../services/permission.service';

const TrackRequest = () => {
  const [formData, setFormData] = useState({
    target_phone: '',
    purpose: '',
    duration_hours: 24
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await permissionService.requestPermission(formData);
      if (response.success) {
        toast.success('Permission request sent!');
      }
    } catch (error) {
      toast.error('Failed to send request');
    }
  };

  return (
    <div className="track-request">
      <h2>Request Location Tracking</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="tel"
          placeholder="Target Phone Number"
          value={formData.target_phone}
          onChange={(e) => setFormData({...formData, target_phone: e.target.value})}
          required
        />
        <textarea
          placeholder="Purpose of tracking"
          value={formData.purpose}
          onChange={(e) => setFormData({...formData, purpose: e.target.value})}
        />
        <button type="submit">Send Request</button>
      </form>
    </div>
  );
};

export default TrackRequest;