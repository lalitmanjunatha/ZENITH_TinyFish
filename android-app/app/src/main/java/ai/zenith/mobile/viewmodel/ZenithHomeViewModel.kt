package ai.zenith.mobile.viewmodel

import ai.zenith.mobile.ui.hud.OrbState
import androidx.compose.runtime.State
import androidx.compose.runtime.mutableStateOf
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.delay

/**
 * ViewModel for the Zenith home screen.
 * Manages the UI state and handles user interactions.
 */
class ZenithHomeViewModel : ViewModel() {

    // UI State
    private val _uiState = MutableStateFlow(UiState())
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    // Internal state for simulation
    private var isListeningInternal = false

    init {
        // Simulate some state changes for demonstration
        viewModelScope.launch {
            while (true) {
                delay(5000) // 5 seconds
                // Simulate a state change
                _uiState.update { it.copy(
                    orbState = if (it.orbState == OrbState.IDLE) OrbState.LISTENING else OrbState.IDLE,
                    isListening = !it.isListening
                )}
            }
        }
    }

    fun onMicrophoneClicked() {
        // Toggle listening state
        _uiState.update { it.copy(
            isListening = !it.isListening,
            orbState = if (it.isListening) OrbState.IDLE else OrbState.LISTENING
        )}
    }

    fun onInterruptClicked() {
        // Set state to interrupted temporarily
        _uiState.update { it.copy(
            orbState = OrbState.INTERRUPTED
        )}
        // After a short delay, return to idle
        viewModelScope.launch {
            delay(1000)
            _uiState.update { it.copy(
                orbState = OrbState.IDLE
            )}
        }
    }

    fun onTextInputClicked() {
        // For now, just change state to thinking
        _uiState.update { it.copy(
            orbState = OrbState.THINKING
        )}
        viewModelScope.launch {
            delay(2000)
            _uiState.update { it.copy(
                orbState = OrbState.IDLE
            )}
        }
    }

    // Data class for UI state
    data class UiState(
        val orbState: OrbState = OrbState.IDLE,
        val isListening: Boolean = false,
        val isInterrupted: Boolean = false,
        val activityLog: List<String> = listOf(
            "SYS: Starting ZENITH Mobile",
            "AI: Initializing",
            "REMOTE: Checking connection"
        ),
        val currentTime: String = "00:00"
    )
}
