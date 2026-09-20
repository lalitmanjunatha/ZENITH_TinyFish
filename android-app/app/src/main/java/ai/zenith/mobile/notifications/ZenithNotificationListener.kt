package ai.zenith.mobile.notifications

import android.service.notification.NotificationListenerService
import android.service.notification.StatusBarNotification

/** Emits metadata/events; only Android-provided RemoteInput reply actions are used. */
class ZenithNotificationListener : NotificationListenerService() {
    override fun onNotificationPosted(sbn: StatusBarNotification) {
        if (sbn.packageName == packageName) return
        // FabricClient.enqueueNotification() is intentionally local-first and added during relay wiring.
    }
}
