import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Typography, Grid, Paper, Alert } from '@mui/material';
import { CloudUpload, Info, Science } from '@mui/icons-material';
import GlassCard from '../components/GlassCard';
import UploadCard from '../components/UploadCard';
import PredictionCard from '../components/PredictionCard';

export default function UploadPage() {
  const navigate = useNavigate();
  const [analysisResult, setAnalysisResult] = useState(null);

  const handleComplete = (result) => {
    setAnalysisResult(result);
  };

  return (
    <Box>
      <Typography variant="h5" fontWeight={800} sx={{ mb: 1 }}>
        Upload UV-Vis Spectrum Dataset
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 4 }}>
        Upload a raw spectral CSV file to run automated peak extraction and Random Forest Machine Learning prediction.
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <GlassCard title="File Ingestion" icon={<CloudUpload sx={{ color: 'primary.main' }} />}>
            <UploadCard onAnalysisComplete={handleComplete} />
          </GlassCard>

          {/* Guidelines */}
          <GlassCard title="CSV Format Requirements" icon={<Info sx={{ color: 'secondary.main' }} />} sx={{ mt: 3 }}>
            <Typography variant="body2" color="text.secondary" paragraph>
              The uploaded CSV must contain clean tabular data with at least two headers:
            </Typography>
            <Box component="ul" sx={{ color: 'text.secondary', pl: 2, fontSize: '0.875rem' }}>
              <li><b>Wavelength</b> — Spectral wavelength in nanometers (nm), e.g., 200 to 800</li>
              <li><b>Absorbance</b> — Absorbance values in Arbitrary Units (AU), e.g., 0.0 to 3.5</li>
            </Box>
            <Alert severity="info" sx={{ mt: 2, borderRadius: '12px' }}>
              Files up to 10MB are supported. Malformed rows will be filtered automatically.
            </Alert>
          </GlassCard>
        </Grid>

        <Grid item xs={12} md={6}>
          {analysisResult ? (
            <PredictionCard analysis={analysisResult} />
          ) : (
            <GlassCard title="Prediction Output Preview" icon={<Science sx={{ color: 'accent.main' }} />}>
              <Box sx={{ py: 6, textAlign: 'center' }}>
                <Science sx={{ fontSize: 64, color: 'primary.main', mb: 2, opacity: 0.5 }} />
                <Typography variant="h6" fontWeight={700}>
                  Awaiting File Upload
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ maxWidth: 360, mx: 'auto', mt: 1 }}>
                  Once you select a spectral CSV file, the AI prediction engine will output analyte concentration, R² accuracy score, and risk status here.
                </Typography>
              </Box>
            </GlassCard>
          )}
        </Grid>
      </Grid>
    </Box>
  );
}
