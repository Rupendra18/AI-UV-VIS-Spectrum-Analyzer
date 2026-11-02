import React, { useState, useRef } from 'react';
import { Box, Typography, Button, CircularProgress, Alert } from '@mui/material';
import { CloudUpload, InsertDriveFile, CheckCircle } from '@mui/icons-material';
import { glass } from '../theme/theme';
import api from '../services/api';

export default function UploadCard({ onAnalysisComplete }) {
  const [dragActive, setDragActive] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const inputRef = useRef(null);

  const handleFile = async (file) => {
    if (!file) return;
    if (!file.name.endsWith('.csv')) {
      setError('Please upload a valid CSV file containing Wavelength and Absorbance columns.');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await api.post('/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      if (res.data.status === 'success') {
        setSuccess(`Successfully analyzed ${file.name}`);
        if (onAnalysisComplete) {
          onAnalysisComplete(res.data.analysis);
        }
      } else {
        setError(res.data.error || 'Failed to analyze spectrum CSV.');
      }
    } catch (err) {
      setError(err.response?.data?.error || err.message || 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') setDragActive(true);
    else if (e.type === 'dragleave') setDragActive(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  return (
    <Box>
      <Box
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        sx={{
          p: 4,
          borderRadius: '20px',
          border: '2px dashed',
          borderColor: dragActive ? 'primary.main' : 'rgba(255,255,255,0.15)',
          background: dragActive ? 'rgba(59,130,246,0.1)' : 'rgba(15,23,42,0.4)',
          backdropFilter: 'blur(20px)',
          textAlign: 'center',
          cursor: 'pointer',
          transition: 'all 0.3s ease',
          '&:hover': {
            borderColor: 'primary.main',
            background: 'rgba(59,130,246,0.05)',
          },
        }}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".csv"
          style={{ display: 'none' }}
          onChange={(e) => handleFile(e.target.files[0])}
        />

        {loading ? (
          <Box sx={{ py: 2 }}>
            <CircularProgress size={48} sx={{ color: 'primary.main', mb: 2 }} />
            <Typography variant="subtitle1" fontWeight={600}>
              Analyzing Spectral Data...
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Running Machine Learning Prediction Model
            </Typography>
          </Box>
        ) : (
          <Box>
            <Box
              sx={{
                width: 64,
                height: 64,
                borderRadius: '50%',
                background: 'linear-gradient(135deg, rgba(59,130,246,0.2), rgba(139,92,246,0.2))',
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                mb: 2,
              }}
            >
              <CloudUpload sx={{ fontSize: 32, color: 'primary.main' }} />
            </Box>
            <Typography variant="h6" fontWeight={700} sx={{ mb: 0.5 }}>
              Drop Spectrum CSV File Here
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              or click to browse from your device
            </Typography>

            <Button
              variant="outlined"
              size="small"
              startIcon={<InsertDriveFile />}
              sx={{ borderRadius: '10px', textTransform: 'none' }}
            >
              Browse Files
            </Button>
            <Typography variant="caption" display="block" color="text.secondary" sx={{ mt: 2 }}>
              Requires <b>Wavelength</b> & <b>Absorbance</b> columns
            </Typography>
          </Box>
        )}
      </Box>

      {error && <Alert severity="error" sx={{ mt: 2, borderRadius: '12px' }}>{error}</Alert>}
      {success && <Alert severity="success" icon={<CheckCircle />} sx={{ mt: 2, borderRadius: '12px' }}>{success}</Alert>}
    </Box>
  );
}
