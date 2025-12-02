// 🚀 Main React Application Component
// File Location: frontend/src/App.jsx

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import './styles/App.css';

// Context Providers
import { AuthProvider } from './context/AuthContext';
import { LocationProvider } from './context/LocationContext';
import { NotificationProvider } from './context/NotificationContext';

// Components
import Login from './components/Auth/Login';
import Register from './components/Auth/Register';
import OTPVerification from './components/Auth/OTPVerification';
import Dashboard from './components/Dashboard/Dashboard';
import TrackRequest from './components/Tracking/TrackRequest';
import ActiveTracking from './components/Tracking/ActiveTracking';
import PermissionModal from './components/Tracking/PermissionModal';
import LiveMap from './components/Map/LiveMap';
import UserProfile from './components/Dashboard/UserProfile';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem('access_token');
  
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
};

// Public Route Component (redirect if authenticated)
const PublicRoute = ({ children }) => {
  const token = localStorage.getItem('access_token');
  
  if (token) {
    return <Navigate to="/dashboard" replace />;
  }
  
  return children;
};

function App() {
  return (
    <Router>
      <AuthProvider>
        <LocationProvider>
          <NotificationProvider>
            <div className="App">
              {/* Toast Notifications */}
              <ToastContainer
                position="top-right"
                autoClose={3000}
                hideProgressBar={false}
                newestOnTop
                closeOnClick
                rtl={false}
                pauseOnFocusLoss
                draggable
                pauseOnHover
                theme="light"
              />

              {/* Application Routes */}
              <Routes>
                {/* Public Routes */}
                <Route
                  path="/"
                  element={
                    <PublicRoute>
                      <Navigate to="/login" replace />
                    </PublicRoute>
                  }
                />
                
                <Route
                  path="/login"
                  element={
                    <PublicRoute>
                      <Login />
                    </PublicRoute>
                  }
                />
                
                <Route
                  path="/register"
                  element={
                    <PublicRoute>
                      <Register />
                    </PublicRoute>
                  }
                />
                
                <Route
                  path="/verify-otp"
                  element={
                    <PublicRoute>
                      <OTPVerification />
                    </PublicRoute>
                  }
                />

                {/* Protected Routes */}
                <Route
                  path="/dashboard"
                  element={
                    <ProtectedRoute>
                      <Dashboard />
                    </ProtectedRoute>
                  }
                />
                
                <Route
                  path="/track-request"
                  element={
                    <ProtectedRoute>
                      <TrackRequest />
                    </ProtectedRoute>
                  }
                />
                
                <Route
                  path="/active-tracking"
                  element={
                    <ProtectedRoute>
                      <ActiveTracking />
                    </ProtectedRoute>
                  }
                />
                
                <Route
                  path="/map/:permissionId"
                  element={
                    <ProtectedRoute>
                      <LiveMap />
                    </ProtectedRoute>
                  }
                />
                
                <Route
                  path="/profile"
                  element={
                    <ProtectedRoute>
                      <UserProfile />
                    </ProtectedRoute>
                  }
                />
                
                <Route
                  path="/permission-response/:permissionId"
                  element={
                    <ProtectedRoute>
                      <PermissionModal />
                    </ProtectedRoute>
                  }
                />

                {/* 404 Route */}
                <Route path="*" element={<Navigate to="/dashboard" replace />} />
              </Routes>
            </div>
          </NotificationProvider>
        </LocationProvider>
      </AuthProvider>
    </Router>
  );
}

export default App;