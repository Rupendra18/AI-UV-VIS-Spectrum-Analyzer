import React, { useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  Box, Typography, TextField, Button, Alert, Container, Link, CircularProgress, InputAdornment
} from '@mui/material';
import { Email, Science, ArrowBack } from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { glass } from '../theme/theme';

export default function ForgotPasswordPage() {
  const { forgotPassword } = useAuth();
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email) {
      setError('Please enter your email address.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await forgotPassword(email);
      setSuccess(true);
    } catch (err) {
      setError(err.message || 'Failed to send password reset email.');
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
              Reset Password
            </Typography>
            <Typography variant="body2" color="#94a3b8">
              We'll send password recovery instructions to your email
            </Typography>
          </Box>

          {error && <Alert severity="error" sx={{ mb: 3, borderRadius: '12px' }}>{error}</Alert>}
          {success && (
            <Alert severity="success" sx={{ mb: 3, borderRadius: '12px' }}>
              Password reset link sent! Check your inbox.
            </Alert>
          )}

          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="Email Address"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              sx={{ mb: 3 }}
              InputProps={{
                startAdornment: <InputAdornment position="start"><Email sx={{ color: 'text.secondary', fontSize: 20 }} /></InputAdornment>,
              }}
            />

            <Button
              type="submit"
              fullWidth
              variant="contained"
              size="large"
              disabled={loading || success}
              sx={{
                py: 1.4, borderRadius: '12px', fontSize: '1rem',
                background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
              }}
            >
              {loading ? <CircularProgress size={24} color="inherit" /> : 'Send Reset Link'}
            </Button>
          </form>

          <Box sx={{ mt: 3, textAlign: 'center' }}>
            <Link
              component={RouterLink}
              to="/login"
              sx={{ color: 'primary.main', fontWeight: 600, textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: 0.5 }}
            >
              <ArrowBack fontSize="small" /> Back to Sign In
            </Link>
          </Box>
        </Box>
      </Container>
    </Box>
  );
}
