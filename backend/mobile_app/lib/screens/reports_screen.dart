import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../widgets/glass_card.dart';

class ReportsScreen extends StatelessWidget {
  const ReportsScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('PDF & Data Reports', style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          const Text('Download or share compiled PDF reports for all past analyses.', style: TextStyle(color: AppTheme.textMuted, fontSize: 13)),
          const SizedBox(height: 16),
          Expanded(
            child: ListView.builder(
              itemCount: 3,
              itemBuilder: (context, index) {
                final names = ['water_sample_01.csv', 'industrial_effluent.csv', 'river_monitoring_b.csv'];
                final dates = ['2026-08-19', '2026-08-18', '2026-08-18'];

                return GlassCard(
                  margin: const EdgeInsets.only(bottom: 12),
                  child: Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: const BoxDecoration(
                          color: Color(0x22EF4444),
                          borderRadius: BorderRadius.all(Radius.circular(12)),
                        ),
                        child: const Icon(Icons.picture_as_pdf, color: AppTheme.statusHigh, size: 28),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(names[index], style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                            Text('Report #${101 + index} • ${dates[index]}', style: const TextStyle(color: AppTheme.textMuted, fontSize: 12)),
                          ],
                        ),
                      ),
                      IconButton(
                        icon: const Icon(Icons.download, color: AppTheme.primaryBlue),
                        onPressed: () {
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(content: Text('Downloading Report #${101 + index}...')),
                          );
                        },
                      ),
                      IconButton(
                        icon: const Icon(Icons.share, color: AppTheme.secondaryCyan),
                        onPressed: () {
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(content: Text('Sharing Report #${101 + index}...')),
                          );
                        },
                      ),
                    ],
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
