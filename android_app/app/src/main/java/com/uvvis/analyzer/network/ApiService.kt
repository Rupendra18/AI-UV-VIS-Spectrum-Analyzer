package com.uvvis.analyzer.network

import com.uvvis.analyzer.data.model.AnalysisResult
import com.uvvis.analyzer.data.model.ApiResponse
import com.uvvis.analyzer.data.model.LoginResponse
import okhttp3.MultipartBody
import retrofit2.Response
import retrofit2.http.*

interface ApiService {

    @GET("api/health")
    suspend fun checkHealth(): Response<Map<String, Any>>

    @POST("api/auth/login")
    suspend fun login(
        @Body body: Map<String, String>
    ): Response<LoginResponse>

    @POST("api/auth/register")
    suspend fun register(
        @Body body: Map<String, String>
    ): Response<LoginResponse>

    @POST("api/auth/logout")
    suspend fun logout(): Response<Map<String, Any>>

    @Multipart
    @POST("api/upload")
    suspend fun uploadSpectrum(
        @Part file: MultipartBody.Part
    ): Response<ApiResponse<AnalysisResult>>

    @GET("api/history")
    suspend fun getHistory(
        @Query("search") search: String? = null,
        @Query("status") status: String? = null,
        @Query("sort_by") sortBy: String? = "date_desc"
    ): Response<ApiResponse<AnalysisResult>>

    @DELETE("api/history/{id}")
    suspend fun deleteHistory(
        @Path("id") id: String
    ): Response<Map<String, Any>>
}
