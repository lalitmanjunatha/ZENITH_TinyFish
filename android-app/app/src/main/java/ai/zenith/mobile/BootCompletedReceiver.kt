package ai.zenith.mobile

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.util.Log

/**
 * Broadcast receiver that starts ZENITH services when the device boots.
 */
class BootCompletedReceiver : BroadcastReceiver() {

    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action == Intent.ACTION_BOOT_COMPLETED) {
            Log.d("BootCompletedReceiver", "Device boot completed. Starting ZENITH services.")
            // Start the voice processing service
            val voiceIntent = Intent(context, voice.VoiceProcessingService::class.java)
            context.startForegroundService(voiceIntent)
            // Start the remote connection service
            val remoteIntent = Intent(context, remote.RemoteConnectionService::class.java)
            context.startForegroundService(remoteIntent)
        }
    }
}
