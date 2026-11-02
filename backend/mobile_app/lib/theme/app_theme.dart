import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTheme {
  // Dark glass theme colors
  static const Color bgDark = Color(0xFF090D16);
  static const Color primaryBlue = Color(0xFF3B82F6);
  static const Color secondaryCyan = Color(0xFF38BDF8);
  static const Color accentPurple = Color(0xFF8B5CF6);
  static const Color glassCardBg = Color(0x990F172A);
  static const Color glassBorder = Color(0x20FFFFFF);
  static const Color textLight = Color(0xFFF8FAFC);
  static const Color textMuted = Color(0xFF94A3B8);

  static const Color statusSafe = Color(0xFF10B981);
  static const Color statusModerate = Color(0xFFF59E0B);
  static const Color statusHigh = Color(0xFFEF4444);

  static ThemeData get darkTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      scaffoldBackgroundColor: bgDark,
      primaryColor: primaryBlue,
      colorScheme: const ColorScheme.dark(
        primary: primaryBlue,
        secondary: secondaryCyan,
        tertiary: accentPurple,
        surface: glassCardBg,
        background: bgDark,
        error: statusHigh,
      ),
      textTheme: TextTheme(
        displayLarge: GoogleFonts.outfit(fontSize: 32, fontWeight: FontWeight.bold, color: textLight),
        titleLarge: GoogleFonts.outfit(fontSize: 22, fontWeight: FontWeight.w700, color: textLight),
        titleMedium: GoogleFonts.outfit(fontSize: 18, fontWeight: FontWeight.w600, color: textLight),
        bodyLarge: GoogleFonts.plusJakartaSans(fontSize: 15, color: textLight),
        bodyMedium: GoogleFonts.plusJakartaSans(fontSize: 13, color: textMuted),
      ),
      cardTheme: CardTheme(
        color: glassCardBg,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: const BorderSide(color: glassBorder, width: 1),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: const Color(0x330F172A),
        contentPadding: const EdgeInsets.symmetric(horizontal: 18, vertical: 16),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: glassBorder),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: glassBorder),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: primaryBlue, width: 1.5),
        ),
        labelStyle: const TextStyle(color: textMuted),
        hintStyle: const TextStyle(color: Color(0xFF64748B)),
      ),
    );
  }
}
