import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { toast } from 'react-toastify';
import '../../styles/Auth.css';
import authService from '../../services/auth.service';

const OTPVerification = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { phone, purpose } = location.state || {};

  const [otp, setOtp] = useState(['', '', '', '', '', '']);
  const [loading, setLoading] = useState(false);
  const [timer, setTimer] = useState(600); // 10 minutes

  useEffect(() => {
    if (!phone || !purpose) {
      navigate('/login');
    }

    const interval = setInterval(() => {
      setTimer((prev) => (prev > 0 ? prev - 1 : 0));
    }, 1000);

    return () => clearInterval(interval);
  }, [phone, purpose, navigate]);

  const handleChange = (index, value) => {
    if (value.length > 1) return;
    
    const newOtp = [...otp];
    newOtp[index] = value;
    setOtp(newOtp);

    // Auto-focus next input
    if (value && index < 5) {
      document.getElementById(`otp-${index + 1}`)?.focus();
    }
  };

  const handleKeyDown = (index, e) => {
    if (e.key === 'Backspace' && !otp[index] && index > 0) {
      document.getElementById(`otp-${index - 1}`)?.focus();
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const otpCode = otp.join('');

    if (otpCode.length !== 6) {
      toast.error('Please enter complete OTP');
      return;
    }

    setLoading(true);

    try {
      const response = await authService.verifyOTP(phone, otpCode, purpose);
      
      if (response.success) {
        toast.success('Verification successful!');
        
        if (purpose === 'login') {
          navigate('/dashboard');
        } else {
          navigate('/login');
        }
      }
    } catch (error) {
      toast.error('Invalid OTP');
      setOtp(['', '', '', '', '', '']);
    } finally {
      setLoading(false);
    }
  };

  const handleResend = async () => {
    try {
      await authService.requestOTP(phone, purpose);
      toast.success('New OTP sent');
      setTimer(600);
      setOtp(['', '', '', '', '', '']);
    } catch (error) {
      toast.error('Failed to resend OTP');
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="auth-container">
      <div className="auth-card otp-card">
        <div className="auth-header">
          <h1>Verify OTP</h1>
          <p>Enter the 6-digit code sent to</p>
          <strong>{phone}</strong>
        </div>

        <form onSubmit={handleSubmit} className="otp-form">
          <div className="otp-inputs">
            {otp.map((digit, index) => (
              <input
                key={index}
                id={`otp-${index}`}
                type="text"
                maxLength="1"
                value={digit}
                onChange={(e) => handleChange(index, e.target.value)}
                onKeyDown={(e) => handleKeyDown(index, e)}
                className="otp-input"
                autoFocus={index === 0}
              />
            ))}
          </div>

          <div className="otp-timer">
            ⏱️ Time remaining: <strong>{formatTime(timer)}</strong>
          </div>

          <button
            type="submit"
            className="btn btn-primary btn-block"
            disabled={loading || timer === 0}
          >
            {loading ? 'Verifying...' : 'Verify OTP'}
          </button>

          <button
            type="button"
            className="btn btn-secondary btn-block"
            onClick={handleResend}
            disabled={timer > 0}
          >
            Resend OTP
          </button>
        </form>
      </div>
    </div>
  );
};

export default OTPVerification;