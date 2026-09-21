package ai.zenith.mobile.voice

import android.app.Service
import android.content.Intent
import android.media.AudioRecord
import android.media.MediaRecorder
import android.os.Binder
import android.os.IBinder
import android.util.Log
import androidx.lifecycle.LifecycleService
import androidx.lifecycle.viewmodelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.collectLatest

/**
 * Service for processing voice input, including wake word detection, speech recognition, and text-to-speech.
 */
class VoiceProcessingService : LifecycleService() {

    private lateinit var wakeWordEngine: WakeWordEngine
    private val voiceState = MutableStateFlow<VoiceState>(VoiceState.IDLE)

    // Binder for clients to bind to this service
    private val binder = LocalBinder()

    // Expose voice state as a StateFlow for UI to collect
    val voiceStateFlow: StateFlow<VoiceState> = voiceState.asStateFlow()

    inner class LocalBinder : Binder() {
        fun getService(): VoiceProcessingService = this@VoiceProcessingService
    }

    override fun onBind(intent: Intent?): IBinder {
        return binder
    }

    override fun onCreate() {
        super.onCreate()
        wakeWordEngine = FakeWakeWordEngine()
        wakeWordEngine.startListening {
            // When wake word is detected, update state and start listening for command
            voiceState.value = VoiceState.LISTENING
            // TODO: Start speech recognition
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        wakeWordEngine.stopListening()
        wakeWordEngine.release()
    }

    // TODO: Implement methods for starting/stopping speech recognition, TTS, etc.

    // Data class for voice state
    enum class VoiceState {
        IDLE,
        LISTENING, // Wake word detected, listening for command
        PROCESSING, // Processing the command (AI thinking)
        SPEAKING // Speaking the response
    }
}
