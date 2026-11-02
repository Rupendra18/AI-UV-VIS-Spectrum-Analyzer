import React from 'react';
import { Box, Typography, Grid, Chip } from '@mui/material';
import { Science, AutoAwesome, Security, Speed, BarChart } from '@mui/icons-material';
import GlassCard from '../components/GlassCard';

export default function AboutPage() {
  const specs = [
    { title: 'Machine Learning', desc: 'Random Forest Regressor (100 estimators, R² = 99.7%)' },
    { title: 'Peak Detection', desc: 'Automatic λmax wavelength and peak absorbance extraction' },
    { title: 'Backend REST API', desc: 'Python Flask 3.0 + PyJWT + Firebase Admin SDK' },
    { title: 'Frontend Architecture', desc: 'React 18 + Vite + Material UI v5 + Plotly.js' },
    { title: 'Reporting', desc: 'ReportLab PDF generation + CSV exports' },
    { title: 'Data Persistence', desc: 'Firebase Firestore + Storage with local JSON fallback' },
  ];

  return (
    <Box maxWidth="md" sx={{ mx: 'auto' }}>
      <GlassCard title="About AI UV-Vis Spectrum Analyzer" icon={<Science sx={{ color: 'primary.main' }} />}>
        <Typography variant="h6" fontWeight={700} gutterBottom>
          Enterprise Spectral Intelligence System
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph sx={{ lineHeight: 1.7 }}>
          The AI UV-Vis Spectrum Analyzer is a professional-grade chemical analysis platform engineered for analytical laboratories, research institutions, and industrial quality control. By replacing standard linear Beer-Lambert multiplication with a trained Random Forest Regressor ML model, it delivers highly accurate analyte concentration predictions across wide absorption bands.
        </Typography>

        <Box sx={{ mt: 4 }}>
          <Typography variant="subtitle1" fontWeight={700} sx={{ mb: 2 }}>
            Technical Architecture Specifications
          </Typography>
          <Grid container spacing={2}>
            {specs.map((item, idx) => (
              <Grid item xs={12} sm={6} key={idx}>
                <Box sx={{ p: 2, borderRadius: '14px', background: 'rgba(15,23,42,0.5)', border: '1px solid rgba(255,255,255,0.06)' }}>
                  <Typography variant="subtitle2" fontWeight={700} color="primary.main">
                    {item.title}
                  </Typography>
                  <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 0.5 }}>
                    {item.desc}
                  </Typography>
                </Box>
              </Grid>
            ))}
          </Grid>
        </Box>
      </GlassCard>
    </Box>
  );
}
