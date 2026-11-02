import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../widgets/glass_card.dart';
import '../widgets/custom_button.dart';
import 'analysis_screen.dart';

class UploadScreen extends StatefulWidget {
  const UploadScreen({Key? key}) : super(key: key);

  @override
  State<UploadScreen> createState() => _UploadScreenState();
}

class _UploadScreenState extends State<UploadScreen> {
  bool _isUploading = false;
  String? _selectedFileName;

  void _pickAndAnalyze() {
    setState(() {
      _selectedFileName = "sample_spectrum.csv";
      _isUploading = true;
    });

    Future.delayed(const Duration(milliseconds: 1200), () {
      if (mounted) {
        setState(() => _isUploading = false);
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (_) => const AnalysisScreen(
              filename: "sample_spectrum.csv",
              peakWavelength: 318.5,
              peakAbsorbance: 0.942,
              concentration: 11.78,
              status: "MODERATE",
            ),
          ),
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          GlassCard(
            padding: const EdgeInsets.all(32),
            child: Column(
              children: [
                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: const BoxDecoration(
                    color: Color(0x223B82F6),
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(Icons.cloud_upload_outlined, size: 64, color: AppTheme.primaryBlue),
                ),
                const SizedBox(height: 20),
                const Text(
                  'Upload Spectral CSV File',
                  style: TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),
                const Text(
                  'File must contain "Wavelength" and "Absorbance" columns.',
                  textAlign: TextAlign.center,
                  style: TextStyle(color: AppTheme.textMuted, fontSize: 13),
                ),
                const SizedBox(height: 24),
                if (_selectedFileName != null) ...[
                  Chip(
                    avatar: const Icon(Icons.description, color: AppTheme.secondaryCyan, size: 18),
                    label: Text(_selectedFileName!),
                    backgroundColor: AppTheme.glassCardBg,
                  ),
                  const SizedBox(height: 16),
                ],
                CustomButton(
                  label: 'Select CSV & Analyze',
                  icon: Icons.analytics_outlined,
                  isLoading: _isUploading,
                  onPressed: _pickAndAnalyze,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
