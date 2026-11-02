import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Drawer, List, ListItem, ListItemButton, ListItemIcon, ListItemText,
  Box, Typography, Tooltip, Divider, Avatar
} from '@mui/material';
import {
  Dashboard, CloudUpload, Assessment, History, Settings, Person,
  Info, ChevronLeft, Science, Logout
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import { glass } from '../theme/theme';

const NAV_ITEMS = [
  { label: 'Dashboard', icon: <Dashboard />, path: '/dashboard' },
  { label: 'Upload Spectrum', icon: <CloudUpload />, path: '/upload' },
  { label: 'Reports', icon: <Assessment />, path: '/reports' },
  { label: 'History', icon: <History />, path: '/history' },
  { label: 'Settings', icon: <Settings />, path: '/settings' },
  { label: 'Profile', icon: <Person />, path: '/profile' },
  { label: 'About', icon: <Info />, path: '/about' },
];

export default function Sidebar({ open, width, collapsedWidth, onToggle }) {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, userProfile, logout } = useAuth();
  const displayName = userProfile?.name || user?.displayName || 'Scientist';
  const initials = displayName.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: open ? width : collapsedWidth,
        flexShrink: 0,
        whiteSpace: 'nowrap',
        '& .MuiDrawer-paper': {
          width: open ? width : collapsedWidth,
          transition: 'width 0.3s ease',
          overflowX: 'hidden',
          ...glass(0.06),
          borderRight: '1px solid rgba(255,255,255,0.08)',
          display: 'flex',
          flexDirection: 'column',
        },
      }}
    >
      {/* Logo */}
      <Box sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 1.5, minHeight: 64 }}>
        <Box
          sx={{
            width: 38, height: 38, borderRadius: '10px', flexShrink: 0,
            background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 4px 12px rgba(59,130,246,0.4)',
          }}
        >
          <Science sx={{ color: 'white', fontSize: 20 }} />
        </Box>
        {open && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.1 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 700, lineHeight: 1.2, color: 'text.primary' }}>
              UV-Vis AI
            </Typography>
            <Typography variant="caption" sx={{ color: 'text.secondary' }}>
              Spectrum Analyzer
            </Typography>
          </motion.div>
        )}
      </Box>

      <Divider sx={{ borderColor: 'divider' }} />

      {/* Navigation */}
      <List sx={{ flexGrow: 1, px: 1, py: 1.5 }}>
        {NAV_ITEMS.map((item) => {
          const active = location.pathname === item.path ||
            (item.path !== '/dashboard' && location.pathname.startsWith(item.path));
          return (
            <Tooltip key={item.path} title={!open ? item.label : ''} placement="right">
              <ListItem disablePadding sx={{ mb: 0.5 }}>
                <ListItemButton
                  onClick={() => navigate(item.path)}
                  sx={{
                    borderRadius: '10px',
                    px: open ? 1.5 : 1,
                    minHeight: 46,
                    justifyContent: open ? 'flex-start' : 'center',
                    background: active ? 'linear-gradient(135deg, rgba(59,130,246,0.2), rgba(139,92,246,0.2))' : 'transparent',
                    border: active ? '1px solid rgba(59,130,246,0.3)' : '1px solid transparent',
                    '&:hover': {
                      background: 'rgba(59,130,246,0.12)',
                    },
                  }}
                >
                  <ListItemIcon
                    sx={{
                      color: active ? 'primary.main' : 'text.secondary',
                      minWidth: open ? 40 : 'auto',
                      justifyContent: 'center',
                    }}
                  >
                    {item.icon}
                  </ListItemIcon>
                  {open && (
                    <ListItemText
                      primary={item.label}
                      primaryTypographyProps={{
                        fontSize: '0.875rem', fontWeight: active ? 600 : 400,
                        color: active ? 'text.primary' : 'text.secondary',
                      }}
                    />
                  )}
                </ListItemButton>
              </ListItem>
            </Tooltip>
          );
        })}
      </List>

      <Divider sx={{ borderColor: 'divider' }} />

      {/* User Footer */}
      <Box sx={{ p: 1.5 }}>
        <ListItemButton
          onClick={handleLogout}
          sx={{ borderRadius: '10px', px: 1.5, py: 1, mb: 1, '&:hover': { background: 'rgba(239,68,68,0.1)' } }}
        >
          <ListItemIcon sx={{ color: 'error.main', minWidth: open ? 40 : 'auto', justifyContent: 'center' }}>
            <Logout fontSize="small" />
          </ListItemIcon>
          {open && <ListItemText primary="Logout" primaryTypographyProps={{ fontSize: '0.875rem', color: 'error.main', fontWeight: 500 }} />}
        </ListItemButton>

        {open && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, p: 1 }}>
            <Avatar sx={{ width: 34, height: 34, fontSize: '0.8rem', background: 'linear-gradient(135deg,#3b82f6,#8b5cf6)' }}>
              {initials}
            </Avatar>
            <Box sx={{ overflow: 'hidden' }}>
              <Typography variant="body2" sx={{ fontWeight: 600, color: 'text.primary', lineHeight: 1.2, noWrap: true }}>
                {displayName}
              </Typography>
              <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                {userProfile?.org_name || 'Laboratory'}
              </Typography>
            </Box>
          </Box>
        )}
      </Box>

      {/* Collapse toggle */}
      <Box
        onClick={onToggle}
        sx={{
          position: 'absolute', top: '50%', right: -14, transform: 'translateY(-50%)',
          width: 28, height: 28, borderRadius: '50%', cursor: 'pointer', zIndex: 10,
          background: 'linear-gradient(135deg,#3b82f6,#8b5cf6)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
          '&:hover': { transform: 'translateY(-50%) scale(1.1)' },
          transition: 'transform 0.2s',
        }}
      >
        <ChevronLeft sx={{ color: 'white', fontSize: 16, transform: open ? 'rotate(0)' : 'rotate(180deg)', transition: 'transform 0.3s' }} />
      </Box>
    </Drawer>
  );
}
