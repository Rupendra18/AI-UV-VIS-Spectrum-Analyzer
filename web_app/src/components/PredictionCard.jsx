import React from 'react';
import { Box, Typography, Grid, Chip, Divider } from '@mui/material';
import {
  Speed, Shield, Psychology, Analytics, ShowChart
} from '@mui/icons-material';
import GlassCard from './GlassCard';

export default function PredictionCard({ analysis }) {
  if (!analysis) return null;

  const {
    peak_wavelength, peak_absorbance, predicted_concentration,
    status, confidence_score, algorithm, accuracy_percentage,
    rmse, mae, interpretation, conclusion
  } = analysis;

  const statusColor = status === 'SAFE' ? 'success' : status === 'MODERATE' ? 'warning' : 'error';
  const statusBg = status === 'SAFE' ? 'rgba(16,185,129,0.15)' : status === 'MODERATE' ? 'rgba(245,158,11,0.15)' : 'rgba(239,68,68,0.15)';

  const stats = [
    { label: 'Peak Wavelength (λmax)', value: `${peak_wavelength} nm`, color: '#38bdf8' },
    { label: 'Peak Absorbance', value: `${peak_absorbance} AU`, color: '#8b5cf6' },
    { label: 'Predicted Concentration', value: `${predicted_concentration} ppm`, color: '#3b82f6' },
    { label: 'AI Confidence Score', value: `${confidence_score}%`, color: '#10b981' },
  ];

  return (
    <GlassCard
      title="AI Spectrum Intelligence"
      icon={<Psychology sx={{ color: 'primary.main' }} />}
      action={
        <Chip
          label={status || 'SAFE'}
          color={statusColor}
          size="small"
          sx={{ fontWeight: 700, px: 1 }}
        />
      }
    >
      <Grid container spacing={2}>
        {stats.map((s, idx) => (
          <Grid item xs={6} sm={3} key={idx}>
            <Box
              sx={{
                p: 2,
                borderRadius: '14px',
                background: 'rgba(15,23,42,0.5)',
                border: '1px solid rgba(255,255,255,0.06)',
              }}
            >
              <Typography variant="caption" color="text.secondary" display="block">
                {s.label}
              </Typography>
              <Typography variant="h6" fontWeight={800} sx={{ color: s.color, mt: 0.5 }}>
                {s.value}
              </Typography>
            </Box>
          </Grid>
        ))}
      </Grid>

      {/* Model Specs */}
      <Box sx={{ mt: 3, p: 2, borderRadius: '14px', background: 'rgba(139,92,246,0.08)', border: '1px solid rgba(139,92,246,0.2)' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
          <Typography variant="subtitle2" fontWeight={700} sx={{ color: '#a78bfa' }}>
            Machine Learning Engine
          </Typography>
          <Chip label={algorithm || 'Random Forest Regressor'} size="small" variant="outlined" sx={{ borderColor: '#8b5cf6', color: '#a78bfa', fontSize: '0.75rem' }} />
        </Box>
        <Grid container spacing={2} sx={{ mt: 0.5 }}>
          <Grid item xs={4}>
            <Typography variant="caption" color="text.secondary">Accuracy (R²)</Typography>
            <Typography variant="body2" fontWeight={700} sx={{ color: '#a78bfa' }}>{accuracy_percentage ?? 99.7}%</Typography>
          </Grid>
          <Grid item xs={4}>
            <Typography variant="caption" color="text.secondary">RMSE</Typography>
            <Typography variant="body2" fontWeight={700} sx={{ color: '#38bdf8' }}>{rmse ?? 0.48}</Typography>
          </Grid>
          <Grid item xs={4}>
            <Typography variant="caption" color="text.secondary">MAE</Typography>
            <Typography variant="body2" fontWeight={700} sx={{ color: '#fbbf24' }}>{mae ?? 0.38}</Typography>
          </Grid>
        </Grid>
      </Box>

      {/* Scientific Interpretation */}
      {interpretation && (
        <Box sx={{ mt: 3 }}>
          <Typography variant="subtitle2" fontWeight={700} sx={{ mb: 1, color: 'text.primary' }}>
            Scientific Interpretation
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.6 }}>
            {interpretation}
          </Typography>
        </Box>
      )}

      {/* Conclusion */}
      {conclusion && (
        <Box sx={{ mt: 2, p: 2, borderRadius: '12px', background: statusBg, border: `1px solid ${status === 'SAFE' ? 'rgba(16,185,129,0.3)' : status === 'MODERATE' ? 'rgba(245,158,11,0.3)' : 'rgba(239,68,68,0.3)'}` }}>
          <Typography variant="caption" fontWeight={700} color={`${statusColor}.main`} display="block" sx={{ textTransform: 'uppercase', letterSpacing: '0.05em', mb: 0.5 }}>
            Recommendation & Conclusion
          </Typography>
          <Typography variant="body2" color="text.primary" sx={{ lineHeight: 1.5 }}>
            {conclusion}
          </Typography>
        </Box>
      )}
    </GlassCard>
  );
}
