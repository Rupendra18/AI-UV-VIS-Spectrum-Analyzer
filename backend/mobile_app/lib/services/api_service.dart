import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import '../models/analysis_model.dart';
import '../models/settings_model.dart';

class ApiService {
  // Configurable host address: defaults to active Wi-Fi LAN IP (192.168.137.254)
  static String baseUrl = 'http://192.168.137.254:5000/api';
  static String token = '';

  static Future<Map<String, dynamic>> login(String email, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/login'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'email': email, 'password': password}),
      ).timeout(const Duration(seconds: 10));

      final data = json.decode(response.body);
      if (response.statusCode == 200 && (data['status'] == 'ok' || data['status'] == 'success')) {
        token = data['token'] ?? '';
        return {'success': true, 'data': data};
      }
      return {'success': false, 'error': data['error'] ?? 'Invalid credentials'};
    } catch (e) {
      return {'success': false, 'error': e.toString()};
    }
  }

  static Future<Map<String, dynamic>> register(String name, String org, String email, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/register'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'name': name,
          'org_name': org,
          'email': email,
          'password': password,
        }),
      ).timeout(const Duration(seconds: 10));

      final data = json.decode(response.body);
      if ((response.statusCode == 200 || response.statusCode == 201) &&
          (data['status'] == 'ok' || data['status'] == 'success')) {
        token = data['token'] ?? '';
        return {'success': true, 'data': data};
      }
      return {'success': false, 'error': data['error'] ?? 'Registration failed'};
    } catch (e) {
      return {'success': false, 'error': e.toString()};
    }
  }

  static Future<AnalysisModel?> uploadCsv(File file) async {
    try {
      final request = http.MultipartRequest('POST', Uri.parse('$baseUrl/upload'));
      if (token.isNotEmpty) {
        request.headers['Authorization'] = 'Bearer $token';
      }
      request.files.add(await http.MultipartFile.fromPath('file', file.path));

      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        if (data['status'] == 'success' && data['analysis'] != null) {
          return AnalysisModel.fromJson(data['analysis']);
        }
      }
    } catch (e) {
      print("API upload error: $e");
    }
    return null;
  }

  static Future<List<AnalysisModel>> fetchHistory({String search = '', String status = ''}) async {
    try {
      final uri = Uri.parse('$baseUrl/history').replace(queryParameters: {
        if (search.isNotEmpty) 'search': search,
        if (status.isNotEmpty) 'status': status,
      });

      final headers = <String, String>{};
      if (token.isNotEmpty) {
        headers['Authorization'] = 'Bearer $token';
      }

      final response = await http.get(uri, headers: headers);
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        if (data['status'] == 'success' && data['history'] != null) {
          final List list = data['history'];
          return list.map((item) => AnalysisModel.fromJson(item)).toList();
        }
      }
    } catch (e) {
      print("API history error: $e");
    }
    return [];
  }

  static Future<SettingsModel?> fetchSettings() async {
    try {
      final headers = <String, String>{};
      if (token.isNotEmpty) {
        headers['Authorization'] = 'Bearer $token';
      }
      final response = await http.get(Uri.parse('$baseUrl/settings'), headers: headers);
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        if (data['status'] == 'success' && data['settings'] != null) {
          return SettingsModel.fromJson(data['settings']);
        }
      }
    } catch (e) {
      print("API settings error: $e");
    }
    return null;
  }

  static Future<bool> updateSettings(SettingsModel settings) async {
    try {
      final headers = {'Content-Type': 'application/json'};
      if (token.isNotEmpty) {
        headers['Authorization'] = 'Bearer $token';
      }
      final response = await http.post(
        Uri.parse('$baseUrl/settings'),
        headers: headers,
        body: json.encode(settings.toJson()),
      );
      return response.statusCode == 200;
    } catch (e) {
      print("API settings update error: $e");
      return false;
    }
  }
}
