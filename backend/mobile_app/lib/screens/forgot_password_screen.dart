import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../widgets/glass_card.dart';
import '../widgets/custom_button.dart';

class ForgotPasswordScreen extends StatefulWidget {
  const ForgotPasswordScreen({Key? key}) : super(key: key);

  @override
  State<ForgotPasswordScreen> createState() => _ForgotPasswordScreenState();
}

class _ForgotPasswordScreenState extends State<ForgotPasswordScreen> {
  final _emailController = TextEditingController();
  bool _sent = false;

  void _reset() {
    if (_emailController.text.isNotEmpty) {
      setState(() => _sent = true);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.bgDark,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        title: const Text('Reset Password'),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: GlassCard(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                if (_sent) ...[
                  const Icon(Icons.check_circle_outline, color: AppTheme.statusSafe, size: 60),
                  const SizedBox(height: 16),
                  const Text(
                    'Reset Link Sent',
                    style: TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'Check your email inbox for instructions to reset your password.',
                    textAlign: TextAlign.center,
                    style: TextStyle(color: AppTheme.textMuted),
                  ),
                  const SizedBox(height: 24),
                  CustomButton(
                    label: 'Back to Login',
                    onPressed: () => Navigator.pop(context),
                  ),
                ] else ...[
                  const Text(
                    'Enter your registered email address to receive password recovery instructions.',
                    style: TextStyle(color: AppTheme.textMuted),
                  ),
                  const SizedBox(height: 20),
                  TextField(
                    controller: _emailController,
                    decoration: const InputDecoration(
                      labelText: 'Email Address',
                      prefixIcon: Icon(Icons.email_outlined, color: AppTheme.textMuted),
                    ),
                  ),
                  const SizedBox(height: 24),
                  CustomButton(
                    label: 'Send Recovery Email',
                    onPressed: _reset,
                  ),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
}
