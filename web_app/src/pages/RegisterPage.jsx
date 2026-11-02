import React, { useState } from 'react';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import {
  Box, Typography, TextField, Button, Alert, Container, Link, CircularProgress, InputAdornment
} from '@mui/material';
import { Person, Business, Email, Lock, Science } from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { glass } from '../theme/theme';

export default function RegisterPage() {
  const navigate = useNavigate();
  const { register } = useAuth();
  const [name, setName] = useState('');
  const [orgName, setOrgName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name || !orgName || !email || !password) {
      setError('Please fill in all fields.');
      return;
    }
    if (password.length < 6) {
      setError('Password must be at least 6 characters long.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await register(name, orgName, email, password);
      navigate('/dashboard');
    } catch (err) {
      setError(err.message || 'Registration failed. Try a different email.');
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
          <Box sx={{ textAlign: 'center', mb: 3 }}>
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
              Create Account
            </Typography>
            <Typography variant="body2" color="#94a3b8">
              Join the AI Spectrum Intelligence Platform
            </Typography>
          </Box>

          {error && <Alert severity="error" sx={{ mb: 3, borderRadius: '12px' }}>{error}</Alert>}

          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="Scientist Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              sx={{ mb: 2 }}
              InputProps={{
                startAdornment: <InputAdornment position="start"><Person sx={{ color: 'text.secondary', fontSize: 20 }} /></InputAdornment>,
              }}
            />

            <TextField
              fullWidth
              label="Organization / Lab Name"
              value={orgName}
              onChange={(e) => setOrgName(e.target.value)}
              sx={{ mb: 2 }}
              InputProps={{
                startAdornment: <InputAdornment position="start"><Business sx={{ color: 'text.secondary', fontSize: 20 }} /></InputAdornment>,
              }}
            />

            <TextField
              fullWidth
              label="Email Address"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              sx={{ mb: 2 }}
              InputProps={{
                startAdornment: <InputAdornment position="start"><Email sx={{ color: 'text.secondary', fontSize: 20 }} /></InputAdornment>,
              }}
            />

            <TextField
              fullWidth
              label="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              sx={{ mb: 3 }}
              InputProps={{
                startAdornment: <InputAdornment position="start"><Lock sx={{ color: 'text.secondary', fontSize: 20 }} /></InputAdornment>,
              }}
            />

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
              {loading ? <CircularProgress size={24} color="inherit" /> : 'Register Account'}
            </Button>
          </form>

          <Box sx={{ mt: 3, textAlign: 'center' }}>
            <Typography variant="body2" color="#94a3b8">
              Already registered?{' '}
              <Link component={RouterLink} to="/login" sx={{ color: 'primary.main', fontWeight: 700, textDecoration: 'none' }}>
                Sign In
              </Link>
            </Typography>
          </Box>
        </Box>
      </Container>
    </Box>
  );
}
