import React from 'react';
import { Box, CircularProgress, Typography } from '@mui/material';

export default function LoadingSpinner({ message = 'Loading...', fullScreen = false }) {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        p: 4,
        ...(fullScreen && {
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          zIndex: 9999,
          background: 'rgba(15, 23, 42, 0.85)',
          backdropFilter: 'blur(20px)',
        }),
      }}
    >
      <CircularProgress size={48} sx={{ color: 'primary.main', mb: 2 }} />
      <Typography variant="body2" color="text.secondary" fontWeight={500}>
        {message}
      </Typography>
    </Box>
  );
}
