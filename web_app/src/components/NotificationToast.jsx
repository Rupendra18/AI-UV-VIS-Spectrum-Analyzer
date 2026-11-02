import React from 'react';
import { Snackbar, Alert } from '@mui/material';

export default function NotificationToast({ open, message, severity = 'info', onClose, autoHideDuration = 4000 }) {
  return (
    <Snackbar
      open={open}
      autoHideDuration={autoHideDuration}
      onClose={onClose}
      anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
    >
      <Alert
        onClose={onClose}
        severity={severity}
        variant="filled"
        sx={{
          borderRadius: '12px',
          fontWeight: 600,
          boxShadow: '0 10px 30px rgba(0,0,0,0.3)',
        }}
      >
        {message}
      </Alert>
    </Snackbar>
  );
}
