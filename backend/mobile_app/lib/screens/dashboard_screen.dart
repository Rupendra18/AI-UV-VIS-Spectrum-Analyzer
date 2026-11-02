import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../widgets/glass_card.dart';
import '../widgets/spectrum_chart.dart';

class DashboardScreen extends StatelessWidget {
  const DashboardScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Stat Counters Grid
          Row(
            children: [
              Expanded(
                child: _buildStatCard('Total Analyses', '14', Icons.analytics_outlined, AppTheme.primaryBlue),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildStatCard('Safe Samples', '10', Icons.check_circle_outline, AppTheme.statusSafe),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: _buildStatCard('Moderate Risk', '3', Icons.warning_amber_rounded, AppTheme.statusModerate),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildStatCard('High Risk', '1', Icons.report_problem_outlined, AppTheme.statusHigh),
              ),
            ],
          ),
          const SizedBox(height: 20),

          // Active Spectrum Graph Card
          GlassCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: const [
                    Text('Active Spectrum', style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
                    Chip(
                      label: Text('λmax: 320 nm', style: TextStyle(color: Colors.white, fontSize: 12)),
                      backgroundColor: AppTheme.primaryBlue,
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                const SpectrumChart(peakWavelength: 320.0, peakAbsorbance: 0.854),
              ],
            ),
          ),
          const SizedBox(height: 20),

          // AI Insights & Metrics
          GlassCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: const [
                    Icon(Icons.auto_awesome, color: AppTheme.accentPurple),
                    SizedBox(width: 8),
                    Text('AI Prediction & Risk Insights', style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
                  ],
                ),
                const Divider(color: AppTheme.glassBorder, height: 24),
                _buildMetricRow('Predicted Concentration', '10.68 ppm'),
                _buildMetricRow('AI Confidence Score', '94.2%'),
                _buildMetricRow('Risk Status', 'SAFE', color: AppTheme.statusSafe),
                const SizedBox(height: 12),
                const Text(
                  'The spectral analysis displays a characteristic peak at 320.0 nm in the UV-A band. Signal-to-noise ratio confirms high confidence.',
                  style: TextStyle(color: AppTheme.textMuted, fontSize: 13),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatCard(String label, String value, IconData icon, Color color) {
    return GlassCard(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(height: 10),
          Text(value, style: TextStyle(color: Colors.white, fontSize: 22, fontWeight: FontWeight.bold)),
          Text(label, style: const TextStyle(color: AppTheme.textMuted, fontSize: 12)),
        ],
      ),
    );
  }

  Widget _buildMetricRow(String title, String val, {Color? color}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(title, style: const TextStyle(color: AppTheme.textMuted, fontSize: 14)),
          Text(val, style: TextStyle(color: color ?? Colors.white, fontWeight: FontWeight.bold, fontSize: 14)),
        ],
      ),
    );
  }
}
