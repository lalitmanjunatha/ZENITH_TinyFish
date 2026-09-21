package ai.zenith.mobile.remote

import android.app.Service
import android.content.Intent
import android.os.IBinder
import android.util.Log
import androidx.lifecycle.LifecycleService
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.launch

/**
 * Service for managing the remote connection to the ZENITH desktop via Render.
 */
class RemoteConnectionService : LifecycleService() {

    private lateinit var remoteNode: RemoteNode
    private val isConnected = mutableStateOf(false)

    override fun onCreate() {
        super.onCreate()
        Log.d("RemoteConnectionService", "Service created")
        initializeRemoteNode()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        Log.d("RemoteConnectionService", "Service started")
        // Start the remote connection loop
        viewModelScope.launch {
            maintainConnection()
        }
        // Make it a foreground service
        startForeground(1, createNotification("ZENITH Remote Service", "Connecting to laptop..."))
        return START_STICKY
    }

    override fun onDestroy() {
        super.onDestroy()
        Log.d("RemoteConnectionService", "Service destroyed")
    }

    override fun onBind(intent: Intent?): IBinder? {
        // We don't provide binding, so return null
        return null
    }

    private fun initializeRemoteNode() {
        // In a real app, we would get the device ID and shared secret from secure storage
        val deviceId = "android_device_" + java.util.UUID.randomUUID().toString().substring(0, 8)
        val sharedSecret = remote.SharedSecret.newInstance() // Generate a new one for demo; in reality, this would be loaded from pairing
        val transport = remote.FakeRemoteTransport() // Replace with real transport when implementing
        remoteNode = remote.RemoteNode(deviceId, sharedSecret, transport)
    }

    private fun maintainConnection() {
        while (true) {
            try {
                // Simulate checking connection status
                val isOnline = java.lang.Math.random() > 0.2 // 80% chance of being online for demo
                isConnected.value = isOnline
                if (isOnline) {
                    // Send any pending events
                    remoteNode.trySendOutbox()
                    // Receive events
                    remoteNode.receiveEvents()
                    // Update notification
                    updateNotification("ZENITH Remote Service", "Connected to laptop")
                } else {
                    updateNotification("ZENITH Remote Service", "Disconnected from laptop")
                }
                delay(5000) // Check every 5 seconds
            } catch (e: Exception) {
                Log.e("RemoteConnectionService", "Error in maintainConnection", e)
                delay(5000)
            }
        }
    }

    private fun createNotification(title: String, text: String): android.app.Notification {
        // This is a simplified notification. In a real app, you would use NotificationCompat and a channel.
        return android.app.Notification.Builder(this, "default")
            .setContentTitle(title)
            .setContentText(text)
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .build()
    }

    private fun updateNotification(title: String, text: String) {
        val notification = createNotification(title, text)
        val notificationManager = getSystemService(NOTIFICATION_SERVICE) as android.app.NotificationManager
        notificationManager.notify(1, notification)
    }
}
