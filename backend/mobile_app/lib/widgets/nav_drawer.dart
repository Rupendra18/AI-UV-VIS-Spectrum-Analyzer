import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class NavDrawer extends StatelessWidget {
  final int selectedIndex;
  final Function(int) onDestinationSelected;

  const NavDrawer({
    Key? key,
    required this.selectedIndex,
    required this.onDestinationSelected,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Drawer(
      backgroundColor: AppTheme.bgDark,
      child: ListView(
        padding: EdgeInsets.zero,
        children: [
          DrawerHeader(
            decoration: const BoxDecoration(
              gradient: LinearGradient(
                colors: [AppTheme.primaryBlue, AppTheme.accentPurple],
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.center,
              children: const [
                Icon(Icons.biotech, size: 40, color: Colors.white),
                SizedBox(height: 10),
                Text(
                  'AI UV-Vis Analyzer',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  'Spectral Intelligence Suite',
                  style: TextStyle(color: Colors.white70, fontSize: 12),
                ),
              ],
            ),
          ),
          ListTile(
            leading: const Icon(Icons.dashboard_rounded, color: AppTheme.primaryBlue),
            title: const Text('Dashboard'),
            selected: selectedIndex == 0,
            onTap: () => onDestinationSelected(0),
          ),
          ListTile(
            leading: const Icon(Icons.cloud_upload_rounded, color: AppTheme.secondaryCyan),
            title: const Text('Upload CSV'),
            selected: selectedIndex == 1,
            onTap: () => onDestinationSelected(1),
          ),
          ListTile(
            leading: const Icon(Icons.history_rounded, color: AppTheme.accentPurple),
            title: const Text('History'),
            selected: selectedIndex == 2,
            onTap: () => onDestinationSelected(2),
          ),
          ListTile(
            leading: const Icon(Icons.description_rounded, color: AppTheme.statusSafe),
            title: const Text('Reports'),
            selected: selectedIndex == 3,
            onTap: () => onDestinationSelected(3),
          ),
          ListTile(
            leading: const Icon(Icons.settings_rounded, color: AppTheme.textMuted),
            title: const Text('Settings'),
            selected: selectedIndex == 4,
            onTap: () => onDestinationSelected(4),
          ),
        ],
      ),
    );
  }
}
