# ZENITH Android agent

Open `android-app` in Android Studio, use JDK 17, and let Gradle install the declared Android dependencies.

The app is intentionally independent of the laptop: `CapabilityRegistry` hosts local tools and the Fabric layer only adds encrypted handoff. To enable delegated calls, install it, grant permissions, and explicitly select ZENITH as the default phone app. The current source provides the safe service boundary; production call audio/STT/TTS and relay transport are the next integration slice.

For local pairing, run `uvicorn fabric.relay:app --host 0.0.0.0 --port 8787` on the laptop and use its LAN IP as the relay URL. Deploy the same relay to Render for remote delivery. The pairing secret and relay token must never be committed.
