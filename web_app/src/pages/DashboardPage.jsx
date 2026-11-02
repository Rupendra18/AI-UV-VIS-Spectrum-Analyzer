import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Grid, Box, Typography, Button, Table, TableBody, TableCell, TableHead,
  TableRow, Chip, IconButton, Tooltip
} from '@mui/material';
import {
  Layers, VerifiedUser, ReportProblem, Shield, Speed, CloudUpload as UploadIcon,
  Visibility, PictureAsPdf, Article
} from '@mui/icons-material';
import GlassCard from '../components/GlassCard';
import SpectrumChart from '../components/SpectrumChart';
import UploadCard from '../components/UploadCard';
import PredictionCard from '../components/PredictionCard';
import LoadingSpinner from '../components/LoadingSpinner';
import api from '../services/api';

export default function DashboardPage() {
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [recentAnalyses, setRecentAnalyses] = useState([]);
  const [currentAnalysis, setCurrentAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const [statsRes, historyRes] = await Promise.all([
        api.get('/dashboard/stats'),
        api.get('/history?per_page=5'),
      ]);

      if (statsRes.data.status === 'ok') setStats(statsRes.data.stats);
      if (historyRes.data.status === 'success') {
        const hist = historyRes.data.history || [];
        setRecentAnalyses(hist);
        if (hist.length > 0 && !currentAnalysis) {
          setCurrentAnalysis(hist[0]);
        }
      }
    } catch (err) {
      console.error('Failed to load dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAnalysisComplete = (newAnalysis) => {
    setCurrentAnalysis(newAnalysis);
    fetchDashboardData();
  };

  if (loading) return <LoadingSpinner message="Loading Dashboard..." />;

  const kpis = [
    { title: 'Total Analyses', value: stats?.total || 0, icon: <Layers sx={{ color: '#3b82f6' }} />, color: '#3b82f6' },
    { title: 'Safe Samples', value: stats?.safe || 0, icon: <VerifiedUser sx={{ color: '#10b981' }} />, color: '#10b981' },
    { title: 'Moderate Concern', value: stats?.moderate || 0, icon: <ReportProblem sx={{ color: '#f59e0b' }} />, color: '#f59e0b' },
    { title: 'High Risk', value: stats?.high_risk || 0, icon: <Shield sx={{ color: '#ef4444' }} />, color: '#ef4444' },
  ];

  return (
    <Box>
      {/* Top KPI Cards Grid */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {kpis.map((kpi, idx) => (
          <Grid item xs={6} sm={3} key={idx}>
            <GlassCard hover sx={{ p: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="caption" color="text.secondary" fontWeight={600}>
                  {kpi.title}
                </Typography>
                <Box sx={{ p: 1, borderRadius: '10px', background: 'rgba(255,255,255,0.04)' }}>
                  {kpi.icon}
                </Box>
              </Box>
              <Typography variant="h4" fontWeight={900} sx={{ color: kpi.color }}>
                {kpi.value}
              </Typography>
            </GlassCard>
          </Grid>
        ))}
      </Grid>

      {/* Main Analysis Section */}
      <Grid container spacing={3}>
        {/* Left Col: Upload & Plotly Graph */}
        <Grid item xs={12} lg={7}>
          <GlassCard title="Upload Spectrum Dataset" icon={<UploadIcon sx={{ color: 'primary.main' }} />} sx={{ mb: 3 }}>
            <UploadCard onAnalysisComplete={handleAnalysisComplete} />
          </GlassCard>

          {currentAnalysis && (
            <GlassCard
              title={`UV-Vis Spectral Plot — ${currentAnalysis.filename}`}
              icon={<Science sx={{ color: 'secondary.main' }} />}
              action={
                <Button
                  size="small"
                  variant="outlined"
                  onClick={() => navigate(`/analysis/${currentAnalysis.id}`)}
                  startIcon={<Visibility />}
                >
                  Full View
                </Button>
              }
            >
              <SpectrumChart
                data={[
                  { Wavelength: currentAnalysis.peak_wavelength - 50, Absorbance: 0.1 },
                  { Wavelength: currentAnalysis.peak_wavelength, Absorbance: currentAnalysis.peak_absorbance },
                  { Wavelength: currentAnalysis.peak_wavelength + 50, Absorbance: 0.05 },
                ]}
                filename={currentAnalysis.filename}
                peakWavelength={currentAnalysis.peak_wavelength}
                peakAbsorbance={currentAnalysis.peak_absorbance}
                height={360}
              />
            </GlassCard>
          )}
        </Grid>

        {/* Right Col: Prediction Intelligence & Recent Activity */}
        <Grid item xs={12} lg={5}>
          {currentAnalysis ? (
            <PredictionCard analysis={currentAnalysis} />
          ) : (
            <GlassCard title="AI Intelligence Ready">
              <Box sx={{ py: 4, textAlign: 'center' }}>
                <Science sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
                <Typography variant="h6" fontWeight={700}>
                  No Spectrum Active
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Upload a CSV file to inspect peak absorbance, ML concentration, and safety classification.
                </Typography>
              </Box>
            </GlassCard>
          )}

          {/* Recent Runs Table */}
          <GlassCard
            title="Recent Analyses"
            sx={{ mt: 3 }}
            action={
              <Button size="small" onClick={() => navigate('/history')}>
                View All
              </Button>
            }
          >
            {recentAnalyses.length === 0 ? (
              <Typography variant="body2" color="text.secondary" align="center" sx={{ py: 3 }}>
                No recent run logs
              </Typography>
            ) : (
              <Box sx={{ overflowX: 'auto' }}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell sx={{ color: 'text.secondary', fontWeight: 700 }}>Filename</TableCell>
                      <TableCell sx={{ color: 'text.secondary', fontWeight: 700 }}>Status</TableCell>
                      <TableCell sx={{ color: 'text.secondary', fontWeight: 700 }}>Conc.</TableCell>
                      <TableCell align="right" sx={{ color: 'text.secondary', fontWeight: 700 }}>Action</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {recentAnalyses.map((row) => (
                      <TableRow key={row.id} hover onClick={() => setCurrentAnalysis(row)} sx={{ cursor: 'pointer' }}>
                        <TableCell sx={{ fontWeight: 600 }}>{row.filename}</TableCell>
                        <TableCell>
                          <Chip
                            label={row.status}
                            size="small"
                            color={row.status === 'SAFE' ? 'success' : row.status === 'MODERATE' ? 'warning' : 'error'}
                            sx={{ fontWeight: 700, fontSize: '0.7rem' }}
                          />
                        </TableCell>
                        <TableCell sx={{ fontWeight: 600, color: 'primary.main' }}>
                          {row.predicted_concentration} ppm
                        </TableCell>
                        <TableCell align="right">
                          <Tooltip title="View Report">
                            <IconButton size="small" onClick={(e) => { e.stopPropagation(); navigate(`/analysis/${row.id}`); }}>
                              <Visibility fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </Box>
            )}
          </GlassCard>
        </Grid>
      </Grid>
    </Box>
  );
}
