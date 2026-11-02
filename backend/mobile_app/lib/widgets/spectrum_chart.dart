import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../theme/app_theme.dart';

class SpectrumChart extends StatelessWidget {
  final double peakWavelength;
  final double peakAbsorbance;

  const SpectrumChart({
    Key? key,
    required this.peakWavelength,
    required this.peakAbsorbance,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    // Generate synthetic Gaussian curve around peak for visualization
    final List<FlSpot> spots = [];
    final double minW = (peakWavelength - 150).clamp(200, 800);
    final double maxW = (peakWavelength + 150).clamp(200, 900);
    final double step = (maxW - minW) / 40;

    for (double x = minW; x <= maxW; x += step) {
      final double dist = (x - peakWavelength) / 35;
      final double y = peakAbsorbance * (0.1 + 0.9 * (1.0 / (1.0 + dist * dist)));
      spots.add(FlSpot(x, double.parse(y.toStringAsFixed(4))));
    }

    return Container(
      height: 220,
      padding: const EdgeInsets.only(right: 18, top: 12, bottom: 6),
      child: LineChart(
        LineChartData(
          gridData: FlGridData(
            show: true,
            getDrawingHorizontalLine: (value) => FlLine(color: AppTheme.glassBorder, strokeWidth: 1),
            getDrawingVerticalLine: (value) => FlLine(color: AppTheme.glassBorder, strokeWidth: 1),
          ),
          titlesData: FlTitlesData(
            show: true,
            topTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
            rightTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
            leftTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                reservedSize: 36,
                getTitlesWidget: (val, meta) => Text(
                  val.toStringAsFixed(1),
                  style: const TextStyle(color: AppTheme.textMuted, fontSize: 10),
                ),
              ),
            ),
            bottomTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                reservedSize: 24,
                getTitlesWidget: (val, meta) => Text(
                  '${val.toInt()}nm',
                  style: const TextStyle(color: AppTheme.textMuted, fontSize: 10),
                ),
              ),
            ),
          ),
          borderData: FlBorderData(show: false),
          minX: minW,
          maxX: maxW,
          minY: 0,
          maxY: peakAbsorbance * 1.2,
          lineBarsData: [
            LineChartBarData(
              spots: spots,
              isCurved: true,
              color: AppTheme.primaryBlue,
              barWidth: 3,
              isStrokeCapRound: true,
              dotData: FlDotData(
                show: true,
                checkToShowDot: (spot, barData) => (spot.x - peakWavelength).abs() < (step / 2),
                getDotPainter: (spot, percent, barData, index) {
                  return FlDotCirclePainter(
                    radius: 7,
                    color: AppTheme.statusHigh,
                    strokeWidth: 2,
                    strokeColor: Colors.white,
                  );
                },
              ),
              belowBarData: BarAreaData(
                show: true,
                color: AppTheme.primaryBlue.withOpacity(0.15),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
