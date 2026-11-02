import React from 'react';
import { Card, CardHeader, CardContent, Divider } from '@mui/material';
import { motion } from 'framer-motion';
import { glass } from '../theme/theme';

export default function GlassCard({ title, action, icon, children, sx = {}, hover = true, animate = true, ...props }) {
  const content = (
    <Card
      sx={{
        ...glass(0.06),
        borderRadius: '20px',
        overflow: 'hidden',
        transition: hover ? 'transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease' : 'none',
        '&:hover': hover ? {
          transform: 'translateY(-3px)',
          boxShadow: '0 20px 40px rgba(0,0,0,0.35), 0 0 20px rgba(59,130,246,0.15)',
          borderColor: 'rgba(59,130,246,0.3)',
        } : {},
        ...sx,
      }}
      {...props}
    >
      {(title || action) && (
        <>
          <CardHeader
            title={title}
            action={action}
            avatar={icon}
            titleTypographyProps={{
              variant: 'h6',
              fontWeight: 700,
              fontSize: '1.05rem',
              color: 'text.primary',
            }}
            sx={{ px: 3, py: 2 }}
          />
          <Divider sx={{ borderColor: 'rgba(255,255,255,0.06)' }} />
        </>
      )}
      <CardContent sx={{ p: 3, '&:last-child': { pb: 3 } }}>
        {children}
      </CardContent>
    </Card>
  );

  if (animate) {
    return (
      <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
        {content}
      </motion.div>
    );
  }

  return content;
}
