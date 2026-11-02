import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box, Typography, Table, TableBody, TableCell, TableHead, TableRow,
  Chip, IconButton, Tooltip, TextField, InputAdornment, MenuItem, Select, FormControl, InputLabel
} from '@mui/material';
import { History, Search, Visibility, Delete, PictureAsPdf } from '@mui/icons-material';
import GlassCard from '../components/GlassCard';
import LoadingSpinner from '../components/LoadingSpinner';
import NotificationToast from '../components/NotificationToast';
import api from '../services/api';

export default function HistoryPage() {
  const navigate = useNavigate();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [sortBy, setSortBy] = useState('date_desc');
  const [toast, setToast] = useState({ open: false, message: '', severity: 'info' });

  useEffect(() => {
    fetchHistory();
  }, [search, statusFilter, sortBy]);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const query = new URLSearchParams({
        search, status: statusFilter, sort_by: sortBy, per_page: 50
      }).toString();
      const res = await api.get(`/history?${query}`);
      if (res.data.status === 'success') {
        setHistory(res.data.history || []);
      }
    } catch (err) {
      console.error('Failed to load history:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this analysis entry?')) return;
    try {
      const res = await api.delete(`/history/${id}`);
      if (res.data.status === 'success') {
        setToast({ open: true, message: 'Analysis entry deleted.', severity: 'success' });
        fetchHistory();
      }
    } catch (err) {
      setToast({ open: true, message: 'Failed to delete record.', severity: 'error' });
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" fontWeight={800}>
          Spectral History Log
        </Typography>

        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <TextField
            placeholder="Search filename..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            size="small"
            sx={{ width: 220 }}
            InputProps={{
              startAdornment: <InputAdornment position="start"><Search fontSize="small" /></InputAdornment>,
            }}
          />

          <FormControl size="small" sx={{ width: 140 }}>
            <InputLabel>Status</InputLabel>
            <Select value={statusFilter} label="Status" onChange={(e) => setStatusFilter(e.target.value)}>
              <MenuItem value="">All Statuses</MenuItem>
              <MenuItem value="SAFE">Safe</MenuItem>
              <MenuItem value="MODERATE">Moderate</MenuItem>
              <MenuItem value="HIGH">High Risk</MenuItem>
            </Select>
          </FormControl>

          <FormControl size="small" sx={{ width: 160 }}>
            <InputLabel>Sort By</InputLabel>
            <Select value={sortBy} label="Sort By" onChange={(e) => setSortBy(e.target.value)}>
              <MenuItem value="date_desc">Newest First</MenuItem>
              <MenuItem value="date_asc">Oldest First</MenuItem>
              <MenuItem value="conc_desc">Conc (High→Low)</MenuItem>
              <MenuItem value="conc_asc">Conc (Low→High)</MenuItem>
            </Select>
          </FormControl>
        </Box>
      </Box>

      {loading ? (
        <LoadingSpinner message="Loading Spectral History..." />
      ) : (
        <GlassCard title={`Analysis History Log (${history.length})`} icon={<History sx={{ color: 'primary.main' }} />}>
          {history.length === 0 ? (
            <Box sx={{ py: 4, textAlign: 'center' }}>
              <Typography variant="body2" color="text.secondary">No spectral history entries found</Typography>
            </Box>
          ) : (
            <Box sx={{ overflowX: 'auto' }}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 700, color: 'text.secondary' }}>Date & Time</TableCell>
                    <TableCell sx={{ fontWeight: 700, color: 'text.secondary' }}>Filename</TableCell>
                    <TableCell sx={{ fontWeight: 700, color: 'text.secondary' }}>Peak (λmax)</TableCell>
                    <TableCell sx={{ fontWeight: 700, color: 'text.secondary' }}>Absorbance</TableCell>
                    <TableCell sx={{ fontWeight: 700, color: 'text.secondary' }}>Concentration</TableCell>
                    <TableCell sx={{ fontWeight: 700, color: 'text.secondary' }}>Status</TableCell>
                    <TableCell align="right" sx={{ fontWeight: 700, color: 'text.secondary' }}>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {history.map((row) => (
                    <TableRow key={row.id} hover>
                      <TableCell sx={{ fontSize: '0.85rem' }}>{row.timestamp}</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>{row.filename}</TableCell>
                      <TableCell sx={{ color: '#38bdf8' }}>{row.peak_wavelength} nm</TableCell>
                      <TableCell sx={{ color: '#8b5cf6' }}>{row.peak_absorbance} AU</TableCell>
                      <TableCell sx={{ fontWeight: 700, color: 'primary.main' }}>
                        {row.predicted_concentration} ppm
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={row.status}
                          size="small"
                          color={row.status === 'SAFE' ? 'success' : row.status === 'MODERATE' ? 'warning' : 'error'}
                          sx={{ fontWeight: 700 }}
                        />
                      </TableCell>
                      <TableCell align="right">
                        <Tooltip title="View Details">
                          <IconButton size="small" onClick={() => navigate(`/analysis/${row.id}`)}>
                            <Visibility fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Download PDF">
                          <IconButton size="small" color="error" onClick={() => window.open(`/api/reports/${row.id}/pdf`, '_blank')}>
                            <PictureAsPdf fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Delete Entry">
                          <IconButton size="small" color="default" onClick={() => handleDelete(row.id)}>
                            <Delete fontSize="small" />
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
      )}

      <NotificationToast open={toast.open} message={toast.message} severity={toast.severity} onClose={() => setToast({ ...toast, open: false })} />
    </Box>
  );
}
