package ai.zenith.mobile.calls

import android.telecom.Call
import android.telecom.InCallService

/** Default-dialer entry point. Call audio/TTS is enabled only after user grants the dialer role. */
class ZenithInCallService : InCallService() {
    override fun onCallAdded(call: Call) {
        super.onCallAdded(call)
        // Delegation policy: only trusted contacts and only when both ZENITH sessions are inactive.
        // If either condition cannot be verified, leave normal Android ringing untouched.
    }
}
