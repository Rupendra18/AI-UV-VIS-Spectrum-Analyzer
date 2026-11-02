package com.uvvis.analyzer.data.repository

import com.uvvis.analyzer.data.model.AnalysisResult
import com.uvvis.analyzer.network.ApiClient
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import org.json.JSONObject
import java.io.File

class SpectrumRepository {

    suspend fun uploadSpectrumFile(file: File): Result<AnalysisResult> {
        return try {
            val requestFile = file.asRequestBody("text/csv".toMediaTypeOrNull())
            val body = MultipartBody.Part.createFormData("file", file.name, requestFile)
            val response = ApiClient.apiService.uploadSpectrum(body)
            if (response.isSuccessful) {
                val bodyData = response.body()
                if (bodyData != null && (bodyData.status == "success" || bodyData.status == "ok") && bodyData.analysis != null) {
                    Result.success(bodyData.analysis)
                } else {
                    Result.failure(Exception(bodyData?.error ?: "Upload failed: empty response from server"))
                }
            } else {
                val errMsg = parseErrorMessage(response.errorBody()?.string())
                    ?: "Upload failed with HTTP ${response.code()}"
                Result.failure(Exception(errMsg))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getHistory(): Result<List<AnalysisResult>> {
        return try {
            val response = ApiClient.apiService.getHistory()
            if (response.isSuccessful) {
                val bodyData = response.body()
                if (bodyData != null && (bodyData.status == "success" || bodyData.status == "ok")) {
                    Result.success(bodyData.history ?: emptyList())
                } else {
                    Result.failure(Exception(bodyData?.error ?: "Failed to fetch history"))
                }
            } else {
                val errMsg = parseErrorMessage(response.errorBody()?.string())
                    ?: "Failed to fetch history (HTTP ${response.code()})"
                Result.failure(Exception(errMsg))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun deleteHistory(id: String): Result<Boolean> {
        return try {
            val response = ApiClient.apiService.deleteHistory(id)
            if (response.isSuccessful) {
                Result.success(true)
            } else {
                val errMsg = parseErrorMessage(response.errorBody()?.string())
                    ?: "Delete failed (HTTP ${response.code()})"
                Result.failure(Exception(errMsg))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    companion object {
        fun parseErrorMessage(jsonStr: String?): String? {
            if (jsonStr.isNullOrBlank()) return null
            return try {
                val obj = JSONObject(jsonStr)
                when {
                    obj.has("error") -> obj.optString("error")
                    obj.has("message") -> obj.optString("message")
                    else -> jsonStr.take(120)
                }
            } catch (e: Exception) {
                jsonStr.take(120)
            }
        }
    }
}
