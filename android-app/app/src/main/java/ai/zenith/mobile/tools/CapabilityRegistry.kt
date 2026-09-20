package ai.zenith.mobile.tools

import ai.zenith.mobile.fabric.ActionRequest
import ai.zenith.mobile.fabric.RiskLevel
import org.json.JSONObject

/** Local tools stay usable even when the laptop and relay are offline. */
class CapabilityRegistry(private val context: android.content.Context) {
    private val handlers = mutableMapOf<String, (JSONObject) -> String>()
    init {
        handlers["app.open"] = { p -> context.packageManager.getLaunchIntentForPackage(p.getString("package"))?.let { context.startActivity(it.addFlags(android.content.Intent.FLAG_ACTIVITY_NEW_TASK)); "opened" } ?: "app_not_found" }
        handlers["media.play"] = { p -> context.startActivity(android.content.Intent(android.content.Intent.ACTION_VIEW, android.net.Uri.parse("https://www.youtube.com/results?search_query=${android.net.Uri.encode(p.getString("query"))}" )).addFlags(android.content.Intent.FLAG_ACTIVITY_NEW_TASK)); "opened_youtube" }
        handlers["device.status"] = { JSONObject().put("battery", "available").put("network", "available").toString() }
    }
    fun manifest() = handlers.keys.sorted()
    fun dispatch(request: ActionRequest): String {
        if (request.risk != RiskLevel.low || !request.trusted) return "approval_required"
        return handlers[request.actionName]?.invoke(request.parameters) ?: "unsupported_action"
    }
}
