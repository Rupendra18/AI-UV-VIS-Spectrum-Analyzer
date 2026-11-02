import React from 'react';
import Plot from 'react-plotly.js';
import { Box, Typography } from '@mui/material';

export default function SpectrumChart({ data, filename = 'spectrum', peakWavelength, peakAbsorbance, height = 400 }) {
  if (!data || data.length === 0) {
    return (
      <Box sx={{ height, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', p: 3, border: '2px dashed rgba(255,255,255,0.1)', borderRadius: '16px' }}>
        <Typography variant="body1" color="text.secondary">No spectrum data loaded</Typography>
        <Typography variant="caption" color="text.secondary">Upload a CSV file to render the UV-Vis absorbance graph</Typography>
      </Box>
    );
  }

  const wavelengths = data.map(d => d.Wavelength || d.wavelength);
  const absorbances = data.map(d => d.Absorbance || d.absorbance);

  // Peak marker logic
  const maxAbs = Math.max(...absorbances);
  const maxIdx = absorbances.indexOf(maxAbs);
  const peakW = peakWavelength ?? wavelengths[maxIdx];
  const peakA = peakAbsorbance ?? maxAbs;

  const plotData = [
    // Spectral curve
    {
      x: wavelengths,
      y: absorbances,
      type: 'scatter',
      mode: 'lines',
      name: 'Absorbance Spectrum',
      line: { color: '#3b82f6', width: 3, shape: 'spline' },
      fill: 'tozeroy',
      fillcolor: 'rgba(59, 130, 246, 0.1)',
      hovertemplate: 'Wavelength: %{x:.1f} nm<br>Absorbance: %{y:.4f} AU<extra></extra>',
    },
    // Red peak marker
    {
      x: [peakW],
      y: [peakA],
      type: 'scatter',
      mode: 'markers+text',
      name: `Peak λmax (${peakW} nm)`,
      marker: { color: '#ef4444', size: 12, symbol: 'diamond', line: { color: '#ffffff', width: 2 } },
      text: [`λmax = ${peakW} nm (${peakA} AU)`],
      textposition: 'top center',
      textfont: { color: '#ef4444', size: 12, family: 'Inter, sans-serif' },
      hovertemplate: '<b>Peak (λmax)</b><br>Wavelength: %{x:.1f} nm<br>Absorbance: %{y:.4f} AU<extra></extra>',
    }
  ];

  const layout = {
    autosize: true,
    height: height,
    margin: { l: 60, r: 30, t: 40, b: 60 },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: { family: 'Inter, sans-serif', color: '#94a3b8' },
    title: { text: filename, font: { size: 14, color: '#f8fafc' } },
    xaxis: {
      title: { text: 'Wavelength λ (nm)', font: { size: 12, color: '#f8fafc' } },
      gridcolor: 'rgba(255,255,255,0.06)',
      zerolinecolor: 'rgba(255,255,255,0.1)',
    },
    yaxis: {
      title: { text: 'Absorbance (AU)', font: { size: 12, color: '#f8fafc' } },
      gridcolor: 'rgba(255,255,255,0.06)',
      zerolinecolor: 'rgba(255,255,255,0.1)',
    },
    showlegend: true,
    legend: { x: 0.75, y: 0.95, font: { color: '#f8fafc' }, bgcolor: 'rgba(15,23,42,0.6)' },
  };

  const config = {
    responsive: true,
    displayModeBar: true,
    displaylogo: false,
    modeBarButtonsToRemove: ['lasso2d', 'select2d'],
    toImageButtonOptions: {
      format: 'png',
      filename: `${filename}_plot`,
      height: 700,
      width: 1200,
      scale: 3,
    },
  };

  return (
    <Box sx={{ width: '100%', height }}>
      <Plot data={plotData} layout={layout} config={config} style={{ width: '100%', height: '100%' }} />
    </Box>
  );
}
