package com.uvvis.analyzer.network

import android.content.Context
import android.content.SharedPreferences
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

object ApiClient {
    private const val PREFS_NAME = "uvvis_prefs"
    private const val KEY_BASE_URL = "base_url"
    private const val KEY_AUTH_TOKEN = "auth_token"
    private const val KEY_USER_NAME = "user_name"
    private const val KEY_USER_EMAIL = "user_email"

    // Default to the computer's current Wi-Fi LAN IP address
    const val DEFAULT_BASE_URL = "http://192.168.137.254:5000/"

    private var currentBaseUrl: String = DEFAULT_BASE_URL
    private var authToken: String? = null
    private var _apiService: ApiService? = null
    private var prefs: SharedPreferences? = null

    fun init(context: Context) {
        prefs = context.applicationContext.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        val savedUrl = prefs?.getString(KEY_BASE_URL, null)

        // If saved URL is missing, or contains stale/localhost/obsolete IP, migrate to current laptop IP
        if (savedUrl.isNullOrBlank() ||
            savedUrl.contains("127.0.0.1") ||
            savedUrl.contains("localhost") ||
            savedUrl.contains("10.0.2.2") ||
            savedUrl.contains("192.168.1.13") ||
            savedUrl.contains("10.55.51.164")
        ) {
            currentBaseUrl = DEFAULT_BASE_URL
            prefs?.edit()?.putString(KEY_BASE_URL, currentBaseUrl)?.apply()
        } else {
            currentBaseUrl = ensureTrailingSlash(savedUrl)
        }

        authToken = prefs?.getString(KEY_AUTH_TOKEN, null)
        buildRetrofit()
    }

    fun ensureTrailingSlash(url: String): String {
        var clean = url.trim().replace("\"", "").replace("'", "")
        if (!clean.startsWith("http://") && !clean.startsWith("https://")) {
            clean = "http://$clean"
        }
        if (!clean.endsWith("/")) {
            clean += "/"
        }
        return clean
    }

    fun getBaseUrl(): String = currentBaseUrl

    fun updateBaseUrl(newUrl: String) {
        currentBaseUrl = ensureTrailingSlash(newUrl)
        prefs?.edit()?.putString(KEY_BASE_URL, currentBaseUrl)?.apply()
        buildRetrofit()
    }

    fun resetToDefaultBaseUrl() {
        updateBaseUrl(DEFAULT_BASE_URL)
    }

    fun setAuthToken(token: String?, userName: String? = null, email: String? = null) {
        authToken = token
        prefs?.edit()?.apply {
            if (token != null) {
                putString(KEY_AUTH_TOKEN, token)
            } else {
                remove(KEY_AUTH_TOKEN)
            }
            if (userName != null) putString(KEY_USER_NAME, userName)
            if (email != null) putString(KEY_USER_EMAIL, email)
            apply()
        }
        buildRetrofit()
    }

    fun getAuthToken(): String? = authToken

    fun getUserName(): String = prefs?.getString(KEY_USER_NAME, "Analyst") ?: "Analyst"

    fun getUserEmail(): String = prefs?.getString(KEY_USER_EMAIL, "") ?: ""

    fun clearSession() {
        authToken = null
        prefs?.edit()?.apply {
            remove(KEY_AUTH_TOKEN)
            remove(KEY_USER_NAME)
            remove(KEY_USER_EMAIL)
            apply()
        }
        buildRetrofit()
    }

    suspend fun testBackendConnection(): Pair<Boolean, String> = withContext(Dispatchers.IO) {
        try {
            val client = OkHttpClient.Builder()
                .connectTimeout(5, TimeUnit.SECONDS)
                .readTimeout(5, TimeUnit.SECONDS)
                .build()

            val healthUrl = "${currentBaseUrl}api/health"
            val request = Request.Builder().url(healthUrl).get().build()
            val response = client.newCall(request).execute()
            val statusCode = response.code
            val isSuccess = response.isSuccessful
            response.close()

            if (isSuccess) {
                Pair(true, "Successfully connected to backend server at $currentBaseUrl")
            } else {
                Pair(false, "Server reached, but returned HTTP $statusCode")
            }
        } catch (e: Exception) {
            Pair(false, "Could not reach $currentBaseUrl: ${e.localizedMessage ?: e.message}")
        }
    }

    @Synchronized
    private fun buildRetrofit() {
        val logging = HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY
        }
        val okHttpClient = OkHttpClient.Builder()
            .addInterceptor(logging)
            .addInterceptor { chain ->
                val requestBuilder = chain.request().newBuilder()
                authToken?.let {
                    requestBuilder.addHeader("Authorization", "Bearer $it")
                }
                chain.proceed(requestBuilder.build())
            }
            .connectTimeout(10, TimeUnit.SECONDS)
            .readTimeout(25, TimeUnit.SECONDS)
            .writeTimeout(25, TimeUnit.SECONDS)
            .retryOnConnectionFailure(true)
            .build()

        _apiService = Retrofit.Builder()
            .baseUrl(currentBaseUrl)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(ApiService::class.java)
    }

    val apiService: ApiService
        get() {
            if (_apiService == null) {
                buildRetrofit()
            }
            return _apiService!!
        }
}
