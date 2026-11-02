import React, { useState } from 'react';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import {
  Box, Typography, TextField, Button, Alert, Container, Link, CircularProgress, InputAdornment, IconButton
} from '@mui/material';
import { Email, Lock, Visibility, VisibilityOff, Science } from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { glass } from '../theme/theme';

export default function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      setError('Please fill in all fields.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err) {
      setError(err.message || 'Login failed. Check your email and password.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #0f172a 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        p: 2,
      }}
    >
      <Container maxWidth="xs">
        <Box
          sx={{
            ...glass(0.08),
            p: 4,
            borderRadius: '24px',
            boxShadow: '0 25px 50px rgba(0,0,0,0.4)',
          }}
        >
          {/* Logo Header */}
          <Box sx={{ textCenter: 'center', textAlign: 'center', mb: 3 }}>
            <Box
              sx={{
                width: 54, height: 54, borderRadius: '16px',
                background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
                display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
                boxShadow: '0 8px 20px rgba(59,130,246,0.4)', mb: 2,
              }}
            >
              <Science sx={{ color: 'white', fontSize: 30 }} />
            </Box>
            <Typography variant="h5" fontWeight={800} color="white">
              Welcome Back
            </Typography>
            <Typography variant="body2" color="#94a3b8">
              Sign in to your UV-Vis Spectrum account
            </Typography>
          </Box>

          {error && <Alert severity="error" sx={{ mb: 3, borderRadius: '12px' }}>{error}</Alert>}

          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="Email Address"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              sx={{ mb: 2.5 }}
              InputProps={{
                startAdornment: <InputAdornment position="start"><Email sx={{ color: 'text.secondary', fontSize: 20 }} /></InputAdornment>,
              }}
            />

            <TextField
              fullWidth
              label="Password"
              type={showPassword ? 'text' : 'password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              sx={{ mb: 1.5 }}
              InputProps={{
                startAdornment: <InputAdornment position="start"><Lock sx={{ color: 'text.secondary', fontSize: 20 }} /></InputAdornment>,
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton size="small" onClick={() => setShowPassword(!showPassword)}>
                      {showPassword ? <VisibilityOff fontSize="small" /> : <Visibility fontSize="small" />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />

            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 3 }}>
              <Link component={RouterLink} to="/forgot-password" variant="caption" sx={{ color: 'primary.main', fontWeight: 600, textDecoration: 'none' }}>
                Forgot Password?
              </Link>
            </Box>

            <Button
              type="submit"
              fullWidth
              variant="contained"
              size="large"
              disabled={loading}
              sx={{
                py: 1.4, borderRadius: '12px', fontSize: '1rem',
                background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
              }}
            >
              {loading ? <CircularProgress size={24} color="inherit" /> : 'Sign In'}
            </Button>
          </form>

          <Box sx={{ mt: 3, textAlign: 'center' }}>
            <Typography variant="body2" color="#94a3b8">
              Don't have an account?{' '}
              <Link component={RouterLink} to="/register" sx={{ color: 'primary.main', fontWeight: 700, textDecoration: 'none' }}>
                Register
              </Link>
            </Typography>
          </Box>
        </Box>
      </Container>
    </Box>
  );
}
