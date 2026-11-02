import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Box, Typography, Button, Grid, Chip } from '@mui/material';
import { PictureAsPdf, Download, ArrowBack, Science } from '@mui/icons-material';
import GlassCard from '../components/GlassCard';
import SpectrumChart from '../components/SpectrumChart';
import PredictionCard from '../components/PredictionCard';
import LoadingSpinner from '../components/LoadingSpinner';
import api from '../services/api';

export default function AnalysisPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchAnalysis();
  }, [id]);

  const fetchAnalysis = async () => {
    setLoading(true);
    try {
      const res = await api.get('/history');
      if (res.data.status === 'success') {
        const item = (res.data.history || []).find((a) => a.id === id);
        if (item) setAnalysis(item);
        else setError('Analysis record not found.');
      }
    } catch (err) {
      setError(err.message || 'Failed to fetch analysis details.');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPDF = () => {
    window.open(`/api/reports/${id}/pdf`, '_blank');
  };

  const handleDownloadCSV = () => {
    window.open(`/api/reports/${id}/csv`, '_blank');
  };

  if (loading) return <LoadingSpinner message="Fetching Analysis Details..." />;
  if (error || !analysis) {
    return (
      <Box sx={{ py: 6, textAlign: 'center' }}>
        <Typography variant="h6" color="error" gutterBottom>{error || 'Record Not Found'}</Typography>
        <Button startIcon={<ArrowBack />} onClick={() => navigate('/history')}>Back to History</Button>
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Button startIcon={<ArrowBack />} onClick={() => navigate(-1)} sx={{ borderRadius: '10px' }}>
          Back
        </Button>
        <Box sx={{ display: 'flex', gap: 1.5 }}>
          <Button variant="outlined" startIcon={<Download />} onClick={handleDownloadCSV} sx={{ borderRadius: '10px' }}>
            Export CSV
          </Button>
          <Button variant="contained" startIcon={<PictureAsPdf />} onClick={handleDownloadPDF} sx={{ borderRadius: '10px' }}>
            Download PDF Report
          </Button>
        </Box>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} lg={7}>
          <GlassCard title={`Spectral Plot — ${analysis.filename}`} icon={<Science sx={{ color: 'primary.main' }} />}>
            <SpectrumChart
              data={[
                { Wavelength: analysis.peak_wavelength - 60, Absorbance: 0.08 },
                { Wavelength: analysis.peak_wavelength, Absorbance: analysis.peak_absorbance },
                { Wavelength: analysis.peak_wavelength + 60, Absorbance: 0.04 },
              ]}
              filename={analysis.filename}
              peakWavelength={analysis.peak_wavelength}
              peakAbsorbance={analysis.peak_absorbance}
              height={450}
            />
          </GlassCard>
        </Grid>

        <Grid item xs={12} lg={5}>
          <PredictionCard analysis={analysis} />
        </Grid>
      </Grid>
    </Box>
  );
}
