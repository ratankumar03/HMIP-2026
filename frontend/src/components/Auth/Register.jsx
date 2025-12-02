import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { toast } from 'react-toastify';
import '../../styles/Auth.css';
import authService from '../../services/auth.service';

const Register = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    phone: '',
    email: '',
    full_name: '',
    password: '',
    password_confirm: '',
    date_of_birth: ''
  });
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (formData.password !== formData.password_confirm) {
      toast.error('Passwords do not match');
      return;
    }

    setLoading(true);

    try {
      const response = await authService.register(formData);
      
      if (response.success) {
        toast.success('Registration successful! Please verify your phone.');
        navigate('/verify-otp', { 
          state: { 
            phone: formData.phone, 
            purpose: 'verification' 
          } 
        });
      }
    } catch (error) {
      toast.error(error.response?.data?.message || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card register-card">
        <div className="auth-header">
          <h1>Create Account</h1>
          <p>Join HMIP-2026 Platform</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label>📱 Phone Number *</label>
            <input
              type="tel"
              name="phone"
              placeholder="Enter phone number"
              value={formData.phone}
              onChange={handleChange}
              required
              className="form-control"
            />
          </div>

          <div className="form-group">
            <label>👤 Full Name *</label>
            <input
              type="text"
              name="full_name"
              placeholder="Enter your full name"
              value={formData.full_name}
              onChange={handleChange}
              required
              className="form-control"
            />
          </div>

          <div className="form-group">
            <label>📧 Email (Optional)</label>
            <input
              type="email"
              name="email"
              placeholder="Enter your email"
              value={formData.email}
              onChange={handleChange}
              className="form-control"
            />
          </div>

          <div className="form-group">
            <label>📅 Date of Birth (Optional)</label>
            <input
              type="date"
              name="date_of_birth"
              value={formData.date_of_birth}
              onChange={handleChange}
              className="form-control"
            />
          </div>

          <div className="form-group">
            <label>🔒 Password *</label>
            <input
              type="password"
              name="password"
              placeholder="Create a password"
              value={formData.password}
              onChange={handleChange}
              required
              minLength="8"
              className="form-control"
            />
          </div>

          <div className="form-group">
            <label>🔒 Confirm Password *</label>
            <input
              type="password"
              name="password_confirm"
              placeholder="Confirm your password"
              value={formData.password_confirm}
              onChange={handleChange}
              required
              className="form-control"
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary btn-block"
            disabled={loading}
          >
            {loading ? 'Creating Account...' : 'Register'}
          </button>
        </form>

        <div className="auth-footer">
          <p>Already have an account? <Link to="/login">Login here</Link></p>
        </div>
      </div>
    </div>
  );
};

export default Register;