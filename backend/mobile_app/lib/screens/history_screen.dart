import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../widgets/glass_card.dart';

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({Key? key}) : super(key: key);

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  String _searchQuery = '';

  final List<Map<String, dynamic>> _mockHistory = [
    {
      'filename': 'water_sample_01.csv',
      'timestamp': '2026-08-19 10:30',
      'peak': '280.0 nm',
      'conc': '3.42 ppm',
      'status': 'SAFE',
    },
    {
      'filename': 'industrial_effluent.csv',
      'timestamp': '2026-08-18 16:45',
      'peak': '345.5 nm',
      'conc': '14.20 ppm',
      'status': 'HIGH',
    },
    {
      'filename': 'river_monitoring_b.csv',
      'timestamp': '2026-08-18 11:15',
      'peak': '312.0 nm',
      'conc': '7.85 ppm',
      'status': 'MODERATE',
    },
  ];

  @override
  Widget build(BuildContext context) {
    final filtered = _mockHistory.where((item) {
      return item['filename'].toLowerCase().contains(_searchQuery.toLowerCase()) ||
          item['status'].toLowerCase().contains(_searchQuery.toLowerCase());
    }).toList();

    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          TextField(
            onChanged: (val) => setState(() => _searchQuery = val),
            decoration: const InputDecoration(
              hintText: 'Search by filename or risk status...',
              prefixIcon: Icon(Icons.search, color: AppTheme.textMuted),
            ),
          ),
          const SizedBox(height: 16),
          Expanded(
            child: ListView.builder(
              itemCount: filtered.length,
              itemBuilder: (context, index) {
                final item = filtered[index];
                final String st = item['status'];
                final Color stColor = st == 'SAFE'
                    ? AppTheme.statusSafe
                    : st == 'MODERATE'
                        ? AppTheme.statusModerate
                        : AppTheme.statusHigh;

                return GlassCard(
                  margin: const EdgeInsets.only(bottom: 12),
                  child: ListTile(
                    contentPadding: EdgeInsets.zero,
                    leading: Container(
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: stColor.withOpacity(0.15),
                        shape: BoxShape.circle,
                      ),
                      child: Icon(Icons.show_chart, color: stColor),
                    ),
                    title: Text(item['filename'], style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                    subtitle: Text('${item['timestamp']} • λmax: ${item['peak']}', style: const TextStyle(color: AppTheme.textMuted, fontSize: 12)),
                    trailing: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: [
                        Text(item['conc'], style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                        Text(st, style: TextStyle(color: stColor, fontSize: 11, fontWeight: FontWeight.bold)),
                      ],
                    ),
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
