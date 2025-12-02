import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { toast } from 'react-toastify';
import '../../styles/Auth.css';
import authService from '../../services/auth.service';

const Login = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    phone: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [useOTP, setUseOTP] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handlePasswordLogin = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await authService.login(formData.phone, formData.password);
      
      if (response.success) {
        toast.success('Login successful!');
        navigate('/dashboard');
      }
    } catch (error) {
      toast.error(error.response?.data?.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleOTPLogin = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await authService.requestOTP(formData.phone, 'login');
      
      if (response.success) {
        toast.success('OTP sent to your phone');
        navigate('/verify-otp', { state: { phone: formData.phone, purpose: 'login' } });
      }
    } catch (error) {
      toast.error('Failed to send OTP');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h1>🚀 HMIP-2026</h1>
          <p>AI-Powered Location Tracking Platform</p>
        </div>

        <div className="auth-toggle">
          <button
            className={!useOTP ? 'active' : ''}
            onClick={() => setUseOTP(false)}
          >
            Password Login
          </button>
          <button
            className={useOTP ? 'active' : ''}
            onClick={() => setUseOTP(true)}
          >
            OTP Login
          </button>
        </div>

        <form onSubmit={useOTP ? handleOTPLogin : handlePasswordLogin} className="auth-form">
          <div className="form-group">
            <label>📱 Phone Number</label>
            <input
              type="tel"
              name="phone"
              placeholder="Enter your phone number"
              value={formData.phone}
              onChange={handleChange}
              required
              className="form-control"
            />
          </div>

          {!useOTP && (
            <div className="form-group">
              <label>🔒 Password</label>
              <input
                type="password"
                name="password"
                placeholder="Enter your password"
                value={formData.password}
                onChange={handleChange}
                required
                className="form-control"
              />
            </div>
          )}

          <button
            type="submit"
            className="btn btn-primary btn-block"
            disabled={loading}
          >
            {loading ? 'Processing...' : useOTP ? 'Send OTP' : 'Login'}
          </button>
        </form>

        <div className="auth-footer">
          <p>Don't have an account? <Link to="/register">Register here</Link></p>
        </div>
      </div>
    </div>
  );
};

export default Login;