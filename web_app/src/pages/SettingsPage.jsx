import React, { useState, useEffect } from 'react';
import {
  Box, Typography, TextField, Button, Grid, Slider, Alert
} from '@mui/material';
import { Settings, Save, Restore } from '@mui/icons-material';
import GlassCard from '../components/GlassCard';
import LoadingSpinner from '../components/LoadingSpinner';
import NotificationToast from '../components/NotificationToast';
import api from '../services/api';

export default function SettingsPage() {
  const [settings, setSettings] = useState({
    org_name: '',
    scientist_name: '',
    safe_limit: 5.0,
    concentration_factor: 12.5,
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [toast, setToast] = useState({ open: false, message: '', severity: 'info' });

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    setLoading(true);
    try {
      const res = await api.get('/settings');
      if (res.data.status === 'success') {
        setSettings(res.data.settings || {});
      }
    } catch (err) {
      console.error('Failed to load settings:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const res = await api.post('/settings', settings);
      if (res.data.status === 'success') {
        setToast({ open: true, message: 'Settings saved successfully!', severity: 'success' });
      }
    } catch (err) {
      setToast({ open: true, message: 'Failed to save settings.', severity: 'error' });
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <LoadingSpinner message="Loading Settings..." />;

  return (
    <Box maxWidth="md" sx={{ mx: 'auto' }}>
      <Typography variant="h5" fontWeight={800} sx={{ mb: 1 }}>
        Application Settings & Thresholds
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 4 }}>
        Configure laboratory defaults, scientist metadata for PDF reports, and contamination risk limit values.
      </Typography>

      <form onSubmit={handleSave}>
        <Grid container spacing={3}>
          {/* Organization & Scientist */}
          <Grid item xs={12}>
            <GlassCard title="Report Metadata" icon={<Settings sx={{ color: 'primary.main' }} />}>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Organization / Laboratory Name"
                    value={settings.org_name || ''}
                    onChange={(e) => setSettings({ ...settings, org_name: e.target.value })}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Lead Scientist Name"
                    value={settings.scientist_name || ''}
                    onChange={(e) => setSettings({ ...settings, scientist_name: e.target.value })}
                  />
                </Grid>
              </Grid>
            </GlassCard>
          </Grid>

          {/* Safe Limit Threshold */}
          <Grid item xs={12}>
            <GlassCard title="Contamination Risk Thresholds" icon={<Settings sx={{ color: 'warning.main' }} />}>
              <Typography variant="subtitle2" fontWeight={700} sx={{ mb: 1 }}>
                Safe Concentration Limit: {settings.safe_limit || 5.0} ppm
              </Typography>
              <Typography variant="caption" color="text.secondary" paragraph>
                Samples below this limit are classified as <b>SAFE</b>. Samples between 1x and 2x are classified as <b>MODERATE</b> concern. Samples above 2x trigger <b>HIGH RISK</b> alerts.
              </Typography>
              <Slider
                value={typeof settings.safe_limit === 'number' ? settings.safe_limit : 5.0}
                onChange={(_, val) => setSettings({ ...settings, safe_limit: val })}
                min={0.5}
                max={25.0}
                step={0.5}
                valueLabelDisplay="auto"
                sx={{ color: 'warning.main', mb: 3 }}
              />

              <Button
                type="submit"
                variant="contained"
                startIcon={<Save />}
                disabled={saving}
                sx={{ borderRadius: '10px' }}
              >
                Save Settings
              </Button>
            </GlassCard>
          </Grid>
        </Grid>
      </form>

      <NotificationToast open={toast.open} message={toast.message} severity={toast.severity} onClose={() => setToast({ ...toast, open: false })} />
    </Box>
  );
}
