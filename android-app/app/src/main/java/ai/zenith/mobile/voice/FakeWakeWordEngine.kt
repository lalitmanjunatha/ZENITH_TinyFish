package ai.zenith.mobile.voice

import android.util.Log
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import kotlinx.coroutines.supervisorScope

/**
 * A fake implementation of WakeWordEngine for demonstration purposes.
 * In a real app, this would be replaced with an actual wake word detection library.
 */
class FakeWakeWordEngine(
    private val wakeWord: String = "ZENITH",
    private val detectionDelayMs: Long = 3000
) : WakeWordEngine {

    private var isListening = false
    private val supervisorScope = supervisorScope()

    override fun startListening(onWakeWordDetected: () -> Unit) {
        if (isListening) return
        isListening = true
        Log.d("WakeWordEngine", "Listening for wake word: $wakeWord")
        supervisorScope.launch {
            while (isActive && isListening) {
                // Simulate waiting for audio and detecting the wake word after a delay
                delay(detectionDelayMs)
                if (isListening) {
                    Log.d("WakeWordEngine", "Wake word detected: $wakeWord")
                    onWakeWordDetected()
                    // After detection, we might want to stop listening for the wake word
                    // and start the voice pipeline. For now, we just continue listening.
                }
            }
        }
    }

    override fun stopListening() {
        isListening = false
        Log.d("WakeWordEngine", "Stopped listening for wake word")
    }

    override fun release() {
        stopListening()
        supervisorScope.cancel()
        Log.d("WakeWordEngine", "Released wake word engine resources")
    }
}
