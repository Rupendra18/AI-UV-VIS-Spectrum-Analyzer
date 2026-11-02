package com.uvvis.analyzer.ui

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.uvvis.analyzer.data.model.AnalysisResult
import com.uvvis.analyzer.data.repository.SpectrumRepository
import com.uvvis.analyzer.network.ApiClient
import kotlinx.coroutines.launch
import java.io.File

class MainViewModel : ViewModel() {

    private val repository = SpectrumRepository()

    private val _history = MutableLiveData<List<AnalysisResult>>()
    val history: LiveData<List<AnalysisResult>> = _history

    private val _currentAnalysis = MutableLiveData<AnalysisResult?>()
    val currentAnalysis: LiveData<AnalysisResult?> = _currentAnalysis

    private val _loading = MutableLiveData<Boolean>()
    val loading: LiveData<Boolean> = _loading

    private val _error = MutableLiveData<String?>()
    val error: LiveData<String?> = _error

    private val _statusMessage = MutableLiveData<String?>()
    val statusMessage: LiveData<String?> = _statusMessage

    fun selectAnalysis(analysis: AnalysisResult) {
        _currentAnalysis.value = analysis
    }

    fun loadHistory() {
        _loading.value = true
        _error.value = null
        viewModelScope.launch {
            repository.getHistory()
                .onSuccess { list ->
                    _history.value = list
                    if (list.isNotEmpty() && _currentAnalysis.value == null) {
                        _currentAnalysis.value = list[0]
                    }
                    _loading.value = false
                }
                .onFailure { e ->
                    if (_history.value.isNullOrEmpty()) {
                        _error.value = "Cannot reach server at ${ApiClient.getBaseUrl()}: ${e.message}"
                    }
                    _loading.value = false
                }
        }
    }

    fun uploadSpectrum(file: File) {
        _loading.value = true
        _error.value = null
        viewModelScope.launch {
            repository.uploadSpectrumFile(file)
                .onSuccess { result ->
                    _currentAnalysis.value = result
                    _statusMessage.value = "Spectrum analyzed successfully!"
                    _loading.value = false
                    loadHistory()
                }
                .onFailure { e ->
                    _error.value = "Upload error: ${e.message}"
                    _loading.value = false
                }
        }
    }

    fun deleteAnalysis(id: String) {
        _loading.value = true
        _error.value = null
        viewModelScope.launch {
            repository.deleteHistory(id)
                .onSuccess {
                    _statusMessage.value = "Analysis deleted"
                    if (_currentAnalysis.value?.id == id) {
                        val remaining = _history.value?.filter { it.id != id } ?: emptyList()
                        _currentAnalysis.value = remaining.firstOrNull()
                    }
                    loadHistory()
                }
                .onFailure { e ->
                    _error.value = "Delete failed: ${e.message}"
                    _loading.value = false
                }
        }
    }
}
