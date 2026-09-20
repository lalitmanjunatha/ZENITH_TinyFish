package ai.zenith.mobile

import android.app.Activity
import android.os.Bundle
import ai.zenith.mobile.fabric.FabricCrypto
import ai.zenith.mobile.tools.CapabilityRegistry

class MainActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val capabilities = CapabilityRegistry(this).manifest()
        title = "ZENITH Mobile — ${capabilities.size} local capabilities"
        // Pairing UI and relay URL setup deliberately occur here, never from a background service.
        FabricCrypto(this)
    }
}
