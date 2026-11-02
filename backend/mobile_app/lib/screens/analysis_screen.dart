import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../widgets/glass_card.dart';
import '../widgets/spectrum_chart.dart';
import '../widgets/custom_button.dart';

class AnalysisScreen extends StatelessWidget {
  final String filename;
  final double peakWavelength;
  final double peakAbsorbance;
  final double concentration;
  final String status;

  const AnalysisScreen({
    Key? key,
    required this.filename,
    required this.peakWavelength,
    required this.peakAbsorbance,
    required this.concentration,
    required this.status,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final Color statusColor = status == 'SAFE'
        ? AppTheme.statusSafe
        : status == 'MODERATE'
            ? AppTheme.statusModerate
            : AppTheme.statusHigh;

    return Scaffold(
      backgroundColor: AppTheme.bgDark,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        title: Text('Analysis: $filename'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            GlassCard(
              child: Column(
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text('Peak Wavelength (λmax)', style: TextStyle(color: AppTheme.textMuted)),
                      Text('$peakWavelength nm', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
                    ],
                  ),
                  const Divider(color: AppTheme.glassBorder, height: 20),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text('Peak Absorbance', style: TextStyle(color: AppTheme.textMuted)),
                      Text('$peakAbsorbance AU', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
                    ],
                  ),
                  const Divider(color: AppTheme.glassBorder, height: 20),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text('Concentration', style: TextStyle(color: AppTheme.textMuted)),
                      Text('$concentration ppm', style: const TextStyle(color: AppTheme.secondaryCyan, fontWeight: FontWeight.bold, fontSize: 16)),
                    ],
                  ),
                  const Divider(color: AppTheme.glassBorder, height: 20),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text('Risk Classification', style: TextStyle(color: AppTheme.textMuted)),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                        decoration: BoxDecoration(
                          color: statusColor.withOpacity(0.2),
                          borderRadius: BorderRadius.circular(20),
                          border: Border.all(color: statusColor),
                        ),
                        child: Text(
                          status,
                          style: TextStyle(color: statusColor, fontWeight: FontWeight.bold),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
            GlassCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('UV-Vis Spectrum Graph', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 12),
                  SpectrumChart(peakWavelength: peakWavelength, peakAbsorbance: peakAbsorbance),
                ],
              ),
            ),
            const SizedBox(height: 24),
            CustomButton(
              label: 'Download PDF Report',
              icon: Icons.picture_as_pdf,
              onPressed: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Downloading report...')),
                );
              },
            ),
          ],
        ),
      ),
    );
  }
}
