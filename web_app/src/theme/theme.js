import { createTheme } from '@mui/material/styles';

// ── Shared Design Tokens ────────────────────────────────────────────────────
const tokens = {
  primary: '#3b82f6',       // Blue-500
  primaryDark: '#1d4ed8',   // Blue-700
  secondary: '#38bdf8',     // Sky-400
  accent: '#8b5cf6',        // Violet-500
  success: '#10b981',       // Emerald-500
  warning: '#f59e0b',       // Amber-500
  danger: '#ef4444',        // Red-500
  fontHeading: '"Inter", sans-serif',
  fontMono: '"JetBrains Mono", monospace',
  radiusMd: '12px',
  radiusLg: '20px',
  radiusFull: '9999px',
};

// ── Glass morphism helper (for sx props) ────────────────────────────────────
export const glass = (opacity = 0.08) => ({
  background: `rgba(255,255,255,${opacity})`,
  backdropFilter: 'blur(20px)',
  WebkitBackdropFilter: 'blur(20px)',
  border: '1px solid rgba(255,255,255,0.12)',
});

export const glassDark = (opacity = 0.04) => ({
  background: `rgba(15,23,42,${1 - opacity})`,
  backdropFilter: 'blur(20px)',
  WebkitBackdropFilter: 'blur(20px)',
  border: '1px solid rgba(255,255,255,0.08)',
});

// ── Dark Theme ───────────────────────────────────────────────────────────────
export const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: tokens.primary, dark: tokens.primaryDark },
    secondary: { main: tokens.secondary },
    success: { main: tokens.success },
    warning: { main: tokens.warning },
    error: { main: tokens.danger },
    background: {
      default: '#0f172a',
      paper: 'rgba(15,23,42,0.9)',
    },
    text: {
      primary: '#f8fafc',
      secondary: '#94a3b8',
    },
    divider: 'rgba(255,255,255,0.08)',
  },
  typography: {
    fontFamily: tokens.fontHeading,
    h1: { fontWeight: 800, letterSpacing: '-0.02em' },
    h2: { fontWeight: 700, letterSpacing: '-0.01em' },
    h3: { fontWeight: 700 },
    h4: { fontWeight: 600 },
    h5: { fontWeight: 600 },
    h6: { fontWeight: 600 },
    body1: { fontSize: '0.9375rem', lineHeight: 1.6 },
    body2: { fontSize: '0.875rem', lineHeight: 1.5, color: '#94a3b8' },
    caption: { fontFamily: tokens.fontMono, fontSize: '0.75rem' },
  },
  shape: { borderRadius: 12 },
  components: {
    MuiCard: {
      defaultProps: { elevation: 0 },
      styleOverrides: {
        root: {
          ...glass(0.06),
          borderRadius: '20px',
          transition: 'transform 0.2s ease, box-shadow 0.2s ease',
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: '0 20px 40px rgba(0,0,0,0.3)',
          },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: '10px',
          textTransform: 'none',
          fontWeight: 600,
          letterSpacing: '0.01em',
          padding: '10px 22px',
        },
        containedPrimary: {
          background: `linear-gradient(135deg, ${tokens.primary}, ${tokens.accent})`,
          boxShadow: `0 4px 15px rgba(59,130,246,0.35)`,
          '&:hover': {
            background: `linear-gradient(135deg, ${tokens.primaryDark}, #7c3aed)`,
            boxShadow: `0 6px 20px rgba(59,130,246,0.5)`,
          },
        },
      },
    },
    MuiTextField: {
      defaultProps: { variant: 'outlined', size: 'small' },
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: '10px',
            background: 'rgba(255,255,255,0.04)',
            '&:hover .MuiOutlinedInput-notchedOutline': {
              borderColor: tokens.primary,
            },
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: { borderRadius: '8px', fontWeight: 600 },
      },
    },
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          background: 'linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #0f172a 100%)',
          backgroundAttachment: 'fixed',
          minHeight: '100vh',
          scrollbarWidth: 'thin',
          scrollbarColor: '#334155 transparent',
          '&::-webkit-scrollbar': { width: '6px' },
          '&::-webkit-scrollbar-track': { background: 'transparent' },
          '&::-webkit-scrollbar-thumb': { background: '#334155', borderRadius: '3px' },
        },
      },
    },
  },
});

// ── Light Theme ──────────────────────────────────────────────────────────────
export const lightTheme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: tokens.primary, dark: tokens.primaryDark },
    secondary: { main: tokens.secondary },
    success: { main: tokens.success },
    warning: { main: tokens.warning },
    error: { main: tokens.danger },
    background: {
      default: '#f0f4ff',
      paper: 'rgba(255,255,255,0.85)',
    },
    text: {
      primary: '#0f172a',
      secondary: '#475569',
    },
  },
  typography: darkTheme.typography,
  shape: { borderRadius: 12 },
  components: {
    ...darkTheme.components,
    MuiCard: {
      defaultProps: { elevation: 0 },
      styleOverrides: {
        root: {
          background: 'rgba(255,255,255,0.8)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(59,130,246,0.15)',
          borderRadius: '20px',
          transition: 'transform 0.2s ease, box-shadow 0.2s ease',
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: '0 16px 32px rgba(59,130,246,0.12)',
          },
        },
      },
    },
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          background: 'linear-gradient(135deg, #e0eaff 0%, #f0f4ff 50%, #e8f5ff 100%)',
          backgroundAttachment: 'fixed',
          minHeight: '100vh',
        },
      },
    },
  },
});

export { tokens };
