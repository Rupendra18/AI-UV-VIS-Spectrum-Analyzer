import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Box } from '@mui/material';
import Navbar from '../Navbar';
import Sidebar from '../Sidebar';

const SIDEBAR_WIDTH = 260;
const SIDEBAR_COLLAPSED = 72;

export default function AppLayout({ darkMode, setDarkMode }) {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <Sidebar
        open={sidebarOpen}
        width={SIDEBAR_WIDTH}
        collapsedWidth={SIDEBAR_COLLAPSED}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
      />
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          ml: `${sidebarOpen ? SIDEBAR_WIDTH : SIDEBAR_COLLAPSED}px`,
          transition: 'margin 0.3s ease',
          display: 'flex',
          flexDirection: 'column',
          minHeight: '100vh',
        }}
      >
        <Navbar darkMode={darkMode} setDarkMode={setDarkMode} sidebarOpen={sidebarOpen} />
        <Box sx={{ flexGrow: 1, p: { xs: 2, sm: 3 }, mt: '64px' }}>
          <Outlet />
        </Box>
      </Box>
    </Box>
  );
}
