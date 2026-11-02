import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box, Typography, Table, TableBody, TableCell, TableHead, TableRow,
  Chip, Button, IconButton, Tooltip, InputAdornment, TextField
} from '@mui/material';
import { PictureAsPdf, Download, Search, Visibility } from '@mui/icons-material';
import GlassCard from '../components/GlassCard';
import LoadingSpinner from '../components/LoadingSpinner';
import api from '../services/api';

export default function ReportsPage() {
  const navigate = useNavigate();
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    fetchReports();
  }, []);

  const fetchReports = async () => {
    setLoading(true);
    try {
      const res = await api.get('/reports');
      if (res.data.status === 'success') {
        setReports(res.data.reports || []);
      }
    } catch (err) {
      console.error('Failed to load reports:', err);
    } finally {
      setLoading(false);
    }
  };

  const filteredReports = reports.filter((r) =>
    r.filename?.toLowerCase().includes(search.toLowerCase()) ||
    r.status?.toLowerCase().includes(search.toLowerCase())
  );

  if (loading) return <LoadingSpinner message="Loading Reports..." />;

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" fontWeight={800}>
          Analysis PDF Reports
        </Typography>
        <TextField
          placeholder="Search reports..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          size="small"
          sx={{ width: 260 }}
          InputProps={{
            startAdornment: <InputAdornment position="start"><Search fontSize="small" /></InputAdornment>,
          }}
        />
      </Box>

      <GlassCard title={`All Generated Reports (${filteredReports.length})`} icon={<PictureAsPdf sx={{ color: 'error.main' }} />}>
        {filteredReports.length === 0 ? (
          <Box sx={{ py: 4, textAlign: 'center' }}>
            <Typography variant="body2" color="text.secondary">No reports match your search criteria</Typography>
          </Box>
        ) : (
          <Box sx={{ overflowX: 'auto' }}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell sx={{ fontWeight: 700, color: 'text.secondary' }}>Date & Time</TableCell>
                  <TableCell sx={{ fontWeight: 700, color: 'text.secondary' }}>Filename</TableCell>
                  <TableCell sx={{ fontWeight: 700, color: 'text.secondary' }}>Algorithm</TableCell>
                  <TableCell sx={{ fontWeight: 700, color: 'text.secondary' }}>Status</TableCell>
                  <TableCell sx={{ fontWeight: 700, color: 'text.secondary' }}>Concentration</TableCell>
                  <TableCell align="right" sx={{ fontWeight: 700, color: 'text.secondary' }}>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredReports.map((row) => (
                  <TableRow key={row.id} hover>
                    <TableCell sx={{ fontSize: '0.85rem' }}>{row.timestamp}</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>{row.filename}</TableCell>
                    <TableCell sx={{ fontSize: '0.85rem', color: '#a78bfa' }}>{row.algorithm}</TableCell>
                    <TableCell>
                      <Chip
                        label={row.status}
                        size="small"
                        color={row.status === 'SAFE' ? 'success' : row.status === 'MODERATE' ? 'warning' : 'error'}
                        sx={{ fontWeight: 700 }}
                      />
                    </TableCell>
                    <TableCell sx={{ fontWeight: 700, color: 'primary.main' }}>
                      {row.predicted_concentration} ppm
                    </TableCell>
                    <TableCell align="right">
                      <Tooltip title="View Analysis">
                        <IconButton size="small" onClick={() => navigate(`/analysis/${row.id}`)}>
                          <Visibility fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Download PDF">
                        <IconButton size="small" color="error" onClick={() => window.open(`/api/reports/${row.id}/pdf`, '_blank')}>
                          <PictureAsPdf fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Export CSV">
                        <IconButton size="small" color="primary" onClick={() => window.open(`/api/reports/${row.id}/csv`, '_blank')}>
                          <Download fontSize="small" />
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
    </Box>
  );
}
