class UserModel {
  final String id;
  final String name;
  final String email;
  final String orgName;
  final String role;

  UserModel({
    required this.id,
    required this.name,
    required this.email,
    required this.orgName,
    this.role = 'User',
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id']?.toString() ?? '',
      name: json['name']?.toString() ?? 'Scientist',
      email: json['email']?.toString() ?? '',
      orgName: json['org_name']?.toString() ?? 'Laboratory',
      role: json['role']?.toString() ?? 'User',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'email': email,
      'org_name': orgName,
      'role': role,
    };
  }
}
