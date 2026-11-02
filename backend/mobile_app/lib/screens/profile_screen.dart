import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../widgets/glass_card.dart';
import '../widgets/custom_button.dart';
import 'login_screen.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.bgDark,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        title: const Text('User Profile'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            GlassCard(
              child: Column(
                children: [
                  const CircleAvatar(
                    radius: 40,
                    backgroundColor: AppTheme.primaryBlue,
                    child: Icon(Icons.person, size: 48, color: Colors.white),
                  ),
                  const SizedBox(height: 16),
                  const Text('Dr. Scientist', style: TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold)),
                  const Text('scientist@lab.org', style: TextStyle(color: AppTheme.textMuted)),
                  const SizedBox(height: 8),
                  Chip(
                    label: const Text('Lead Analyst'),
                    backgroundColor: AppTheme.primaryBlue.withOpacity(0.2),
                    side: const BorderSide(color: AppTheme.primaryBlue),
                  ),
                ],
              ),
            ),
            const Spacer(),
            CustomButton(
              label: 'Sign Out',
              color: AppTheme.statusHigh,
              icon: Icons.logout,
              onPressed: () {
                Navigator.of(context).pushAndRemoveUntil(
                  MaterialPageRoute(builder: (_) => const LoginScreen()),
                  (route) => false,
                );
              },
            ),
          ],
        ),
      ),
    );
  }
}
