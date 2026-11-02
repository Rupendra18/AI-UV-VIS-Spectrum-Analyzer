package com.uvvis.analyzer.ui

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.biometric.BiometricPrompt
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import com.uvvis.analyzer.R
import com.uvvis.analyzer.data.repository.SpectrumRepository
import com.uvvis.analyzer.databinding.ActivityLoginBinding
import com.uvvis.analyzer.network.ApiClient
import kotlinx.coroutines.launch

class LoginActivity : AppCompatActivity() {

    private lateinit var binding: ActivityLoginBinding
    private var isSignUpMode = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        ApiClient.init(this)
        binding = ActivityLoginBinding.inflate(layoutInflater)
        setContentView(binding.root)

        updateServerUrlDisplay()
        setupTabSwitchers()
        setupListeners()
    }

    private fun updateServerUrlDisplay() {
        binding.tvServerUrl.text = "Server: ${ApiClient.getBaseUrl()}"
    }

    private fun setupTabSwitchers() {
        binding.btnTabSignIn.setOnClickListener { switchMode(false) }
        binding.btnTabSignUp.setOnClickListener { switchMode(true) }
        binding.tvSwitchToSignUp.setOnClickListener { switchMode(true) }
        binding.tvSwitchToSignIn.setOnClickListener { switchMode(false) }
    }

    private fun switchMode(signUp: Boolean) {
        isSignUpMode = signUp
        if (signUp) {
            binding.layoutSignIn.visibility = View.GONE
            binding.layoutSignUp.visibility = View.VISIBLE

            binding.btnTabSignUp.setBackgroundColor(ContextCompat.getColor(this, R.color.primary))
            binding.btnTabSignUp.setTextColor(ContextCompat.getColor(this, R.color.white))
            binding.btnTabSignIn.setBackgroundColor(android.graphics.Color.TRANSPARENT)
            binding.btnTabSignIn.setTextColor(ContextCompat.getColor(this, R.color.tab_inactive))
        } else {
            binding.layoutSignIn.visibility = View.VISIBLE
            binding.layoutSignUp.visibility = View.GONE

            binding.btnTabSignIn.setBackgroundColor(ContextCompat.getColor(this, R.color.primary))
            binding.btnTabSignIn.setTextColor(ContextCompat.getColor(this, R.color.white))
            binding.btnTabSignUp.setBackgroundColor(android.graphics.Color.TRANSPARENT)
            binding.btnTabSignUp.setTextColor(ContextCompat.getColor(this, R.color.tab_inactive))
        }
    }

    private fun setupListeners() {
        // Sign In Button
        binding.btnLoginSubmit.setOnClickListener {
            val email = binding.etLoginEmail.text.toString().trim()
            val password = binding.etLoginPassword.text.toString()

            if (email.isEmpty() || password.isEmpty()) {
                Toast.makeText(this, "Please enter both email and password", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            performLogin(email, password)
        }

        // Sign Up Button
        binding.btnRegisterSubmit.setOnClickListener {
            val name = binding.etRegisterName.text.toString().trim()
            val org = binding.etRegisterOrg.text.toString().trim()
            val email = binding.etRegisterEmail.text.toString().trim()
            val password = binding.etRegisterPassword.text.toString()
            val confirmPassword = binding.etRegisterConfirmPassword.text.toString()

            if (name.isEmpty()) {
                Toast.makeText(this, "Please enter your name", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            if (email.isEmpty()) {
                Toast.makeText(this, "Please enter your email", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            if (password.length < 6) {
                Toast.makeText(this, "Password must be at least 6 characters", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            if (password != confirmPassword) {
                Toast.makeText(this, "Passwords do not match", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            performRegister(name, org, email, password)
        }

        // Biometric Button
        binding.btnBiometric.setOnClickListener {
            showBiometricPrompt()
        }

        // Server Config Pill
        binding.btnServerConfig.setOnClickListener {
            showServerConfigDialog()
        }

        // Test Live Backend Connection Button
        binding.btnTestConnection.setOnClickListener {
            runLiveConnectionTest()
        }
    }

    private fun runLiveConnectionTest() {
        Toast.makeText(this, "Testing backend connection...", Toast.LENGTH_SHORT).show()
        lifecycleScope.launch {
            val (ok, message) = ApiClient.testBackendConnection()
            AlertDialog.Builder(this@LoginActivity)
                .setTitle(if (ok) "Backend Online ✅" else "Backend Unreachable ❌")
                .setMessage(
                    if (ok) {
                        "$message\n\nYour mobile phone can successfully talk to your laptop's backend server!"
                    } else {
                        "$message\n\nChecklist to fix:\n" +
                                "1. Run 'python backend\\app.py' on your laptop.\n" +
                                "2. Connect your phone to the same Wi-Fi network.\n" +
                                "3. Confirm your laptop's Wi-Fi IP address (run 'ipconfig' in PowerShell).\n" +
                                "4. Current laptop target: ${ApiClient.getBaseUrl()}"
                    }
                )
                .setPositiveButton(if (ok) "Great!" else "Change Server IP") { _, _ ->
                    if (!ok) showServerConfigDialog()
                }
                .setNegativeButton("Close", null)
                .show()
        }
    }

    private fun performLogin(email: String, password: String) {
        setLoading(true)

        lifecycleScope.launch {
            try {
                val res = ApiClient.apiService.login(mapOf("email" to email, "password" to password))
                setLoading(false)

                if (res.isSuccessful && (res.body()?.status == "ok" || res.body()?.status == "success")) {
                    val loginRes = res.body()
                    val userName = loginRes?.user?.name ?: email.substringBefore("@")
                    ApiClient.setAuthToken(loginRes?.token, userName, email)
                    Toast.makeText(this@LoginActivity, "Welcome back, $userName!", Toast.LENGTH_SHORT).show()
                    navigateToMain()
                } else {
                    val errBody = res.errorBody()?.string()
                    val errorMsg = SpectrumRepository.parseErrorMessage(errBody)
                        ?: res.body()?.error
                        ?: "Invalid email or password"
                    Toast.makeText(this@LoginActivity, "Login failed: $errorMsg", Toast.LENGTH_LONG).show()
                }
            } catch (e: Exception) {
                setLoading(false)
                showConnectionErrorDialog("Login", e.localizedMessage ?: e.message ?: "Connection error")
            }
        }
    }

    private fun performRegister(name: String, org: String, email: String, password: String) {
        setLoading(true)

        lifecycleScope.launch {
            try {
                val body = mutableMapOf(
                    "name" to name,
                    "email" to email,
                    "password" to password
                )
                if (org.isNotBlank()) {
                    body["org_name"] = org
                }

                val res = ApiClient.apiService.register(body)
                setLoading(false)

                if (res.isSuccessful && (res.body()?.status == "ok" || res.body()?.status == "success")) {
                    val regRes = res.body()
                    val userName = regRes?.user?.name ?: name
                    ApiClient.setAuthToken(regRes?.token, userName, email)
                    Toast.makeText(this@LoginActivity, "Account created successfully! Welcome, $userName", Toast.LENGTH_SHORT).show()
                    navigateToMain()
                } else {
                    val errBody = res.errorBody()?.string()
                    val errorMsg = SpectrumRepository.parseErrorMessage(errBody)
                        ?: res.body()?.error
                        ?: "Registration failed (HTTP ${res.code()})"
                    Toast.makeText(this@LoginActivity, errorMsg, Toast.LENGTH_LONG).show()
                }
            } catch (e: Exception) {
                setLoading(false)
                showConnectionErrorDialog("Registration", e.localizedMessage ?: e.message ?: "Connection error")
            }
        }
    }

    private fun setLoading(isLoading: Boolean) {
        binding.progressBarAuth.visibility = if (isLoading) View.VISIBLE else View.GONE
        binding.btnLoginSubmit.isEnabled = !isLoading
        binding.btnRegisterSubmit.isEnabled = !isLoading
        binding.btnLoginSubmit.text = if (isLoading) "Signing in..." else "Sign In"
        binding.btnRegisterSubmit.text = if (isLoading) "Creating Account..." else "Create Account"
    }

    private fun showConnectionErrorDialog(action: String, errorDetails: String) {
        AlertDialog.Builder(this)
            .setTitle("$action Connection Failed")
            .setMessage(
                "Could not reach backend server at:\n${ApiClient.getBaseUrl()}\n\n" +
                "Error Details:\n$errorDetails\n\n" +
                "Troubleshooting Steps:\n" +
                "• Ensure 'python backend\\app.py' is running on your laptop.\n" +
                "• Connect both your mobile phone and laptop to the same Wi-Fi.\n" +
                "• Ensure Windows Firewall allows incoming connections on port 5000."
            )
            .setPositiveButton("Change Server IP") { _, _ ->
                showServerConfigDialog()
            }
            .setNeutralButton("Test Connection") { _, _ ->
                runLiveConnectionTest()
            }
            .setNegativeButton("Cancel", null)
            .show()
    }

    private fun showServerConfigDialog() {
        val dialogView = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(50, 40, 50, 20)
        }

        val input = EditText(this).apply {
            setText(ApiClient.getBaseUrl())
            hint = "http://192.168.137.254:5000/"
            setSingleLine(true)
        }
        dialogView.addView(input)

        AlertDialog.Builder(this)
            .setTitle("Backend Server Connection")
            .setMessage("Enter the IPv4 address of your laptop (running python app.py on port 5000):")
            .setView(dialogView)
            .setPositiveButton("Save & Apply") { _, _ ->
                val newUrl = input.text.toString().trim()
                if (newUrl.isNotBlank()) {
                    ApiClient.updateBaseUrl(newUrl)
                    updateServerUrlDisplay()
                    Toast.makeText(this, "Updated: ${ApiClient.getBaseUrl()}", Toast.LENGTH_SHORT).show()
                }
            }
            .setNeutralButton("Reset to Laptop IP") { _, _ ->
                ApiClient.resetToDefaultBaseUrl()
                updateServerUrlDisplay()
                Toast.makeText(this, "Set to Laptop IP: ${ApiClient.DEFAULT_BASE_URL}", Toast.LENGTH_SHORT).show()
            }
            .setNegativeButton("Cancel", null)
            .show()
    }

    private fun navigateToMain() {
        startActivity(Intent(this@LoginActivity, MainActivity::class.java))
        finish()
    }

    private fun showBiometricPrompt() {
        val executor = ContextCompat.getMainExecutor(this)
        val prompt = BiometricPrompt(this, executor, object : BiometricPrompt.AuthenticationCallback() {
            override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
                val savedName = ApiClient.getUserName()
                ApiClient.setAuthToken("biometric-session-token", savedName, ApiClient.getUserEmail())
                Toast.makeText(this@LoginActivity, "Biometric authentication verified", Toast.LENGTH_SHORT).show()
                navigateToMain()
            }

            override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
                super.onAuthenticationError(errorCode, errString)
                Toast.makeText(this@LoginActivity, "Biometric: $errString", Toast.LENGTH_SHORT).show()
            }
        })

        val promptInfo = BiometricPrompt.PromptInfo.Builder()
            .setTitle("Biometric Login")
            .setSubtitle("Use your fingerprint to log into UV-Vis Analyzer")
            .setNegativeButtonText("Cancel")
            .build()

        prompt.authenticate(promptInfo)
    }
}
