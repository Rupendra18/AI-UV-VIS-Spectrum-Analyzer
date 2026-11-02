package com.uvvis.analyzer.ui

import android.content.Intent
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import androidx.appcompat.app.AppCompatActivity
import com.uvvis.analyzer.R
import com.uvvis.analyzer.network.ApiClient

class SplashActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_splash)

        ApiClient.init(this)

        Handler(Looper.getMainLooper()).postDelayed({
            val token = ApiClient.getAuthToken()
            if (!token.isNullOrBlank()) {
                startActivity(Intent(this, MainActivity::class.java))
            } else {
                startActivity(Intent(this, LoginActivity::class.java))
            }
            finish()
        }, 1500)
    }
}
