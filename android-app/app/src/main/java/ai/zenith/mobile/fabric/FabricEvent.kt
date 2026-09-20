package ai.zenith.mobile.fabric

import org.json.JSONObject
import java.util.UUID

enum class EventType { presence, capability, notification, action_request, action_result, context_delta, file_offer, file_request, call_report, ack }
enum class RiskLevel { low, sensitive }

data class FabricEvent(
    val eventType: EventType, val originDeviceId: String, val payload: JSONObject,
    val targetDeviceId: String? = null, val expiresAt: Long? = null,
    val eventId: String = UUID.randomUUID().toString(), val createdAt: Long = System.currentTimeMillis(),
)

data class ActionRequest(val actionName: String, val parameters: JSONObject, val risk: RiskLevel,
                         val targetDeviceId: String, val trusted: Boolean = false)
