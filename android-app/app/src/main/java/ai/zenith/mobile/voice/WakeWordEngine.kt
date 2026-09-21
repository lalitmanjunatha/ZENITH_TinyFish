package ai.zenith.mobile.voice

/**
 * Interface for wake word detection.
 * Implementations should detect the wake word (e.g., "ZENITH") in audio streams.
 */
interface WakeWordEngine {

    /**
     * Start listening for the wake word.
     * @param onWakeWordDetected Callback to invoke when the wake word is detected.
     */
    fun startListening(onWakeWordDetected: () -> Unit)

    /**
     * Stop listening for the wake word.
     */
    fun stopListening()

    /**
     * Release any resources held by the wake word engine.
     */
    fun release()
}
