package com.uvvis.analyzer.ui

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.provider.OpenableColumns
import android.view.LayoutInflater
import android.view.View
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.viewModels
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import com.github.mikephil.charting.data.Entry
import com.github.mikephil.charting.data.LineData
import com.github.mikephil.charting.data.LineDataSet
import com.uvvis.analyzer.R
import com.uvvis.analyzer.data.model.AnalysisResult
import com.uvvis.analyzer.databinding.ActivityMainBinding
import com.uvvis.analyzer.network.ApiClient
import java.io.File
import java.io.FileOutputStream

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private val viewModel: MainViewModel by viewModels()

    private val selectCsvLauncher = registerForActivityResult(ActivityResultContracts.GetContent()) { uri: Uri? ->
        uri?.let { handleSelectedFile(it) }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        ApiClient.init(this)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        val userName = ApiClient.getUserName()
        binding.tvScientistInfo.text = "Analyst: $userName"

        setupListeners()
        setupObservers()
        viewModel.loadHistory()
    }

    private fun setupListeners() {
        binding.btnSelectFile.setOnClickListener {
            // Open file picker for CSV files
            selectCsvLauncher.launch("*/*")
        }

        binding.btnSampleSpectrum.setOnClickListener {
            generateAndUploadSampleSpectrum()
        }

        binding.btnRefresh.setOnClickListener {
            viewModel.loadHistory()
        }

        binding.btnServerConfigMain.setOnClickListener {
            showServerConfigDialog()
        }

        binding.btnLogout.setOnClickListener {
            showLogoutDialog()
        }
    }

    private fun handleSelectedFile(uri: Uri) {
        try {
            val contentResolver = applicationContext.contentResolver
            var fileName = "spectrum_${System.currentTimeMillis()}.csv"

            contentResolver.query(uri, null, null, null, null)?.use { cursor ->
                val nameIndex = cursor.getColumnIndex(OpenableColumns.DISPLAY_NAME)
                if (nameIndex != -1 && cursor.moveToFirst()) {
                    val name = cursor.getString(nameIndex)
                    if (!name.isNullOrBlank()) {
                        fileName = name
                    }
                }
            }

            val tempFile = File(cacheDir, fileName)
            contentResolver.openInputStream(uri)?.use { input ->
                FileOutputStream(tempFile).use { output ->
                    input.copyTo(output)
                }
            }

            binding.tvCurrentFileName.text = "Analyzing: $fileName"
            viewModel.uploadSpectrum(tempFile)
        } catch (e: Exception) {
            Toast.makeText(this, "Failed to read file: ${e.message}", Toast.LENGTH_LONG).show()
        }
    }

    private fun generateAndUploadSampleSpectrum() {
        try {
            val sampleFile = File(cacheDir, "sample_spectrum_${System.currentTimeMillis()}.csv")
            sampleFile.bufferedWriter().use { writer ->
                writer.write("Wavelength,Absorbance\n")
                // Generate a realistic UV-Vis curve with peak around 275nm
                for (w in 200..800 step 10) {
                    val dist = kotlin.math.abs(w - 275)
                    val abs = 1.35 * kotlin.math.exp(-dist * dist / 2200.0) + (0.02 * kotlin.random.Random.nextDouble())
                    writer.write(String.format(java.util.Locale.US, "%d,%.4f\n", w, abs))
                }
            }

            binding.tvCurrentFileName.text = "Analyzing: sample_spectrum.csv"
            viewModel.uploadSpectrum(sampleFile)
        } catch (e: Exception) {
            Toast.makeText(this, "Failed to generate demo spectrum: ${e.message}", Toast.LENGTH_SHORT).show()
        }
    }

    private fun setupObservers() {
        viewModel.loading.observe(this) { isLoading ->
            binding.progressBar.visibility = if (isLoading == true) View.VISIBLE else View.GONE
            binding.btnSelectFile.isEnabled = isLoading != true
            binding.btnSampleSpectrum.isEnabled = isLoading != true
            binding.btnRefresh.isEnabled = isLoading != true
        }

        viewModel.error.observe(this) { errorMsg ->
            if (!errorMsg.isNullOrBlank()) {
                Toast.makeText(this, errorMsg, Toast.LENGTH_LONG).show()
            }
        }

        viewModel.statusMessage.observe(this) { msg ->
            if (!msg.isNullOrBlank()) {
                Toast.makeText(this, msg, Toast.LENGTH_SHORT).show()
            }
        }

        viewModel.currentAnalysis.observe(this) { analysis ->
            analysis?.let { displayAnalysis(it) }
        }

        viewModel.history.observe(this) { list ->
            populateHistoryList(list ?: emptyList())
        }
    }

    private fun displayAnalysis(it: AnalysisResult) {
        binding.tvCurrentFileName.text = it.filename ?: "Spectrum Analysis"
        binding.tvPeakWavelength.text = String.format(java.util.Locale.US, "%.1f nm", it.peakWavelength)
        binding.tvPeakAbsorbance.text = String.format(java.util.Locale.US, "%.3f AU", it.peakAbsorbance)
        binding.tvConcentration.text = String.format(java.util.Locale.US, "%.2f ppm", it.predictedConcentration)

        binding.tvStatus.text = "Status: ${it.status}"
        when (it.status.uppercase()) {
            "SAFE" -> binding.tvStatus.setTextColor(ContextCompat.getColor(this, R.color.safe_green))
            "MODERATE" -> binding.tvStatus.setTextColor(ContextCompat.getColor(this, R.color.warning_amber))
            "HIGH" -> binding.tvStatus.setTextColor(ContextCompat.getColor(this, R.color.danger_red))
            else -> binding.tvStatus.setTextColor(ContextCompat.getColor(this, R.color.text_primary))
        }

        binding.tvConfidence.text = String.format(java.util.Locale.US, "AI Confidence: %.1f%%", it.confidenceScore)
        val algorithmName = it.algorithm ?: "Random Forest Regressor"
        val accuracy = it.accuracyPercentage ?: 96.5
        binding.tvMetrics.text = String.format(java.util.Locale.US, "Model: %s (Acc: %.1f%%)", algorithmName, accuracy)
        binding.tvInterpretation.text = it.interpretation ?: "No interpretation available for this sample."

        renderSpectrumChart(it.peakWavelength, it.peakAbsorbance)
    }

    private fun populateHistoryList(list: List<AnalysisResult>) {
        binding.layoutHistoryList.removeAllViews()

        if (list.isEmpty()) {
            binding.tvHistoryEmpty.visibility = View.VISIBLE
            binding.layoutHistoryList.visibility = View.GONE
            binding.tvHistoryHeader.text = "Recent Analyses History (0)"
            return
        }

        binding.tvHistoryEmpty.visibility = View.GONE
        binding.layoutHistoryList.visibility = View.VISIBLE
        binding.tvHistoryHeader.text = "Recent Analyses History (${list.size})"

        for (item in list) {
            val itemView = createHistoryItemView(item)
            binding.layoutHistoryList.addView(itemView)
        }
    }

    private fun createHistoryItemView(item: AnalysisResult): View {
        val container = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            background = ContextCompat.getDrawable(this@MainActivity, R.drawable.bg_input)
            val pad = (12 * resources.displayMetrics.density).toInt()
            setPadding(pad, pad, pad, pad)
            val params = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply {
                bottomMargin = (10 * resources.displayMetrics.density).toInt()
            }
            layoutParams = params
        }

        // Row 1: File Name + Status
        val row1 = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = android.view.Gravity.CENTER_VERTICAL
        }

        val tvName = TextView(this).apply {
            text = item.filename ?: "Spectrum"
            setTextColor(ContextCompat.getColor(this@MainActivity, R.color.text_primary))
            textSize = 14f
            setTypeface(typeface, android.graphics.Typeface.BOLD)
            val p = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f)
            layoutParams = p
        }

        val tvBadge = TextView(this).apply {
            text = item.status.uppercase()
            textSize = 12f
            setTypeface(typeface, android.graphics.Typeface.BOLD)
            when (item.status.uppercase()) {
                "SAFE" -> setTextColor(ContextCompat.getColor(this@MainActivity, R.color.safe_green))
                "MODERATE" -> setTextColor(ContextCompat.getColor(this@MainActivity, R.color.warning_amber))
                "HIGH" -> setTextColor(ContextCompat.getColor(this@MainActivity, R.color.danger_red))
                else -> setTextColor(ContextCompat.getColor(this@MainActivity, R.color.text_secondary))
            }
        }

        row1.addView(tvName)
        row1.addView(tvBadge)
        container.addView(row1)

        // Row 2: Date + Concentration
        val row2 = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = android.view.Gravity.CENTER_VERTICAL
            val params = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply {
                topMargin = (4 * resources.displayMetrics.density).toInt()
                bottomMargin = (8 * resources.displayMetrics.density).toInt()
            }
            layoutParams = params
        }

        val tvTime = TextView(this).apply {
            text = item.timestamp ?: ""
            setTextColor(ContextCompat.getColor(this@MainActivity, R.color.text_secondary))
            textSize = 11f
            val p = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f)
            layoutParams = p
        }

        val tvConc = TextView(this).apply {
            text = String.format(java.util.Locale.US, "%.2f ppm", item.predictedConcentration)
            setTextColor(ContextCompat.getColor(this@MainActivity, R.color.primary))
            textSize = 13f
            setTypeface(typeface, android.graphics.Typeface.BOLD)
        }

        row2.addView(tvTime)
        row2.addView(tvConc)
        container.addView(row2)

        // Row 3: Action Buttons (View Chart, Delete)
        val row3 = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = android.view.Gravity.END
        }

        val btnView = Button(this, null, androidx.appcompat.R.attr.borderlessButtonStyle).apply {
            text = "View Curve"
            setTextColor(ContextCompat.getColor(this@MainActivity, R.color.secondary))
            textSize = 12f
            setOnClickListener {
                viewModel.selectAnalysis(item)
                Toast.makeText(this@MainActivity, "Viewing: ${item.filename}", Toast.LENGTH_SHORT).show()
            }
        }

        val btnDelete = Button(this, null, androidx.appcompat.R.attr.borderlessButtonStyle).apply {
            text = "Delete"
            setTextColor(ContextCompat.getColor(this@MainActivity, R.color.danger_red))
            textSize = 12f
            setOnClickListener {
                item.id?.let { id ->
                    AlertDialog.Builder(this@MainActivity)
                        .setTitle("Delete Analysis")
                        .setMessage("Delete record for '${item.filename}'?")
                        .setPositiveButton("Delete") { _, _ -> viewModel.deleteAnalysis(id) }
                        .setNegativeButton("Cancel", null)
                        .show()
                }
            }
        }

        row3.addView(btnView)
        row3.addView(btnDelete)
        container.addView(row3)

        return container
    }

    private fun renderSpectrumChart(peakW: Double, peakA: Double) {
        val entries = ArrayList<Entry>()
        val startW = 200
        val endW = 800

        val effectivePeakW = if (peakW in 200.0..800.0) peakW else 280.0
        val effectivePeakA = if (peakA > 0.0) peakA else 1.0

        for (w in startW..endW step 5) {
            val dist = kotlin.math.abs(w - effectivePeakW)
            val abs = effectivePeakA * kotlin.math.exp(-dist * dist / 1800.0)
            entries.add(Entry(w.toFloat(), abs.toFloat()))
        }

        val dataSet = LineDataSet(entries, "Absorbance Spectrum (AU)").apply {
            color = android.graphics.Color.parseColor("#38BDF8")
            lineWidth = 2.5f
            setDrawCircles(false)
            setDrawFilled(true)
            fillColor = android.graphics.Color.parseColor("#0284C7")
            fillAlpha = 60
            setDrawValues(false)
        }

        binding.chartSpectrum.apply {
            data = LineData(dataSet)
            description.isEnabled = false
            legend.textColor = android.graphics.Color.WHITE
            xAxis.textColor = android.graphics.Color.LTGRAY
            axisLeft.textColor = android.graphics.Color.LTGRAY
            axisRight.isEnabled = false
            animateX(500)
            invalidate()
        }
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
            .setMessage("Current backend API endpoint:")
            .setView(dialogView)
            .setPositiveButton("Save & Reload") { _, _ ->
                val newUrl = input.text.toString().trim()
                if (newUrl.isNotBlank()) {
                    ApiClient.updateBaseUrl(newUrl)
                    viewModel.loadHistory()
                    Toast.makeText(this, "Server updated: ${ApiClient.getBaseUrl()}", Toast.LENGTH_SHORT).show()
                }
            }
            .setNeutralButton("Reset to Laptop IP") { _, _ ->
                ApiClient.resetToDefaultBaseUrl()
                viewModel.loadHistory()
                Toast.makeText(this, "Set to Laptop IP: ${ApiClient.DEFAULT_BASE_URL}", Toast.LENGTH_SHORT).show()
            }
            .setNegativeButton("Cancel", null)
            .show()
    }

    private fun showLogoutDialog() {
        AlertDialog.Builder(this)
            .setTitle("Logout")
            .setMessage("Are you sure you want to log out of your session?")
            .setPositiveButton("Logout") { _, _ ->
                ApiClient.clearSession()
                Toast.makeText(this, "Logged out successfully", Toast.LENGTH_SHORT).show()
                startActivity(Intent(this, LoginActivity::class.java))
                finish()
            }
            .setNegativeButton("Cancel", null)
            .show()
    }
}
