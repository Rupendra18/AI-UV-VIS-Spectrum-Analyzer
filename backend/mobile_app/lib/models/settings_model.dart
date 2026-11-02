class SettingsModel {
  final String orgName;
  final String scientistName;
  final double safeLimit;
  final double concentrationFactor;
  final String theme;

  SettingsModel({
    this.orgName = 'My Laboratory',
    this.scientistName = 'Scientist',
    this.safeLimit = 5.0,
    this.concentrationFactor = 12.5,
    this.theme = 'dark',
  });

  factory SettingsModel.fromJson(Map<String, dynamic> json) {
    return SettingsModel(
      orgName: json['org_name']?.toString() ?? 'My Laboratory',
      scientistName: json['scientist_name']?.toString() ?? 'Scientist',
      safeLimit: (json['safe_limit'] as num?)?.toDouble() ?? 5.0,
      concentrationFactor: (json['concentration_factor'] as num?)?.toDouble() ?? 12.5,
      theme: json['theme']?.toString() ?? 'dark',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'org_name': orgName,
      'scientist_name': scientistName,
      'safe_limit': safeLimit,
      'concentration_factor': concentrationFactor,
      'theme': theme,
    };
  }
}
