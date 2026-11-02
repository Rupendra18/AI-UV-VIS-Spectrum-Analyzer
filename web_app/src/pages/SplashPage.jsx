import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Typography, Button, Container, Grid } from '@mui/material';
import { Science, ArrowForward, AutoAwesome, Security, Speed, BarChart } from '@mui/icons-material';
import { motion } from 'framer-motion';

export default function SplashPage() {
  const navigate = useNavigate();

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #0f172a 100%)',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        position: 'relative',
        overflow: 'hidden',
        color: 'white',
      }}
    >
      {/* Background Glow Spheres */}
      <Box
        sx={{
          position: 'absolute', top: '-10%', left: '20%', width: 500, height: 500,
          borderRadius: '50%', background: 'radial-gradient(circle, rgba(59,130,246,0.2) 0%, rgba(0,0,0,0) 70%)',
          filter: 'blur(60px)', pointerEvents: 'none',
        }}
      />
      <Box
        sx={{
          position: 'absolute', bottom: '-10%', right: '15%', width: 600, height: 600,
          borderRadius: '50%', background: 'radial-gradient(circle, rgba(139,92,246,0.2) 0%, rgba(0,0,0,0) 70%)',
          filter: 'blur(80px)', pointerEvents: 'none',
        }}
      />

      <Container maxWidth="lg" sx={{ zIndex: 1, py: 8 }}>
        <Grid container spacing={6} alignItems="center">
          <Grid item xs={12} md={7}>
            <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8 }}>
              {/* Badge */}
              <Box
                sx={{
                  display: 'inline-flex', alignItems: 'center', gap: 1, px: 2, py: 0.8,
                  borderRadius: '9999px', background: 'rgba(59,130,246,0.15)',
                  border: '1px solid rgba(59,130,246,0.3)', mb: 3,
                }}
              >
                <AutoAwesome sx={{ color: '#38bdf8', fontSize: 18 }} />
                <Typography variant="caption" sx={{ color: '#38bdf8', fontWeight: 700, letterSpacing: '0.05em', textTransform: 'uppercase' }}>
                  Next-Gen AI Chemical Analysis
                </Typography>
              </Box>

              <Typography variant="h2" sx={{ fontWeight: 900, lineHeight: 1.1, mb: 3 }}>
                Precision UV-Vis <br />
                <span style={{ background: 'linear-gradient(135deg, #3b82f6, #8b5cf6, #ec4899)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                  Spectrum Intelligence
                </span>
              </Typography>

              <Typography variant="h6" sx={{ color: '#94a3b8', fontWeight: 400, mb: 4, maxWidth: 540, lineHeight: 1.6 }}>
                Transform raw absorption curves into instant chemical insights. Powered by trained Random Forest Machine Learning, automated peak detection, and enterprise PDF reporting.
              </Typography>

              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Button
                  variant="contained"
                  size="large"
                  endIcon={<ArrowForward />}
                  onClick={() => navigate('/login')}
                  sx={{
                    px: 4, py: 1.5, fontSize: '1.05rem', borderRadius: '14px',
                    background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
                    boxShadow: '0 8px 25px rgba(59,130,246,0.4)',
                  }}
                >
                  Launch App
                </Button>

                <Button
                  variant="outlined"
                  size="large"
                  onClick={() => navigate('/about')}
                  sx={{
                    px: 4, py: 1.5, fontSize: '1.05rem', borderRadius: '14px',
                    borderColor: 'rgba(255,255,255,0.2)', color: 'white',
                    '&:hover': { borderColor: 'white', background: 'rgba(255,255,255,0.05)' },
                  }}
                >
                  Explore Documentation
                </Button>
              </Box>
            </motion.div>
          </Grid>

          {/* Graphic Showcase */}
          <Grid item xs={12} md={5}>
            <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.8, delay: 0.2 }}>
              <Box
                sx={{
                  p: 4, borderRadius: '24px',
                  background: 'rgba(255,255,255,0.05)', backdropFilter: 'blur(30px)',
                  border: '1px solid rgba(255,255,255,0.12)',
                  boxShadow: '0 30px 60px rgba(0,0,0,0.4)',
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                  <Box sx={{ width: 48, height: 48, borderRadius: '14px', background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Science sx={{ color: 'white', fontSize: 26 }} />
                  </Box>
                  <Box>
                    <Typography variant="subtitle1" fontWeight={700}>Random Forest RF-100</Typography>
                    <Typography variant="caption" sx={{ color: '#10b981', fontWeight: 600 }}>R² Score: 99.7% Accuracy</Typography>
                  </Box>
                </Box>

                {/* Feature Chips */}
                <Grid container spacing={2}>
                  {[
                    { icon: <Speed />, title: '< 500ms', desc: 'Inference Speed' },
                    { icon: <Security />, title: 'ISO Compliant', desc: 'PDF Reports' },
                    { icon: <BarChart />, title: 'λmax Peak', desc: 'Auto Detection' },
                    { icon: <AutoAwesome />, title: 'Real-time', desc: 'Firebase Sync' },
                  ].map((f, i) => (
                    <Grid item xs={6} key={i}>
                      <Box sx={{ p: 2, borderRadius: '14px', background: 'rgba(15,23,42,0.6)', border: '1px solid rgba(255,255,255,0.06)' }}>
                        <Box sx={{ color: '#38bdf8', mb: 1 }}>{f.icon}</Box>
                        <Typography variant="body2" fontWeight={700}>{f.title}</Typography>
                        <Typography variant="caption" color="#94a3b8">{f.desc}</Typography>
                      </Box>
                    </Grid>
                  ))}
                </Grid>
              </Box>
            </motion.div>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
}
