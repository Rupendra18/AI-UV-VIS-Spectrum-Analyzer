import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  AppBar, Toolbar, Typography, IconButton, Box, Badge, Menu, MenuItem,
  ListItemIcon, ListItemText, Tooltip, Avatar, Divider
} from '@mui/material';
import {
  DarkMode, LightMode, Notifications, Person, Settings, Logout,
  CloudUpload, Refresh
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';

const PAGE_TITLES = {
  '/dashboard': 'Dashboard Overview',
  '/upload': 'Upload Spectrum',
  '/reports': 'Analysis Reports',
  '/history': 'Spectral History',
  '/settings': 'Application Settings',
  '/profile': 'User Profile',
  '/about': 'About AI Spectrum Analyzer',
};

export default function Navbar({ darkMode, setDarkMode, sidebarOpen }) {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, userProfile, logout } = useAuth();
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [notifAnchor, setNotifAnchor] = useState(null);
  const [profileAnchor, setProfileAnchor] = useState(null);

  const title = PAGE_TITLES[location.pathname] || 'Spectrum Intelligence';

  useEffect(() => {
    fetchNotifications();
  }, []);

  const fetchNotifications = async () => {
    try {
      const res = await api.get('/notifications');
      if (res.data.status === 'success') {
        setNotifications(res.data.notifications || []);
        setUnreadCount(res.data.unread || 0);
      }
    } catch (_) {}
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const displayName = userProfile?.name || user?.displayName || 'Scientist';
  const initials = displayName.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);

  return (
    <AppBar
      position="fixed"
      elevation={0}
      sx={{
        width: `calc(100% - ${sidebarOpen ? 260 : 72}px)`,
        ml: `${sidebarOpen ? 260 : 72}px`,
        transition: 'width 0.3s ease, margin 0.3s ease',
        background: 'rgba(15, 23, 42, 0.75)',
        backdropFilter: 'blur(20px)',
        WebkitBackdropFilter: 'blur(20px)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
        color: 'text.primary',
        zIndex: (theme) => theme.zIndex.drawer + 1,
      }}
    >
      <Toolbar sx={{ justifyContent: 'space-between', minHeight: 64 }}>
        <Typography variant="h6" sx={{ fontWeight: 700, background: 'linear-gradient(135deg, #f8fafc, #94a3b8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
          {title}
        </Typography>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Tooltip title="Upload Spectrum">
            <IconButton onClick={() => navigate('/upload')} sx={{ color: 'primary.main', background: 'rgba(59,130,246,0.1)' }}>
              <CloudUpload fontSize="small" />
            </IconButton>
          </Tooltip>

          <Tooltip title={darkMode ? 'Light Mode' : 'Dark Mode'}>
            <IconButton onClick={() => setDarkMode(!darkMode)} color="inherit">
              {darkMode ? <LightMode fontSize="small" /> : <DarkMode fontSize="small" />}
            </IconButton>
          </Tooltip>

          {/* Notifications */}
          <Tooltip title="Notifications">
            <IconButton onClick={(e) => setNotifAnchor(e.currentTarget)} color="inherit">
              <Badge badgeContent={unreadCount} color="error">
                <Notifications fontSize="small" />
              </Badge>
            </IconButton>
          </Tooltip>

          <Menu
            anchorEl={notifAnchor}
            open={Boolean(notifAnchor)}
            onClose={() => setNotifAnchor(null)}
            PaperProps={{
              sx: {
                width: 320,
                maxHeight: 400,
                mt: 1.5,
                background: 'rgba(15, 23, 42, 0.95)',
                backdropFilter: 'blur(20px)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '16px',
              }
            }}
          >
            <Box sx={{ p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 700 }}>Notifications</Typography>
              <IconButton size="small" onClick={fetchNotifications}><Refresh fontSize="small" /></IconButton>
            </Box>
            <Divider sx={{ borderColor: 'divider' }} />
            {notifications.length === 0 ? (
              <Box sx={{ p: 3, textAlign: 'center' }}>
                <Typography variant="body2" color="text.secondary">No new alerts</Typography>
              </Box>
            ) : (
              notifications.map((n) => (
                <MenuItem key={n.id} onClick={() => { setNotifAnchor(null); navigate('/history'); }}>
                  <Box>
                    <Typography variant="body2" sx={{ fontWeight: 600, color: n.type === 'alert' ? 'error.main' : 'warning.main' }}>
                      {n.title}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">{n.message}</Typography>
                  </Box>
                </MenuItem>
              ))
            )}
          </Menu>

          {/* Profile Menu */}
          <IconButton onClick={(e) => setProfileAnchor(e.currentTarget)} sx={{ p: 0.5, ml: 1 }}>
            <Avatar sx={{ width: 36, height: 36, fontSize: '0.85rem', background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)' }}>
              {initials}
            </Avatar>
          </IconButton>

          <Menu
            anchorEl={profileAnchor}
            open={Boolean(profileAnchor)}
            onClose={() => setProfileAnchor(null)}
            PaperProps={{
              sx: {
                width: 220,
                mt: 1.5,
                background: 'rgba(15, 23, 42, 0.95)',
                backdropFilter: 'blur(20px)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '16px',
              }
            }}
          >
            <Box sx={{ px: 2, py: 1.5 }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 700 }}>{displayName}</Typography>
              <Typography variant="caption" color="text.secondary">{user?.email}</Typography>
            </Box>
            <Divider sx={{ borderColor: 'divider' }} />
            <MenuItem onClick={() => { setProfileAnchor(null); navigate('/profile'); }}>
              <ListItemIcon><Person fontSize="small" /></ListItemIcon>
              <ListItemText primary="Profile" />
            </MenuItem>
            <MenuItem onClick={() => { setProfileAnchor(null); navigate('/settings'); }}>
              <ListItemIcon><Settings fontSize="small" /></ListItemIcon>
              <ListItemText primary="Settings" />
            </MenuItem>
            <Divider sx={{ borderColor: 'divider' }} />
            <MenuItem onClick={handleLogout} sx={{ color: 'error.main' }}>
              <ListItemIcon><Logout fontSize="small" sx={{ color: 'error.main' }} /></ListItemIcon>
              <ListItemText primary="Logout" />
            </MenuItem>
          </Menu>
        </Box>
      </Toolbar>
    </AppBar>
  );
}
