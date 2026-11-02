import React, { useState } from 'react';
import {
  Box, Typography, TextField, Button, Avatar, Grid
} from '@mui/material';
import { Person, Save } from '@mui/icons-material';
import GlassCard from '../components/GlassCard';
import NotificationToast from '../components/NotificationToast';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';

export default function ProfilePage() {
  const { user, userProfile } = useAuth();
  const [name, setName] = useState(userProfile?.name || user?.displayName || '');
  const [orgName, setOrgName] = useState(userProfile?.org_name || '');
  const [saving, setSaving] = useState(false);
  const [toast, setToast] = useState({ open: false, message: '', severity: 'info' });

  const displayName = name || 'Scientist';
  const initials = displayName.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const res = await api.put('/auth/profile', { name, org_name: orgName });
      if (res.data.status === 'ok') {
        setToast({ open: true, message: 'Profile updated!', severity: 'success' });
      }
    } catch (err) {
      setToast({ open: true, message: 'Failed to update profile.', severity: 'error' });
    } finally {
      setSaving(false);
    }
  };

  return (
    <Box maxWidth="sm" sx={{ mx: 'auto' }}>
      <GlassCard title="Scientist Profile" icon={<Person sx={{ color: 'primary.main' }} />}>
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mb: 4 }}>
          <Avatar
            sx={{
              width: 80, height: 80, fontSize: '1.8rem', mb: 2,
              background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
              boxShadow: '0 8px 20px rgba(59,130,246,0.3)',
            }}
          >
            {initials}
          </Avatar>
          <Typography variant="h6" fontWeight={700}>{displayName}</Typography>
          <Typography variant="body2" color="text.secondary">{user?.email}</Typography>
        </Box>

        <form onSubmit={handleSubmit}>
          <Grid container spacing={2.5}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Full Name"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Organization / Laboratory"
                value={orgName}
                onChange={(e) => setOrgName(e.target.value)}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Email Address"
                value={user?.email || ''}
                disabled
              />
            </Grid>
            <Grid item xs={12}>
              <Button
                type="submit"
                variant="contained"
                fullWidth
                startIcon={<Save />}
                disabled={saving}
                sx={{ py: 1.2, borderRadius: '10px' }}
              >
                Update Profile
              </Button>
            </Grid>
          </Grid>
        </form>
      </GlassCard>

      <NotificationToast open={toast.open} message={toast.message} severity={toast.severity} onClose={() => setToast({ ...toast, open: false })} />
    </Box>
  );
}
