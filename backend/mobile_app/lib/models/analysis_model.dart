class AnalysisModel {
  final String id;
  final String timestamp;
  final String filename;
  final double peakWavelength;
  final double peakAbsorbance;
  final double predictedConcentration;
  final String status;
  final double confidenceScore;
  final String interpretation;
  final String conclusion;
  final String csvUrl;
  final String pdfUrl;

  AnalysisModel({
    required this.id,
    required this.timestamp,
    required this.filename,
    required this.peakWavelength,
    required this.peakAbsorbance,
    required this.predictedConcentration,
    required this.status,
    required this.confidenceScore,
    required this.interpretation,
    required this.conclusion,
    this.csvUrl = '',
    this.pdfUrl = '',
  });

  factory AnalysisModel.fromJson(Map<String, dynamic> json) {
    return AnalysisModel(
      id: json['id']?.toString() ?? '',
      timestamp: json['timestamp']?.toString() ?? '',
      filename: json['filename']?.toString() ?? 'Sample.csv',
      peakWavelength: (json['peak_wavelength'] as num?)?.toDouble() ?? 0.0,
      peakAbsorbance: (json['peak_absorbance'] as num?)?.toDouble() ?? 0.0,
      predictedConcentration: (json['predicted_concentration'] as num?)?.toDouble() ?? 0.0,
      status: json['status']?.toString() ?? 'SAFE',
      confidenceScore: (json['confidence_score'] as num?)?.toDouble() ?? 75.0,
      interpretation: json['interpretation']?.toString() ?? '',
      conclusion: json['conclusion']?.toString() ?? '',
      csvUrl: json['csv_url']?.toString() ?? '',
      pdfUrl: json['pdf_url']?.toString() ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'timestamp': timestamp,
      'filename': filename,
      'peak_wavelength': peakWavelength,
      'peak_absorbance': peakAbsorbance,
      'predicted_concentration': predictedConcentration,
      'status': status,
      'confidence_score': confidenceScore,
      'interpretation': interpretation,
      'conclusion': conclusion,
      'csv_url': csvUrl,
      'pdf_url': pdfUrl,
    };
  }
}
