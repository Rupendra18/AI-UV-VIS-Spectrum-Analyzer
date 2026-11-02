import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../widgets/glass_card.dart';
import '../widgets/custom_button.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({Key? key}) : super(key: key);

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  final _orgController = TextEditingController(text: "My Laboratory");
  final _nameController = TextEditingController(text: "Scientist");
  final _safeLimitController = TextEditingController(text: "5.0");
  final _factorController = TextEditingController(text: "12.5");

  void _saveSettings() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Settings saved successfully!')),
    );
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          GlassCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('Analyzer Parameters', style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
                const SizedBox(height: 16),
                TextField(
                  controller: _orgController,
                  decoration: const InputDecoration(labelText: 'Organization Name'),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: _nameController,
                  decoration: const InputDecoration(labelText: 'Scientist Name'),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: _safeLimitController,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(labelText: 'Safe Limit Threshold (ppm)'),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: _factorController,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(labelText: 'Concentration Factor'),
                ),
                const SizedBox(height: 20),
                CustomButton(
                  label: 'Save Configuration',
                  onPressed: _saveSettings,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
