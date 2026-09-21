package ai.zenith.mobile.remote

import android.util.Base64
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import org.json.JSONException
import org.json.JSONObject
import java.io.IOException
import java.security.SecureRandom
import java.util.Date
import java.util.HashMap
import java.util.Map
import java.util.Random
import java.util.UUID
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec
import javax.crypto.spec.SecretKeySpec

/**
 * RemoteNode handles the creation, sealing, and opening of events for remote communication.
 * This is a simplified Kotlin version of the Python FabricNode.
 */
class RemoteNode(
    private val deviceId: String,
    private val sharedSecret: SharedSecret,
    private val transport: RemoteTransport
) {

    private val outbox = mutableMapOf<String, Pair<DeviceEvent, String>>()
    private val mutex = Mutex()
    private val _pendingEvents = MutableStateFlow<List<DeviceEvent>>(emptyList())
    val pendingEvents: StateFlow<List<DeviceEvent>> = _pendingEvents.asStateFlow()

    init {
        // Simulate periodic sending of outbox events
        viewModelScope.launch {
            while (true) {
                trySendOutbox()
                delay(5000) // 5 seconds
            }
        }
    }

    /**
     * Register a handler for incoming events of a specific type.
     * In a full implementation, this would be part of an event bus.
     */
    fun registerHandler(eventType: String, handler: (DeviceEvent) -> Unit) {
        // TODO: Implement handler registration
    }

    /**
     * Create a new event with the given type and payload.
     * @param eventType The type of the event.
     * @param payload The payload to include in the event.
     * @param targetDeviceId The target device ID (optional).
     * @param expiresInSeconds How long until the event expires (optional).
     * @return The created event and its sealed envelope.
     */
    fun makeEvent(
        eventType: String,
        payload: Map<String, Any>,
        targetDeviceId: String? = null,
        expiresInSeconds: Long? = null
    ): Pair<DeviceEvent, String> {
        val eventTime = (Date().time / 1000) + (expiresInSeconds ?: 0)
        val event = DeviceEvent(
            eventId = UUID.randomUUID().toString(),
            eventType = eventType,
            deviceId = deviceId,
            payload = payload,
            targetDeviceId = targetDeviceId,
            timestamp = eventTime
        )
        val envelope = sealEvent(event)
        return Pair(event, envelope)
    }

    /**
     * Seal an event into an envelope (encrypted JSON string).
     * @param event The event to seal.
     * @return The sealed envelope as a JSON string.
     */
    private fun sealEvent(event: DeviceEvent): String {
        val jsonObject = JSONObject()
        jsonObject.put("eventId", event.eventId)
        jsonObject.put("eventType", event.eventType)
        jsonObject.put("deviceId", event.deviceId)
        jsonObject.put("payload", JSONObject(event.payload))
        jsonObject.put("targetDeviceId", event.targetDeviceId.orNull())
        jsonObject.put("timestamp", event.timestamp)

        val plainText = jsonObject.toString()
        val encrypted = sharedSecret.seal(plainText)
        return encrypted
    }

    /**
     * Open an envelope (encrypted JSON string) into a DeviceEvent.
     * @param envelope The sealed envelope.
     * @return The opened DeviceEvent.
     * @throws IOException If the envelope cannot be opened.
     */
    fun openEnvelope(envelope: String): DeviceEvent {
        val plainText = sharedSecret.open(envelope)
        val jsonObject = JSONObject(plainText)
        return DeviceEvent(
            eventId = jsonObject.getString("eventId"),
            eventType = jsonObject.getString("eventType"),
            deviceId = jsonObject.getString("deviceId"),
            payload = jsonObject.getJSONObject("payload").toMap(),
            targetDeviceId = jsonObject.optString("targetDeviceId"),
            timestamp = jsonObject.getLong("timestamp")
        )
    }

    /**
     * Add an event to the outbox to be sent.
     * @param event The event to send.
     * @param envelope The sealed envelope of the event.
     */
    fun queueOutbox(event: DeviceEvent, envelope: String) {
        mutex.withLock {
            outbox[event.eventId] = Pair(event, envelope)
            updatePendingEvents()
        }
    }

    /**
     * Mark an event as sent (remove from outbox).
     * @param eventId The ID of the event that was sent.
     */
    fun markSent(eventId: String) {
        mutex.withLock {
            outbox.remove(eventId)
            updatePendingEvents()
        }
    }

    /**
     * Get all pending outbox events.
     * @return A list of pairs (event, envelope) for events waiting to be sent.
     */
    fun pendingOutbox(): List<Pair<DeviceEvent, String>> {
        return mutex.withLock { outbox.entries.map { it.value to it.key } }
    }

    /**
     * Try to send the outbox events via the transport.
     */
    private fun trySendOutbox() {
        val toSend = mutex.withLock { outbox.toMap() }
        if (toSend.isEmpty()) return

        val sent = transport.flush(this, toSend)
        sent.forEach { eventId ->
            mutex.withLock {
                outbox.remove(eventId)
            }
        }
        updatePendingEvents()
    }

    private fun updatePendingEvents() {
        val pending = mutex.withLock { outbox.keys.toList() }
        _pendingEvents.value = pending.map { eventId ->
            mutex.withLock { outbox[eventId]?.first }!!
        }
    }

    /**
     * Receive and process incoming events from the transport.
     * This should be called periodically.
     */
    fun receiveEvents() {
        val envelopes = transport.receive(this, deviceId)
        envelopes.forEach { envelope ->
            try {
                val event = openEnvelope(envelope)
                // TODO: Dispatch event to registered handlers
                // For now, just log
                android.util.Log.d("RemoteNode", "Received event: $event")
            } catch (e: Exception) {
                android.util.Log.e("RemoteNode", "Failed to open envelope", e)
            }
        }
    }
}

/**
 * Simple data class representing a device event.
 */
data class DeviceEvent(
    val eventId: String,
    val eventType: String,
    val deviceId: String,
    val payload: Map<String, Any>,
    val targetDeviceId: String?,
    val timestamp: Long
)

/**
 * Shared secret for encryption and decryption.
 * This is a simplified version of the Python SharedSecret.
 */
class SharedSecret(private val key: ByteArray) {

    companion object {
        /** Generate a new random shared secret. */
        fun newInstance(): SharedSecret {
            val key = ByteArray(32)
            SecureRandom().nextBytes(key)
            return SharedSecret(key)
        }

        /** Create a shared secret from an exported base64 string. */
        fun fromExport(exported: String): SharedSecret {
            val key = Base64.decode(exported, Base64.DEFAULT)
            return SharedSecret(key)
        }
    }

    /** Export the shared secret as a base64 string. */
    fun export(): String {
        return Base64.encodeToString(key, Base64.DEFAULT)
    }

    /**
     * Seal (encrypt) a plaintext string.
     * In a real implementation, we would use AES-GCM with a purpose-derived key.
     * For simplicity, we're using a basic XOR with the key (NOT SECURE - for demonstration only).
     * DO NOT USE IN PRODUCTION.
     */
    fun seal(plainText: String): String {
        // TODO: Implement proper encryption (AES-GCM with HKDF)
        // This is a placeholder and insecure.
        val plainBytes = plainText.toByteArray()
        val encryptedBytes = ByteArray(plainBytes.size)
        for (i in plainBytes.indices) {
            encryptedBytes[i] = (plainBytes[i] xor key[i % key.size]).toByte()
        }
        return Base64.encodeToString(encryptedBytes, Base64.DEFAULT)
    }

    /**
     * Open (decrypt) a ciphertext string.
     * @param cipherText The encrypted string.
     * @return The decrypted plaintext string.
     * TODO: Implement proper decryption.
     */
    fun open(cipherText: String): String {
        // TODO: Implement proper decryption.
        val encryptedBytes = Base64.decode(cipherText, Base64.DEFAULT)
        val plainBytes = ByteArray(encryptedBytes.size)
        for (i in encryptedBytes.indices) {
            plainBytes[i] = (encryptedBytes[i] xor key[i % key.size]).toByte()
        }
        return String(plainBytes)
    }
}

/**
 * Interface for transporting events to and from the remote relay.
 */
interface RemoteTransport {
    /**
     * Send a batch of events to the relay.
     * @param node The node sending the events.
     * @param events The events to send.
     * @return The number of events sent.
     */
    fun flush(node: RemoteNode, events: Map<String, Pair<DeviceEvent, String>>): List<String>

    /**
     * Receive events for a given device from the relay.
     * @param node The node receiving the events.
     * @param deviceId The device ID to receive events for.
     * @return A list of envelopes (encrypted event data).
     */
    fun receive(node: RemoteNode, deviceId: String): List<String>
}

/**
 * A fake transport for demonstration purposes.
 * In a real implementation, this would communicate with the Render relay via HTTP.
 */
class FakeRemoteTransport : RemoteTransport {
    override fun flush(node: RemoteNode, events: Map<String, Pair<DeviceEvent, String>>): List<String> {
        // Simulate sending by just logging and returning the event IDs as "sent"
        events.forEach { (eventId, pair) ->
            android.util.Log.d("FakeRemoteTransport", "Sent event $eventId: ${pair.first}")
        }
        return events.keys.toList()
    }

    override fun receive(node: RemoteNode, deviceId: String): List<String> {
        // Simulate receiving by returning an empty list
        return emptyList()
    }
}