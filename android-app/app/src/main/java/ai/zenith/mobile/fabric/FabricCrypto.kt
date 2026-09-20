package ai.zenith.mobile.fabric

import android.util.Base64
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import org.json.JSONObject
import java.security.SecureRandom
import javax.crypto.Cipher
import javax.crypto.spec.GCMParameterSpec

/** Stores the pairing secret only in Android Keystore-backed preferences. */
class FabricCrypto(private val context: android.content.Context) {
    private val prefs = EncryptedSharedPreferences.create(context, "zenith_fabric",
        MasterKey.Builder(context).setKeyScheme(MasterKey.KeyScheme.AES256_GCM).build(),
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM)
    fun savePairingSecret(base64: String) = prefs.edit().putString("pairing_secret", base64).apply()
    fun hasPairing() = prefs.contains("pairing_secret")
    fun seal(event: JSONObject): JSONObject {
        val key = Base64.decode(requireNotNull(prefs.getString("pairing_secret", null)), Base64.URL_SAFE)
        val nonce = ByteArray(12).also { SecureRandom().nextBytes(it) }
        val cipher = Cipher.getInstance("AES/GCM/NoPadding").apply { init(Cipher.ENCRYPT_MODE, javax.crypto.spec.SecretKeySpec(key, "AES"), GCMParameterSpec(128, nonce)) }
        val encrypted = cipher.doFinal(event.toString().toByteArray())
        return JSONObject().put("nonce", Base64.encodeToString(nonce, Base64.URL_SAFE or Base64.NO_WRAP)).put("ciphertext", Base64.encodeToString(encrypted, Base64.URL_SAFE or Base64.NO_WRAP)).put("purpose", "event")
    }
}
