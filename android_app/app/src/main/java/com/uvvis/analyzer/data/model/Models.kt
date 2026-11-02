package com.uvvis.analyzer.data.model

import com.google.gson.annotations.SerializedName

data class SpectrumPoint(
    @SerializedName("Wavelength") val wavelength: Double = 0.0,
    @SerializedName("Absorbance") val absorbance: Double = 0.0
)

data class UserData(
    @SerializedName("id") val id: String? = null,
    @SerializedName("name") val name: String? = null,
    @SerializedName("email") val email: String? = null,
    @SerializedName("org_name") val orgName: String? = null,
    @SerializedName("role") val role: String? = null
)

data class AnalysisResult(
    @SerializedName("id") val id: String? = null,
    @SerializedName("filename") val filename: String? = null,
    @SerializedName("timestamp") val timestamp: String? = null,
    @SerializedName("peak_wavelength") val peakWavelength: Double = 0.0,
    @SerializedName("peak_absorbance") val peakAbsorbance: Double = 0.0,
    @SerializedName("predicted_concentration") val predictedConcentration: Double = 0.0,
    @SerializedName("status") val status: String = "UNKNOWN",
    @SerializedName("confidence_score") val confidenceScore: Double = 0.0,
    @SerializedName("algorithm") val algorithm: String? = null,
    @SerializedName("accuracy_percentage") val accuracyPercentage: Double? = null,
    @SerializedName("rmse") val rmse: Double? = null,
    @SerializedName("mae") val mae: Double? = null,
    @SerializedName("interpretation") val interpretation: String? = null,
    @SerializedName("conclusion") val conclusion: String? = null,
    @SerializedName("csv_url") val csvUrl: String? = null,
    @SerializedName("pdf_url") val pdfUrl: String? = null
)

data class ApiResponse<T>(
    @SerializedName("status") val status: String? = null,
    @SerializedName("analysis") val analysis: T? = null,
    @SerializedName("prediction") val prediction: T? = null,
    @SerializedName("history") val history: List<T>? = null,
    @SerializedName("reports") val reports: List<T>? = null,
    @SerializedName("error") val error: String? = null,
    @SerializedName("total") val total: Int? = null,
    @SerializedName("page") val page: Int? = null,
    @SerializedName("deleted") val deleted: String? = null
)

data class LoginResponse(
    @SerializedName("status") val status: String? = null,
    @SerializedName("uid") val uid: String? = null,
    @SerializedName("token") val token: String? = null,
    @SerializedName("error") val error: String? = null,
    @SerializedName("user") val user: UserData? = null
)
