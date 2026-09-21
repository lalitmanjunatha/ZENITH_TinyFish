package ai.zenith.mobile

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import ai.zenith.mobile.ui.theme.ZenithTheme

/**
 * Main activity for ZENITH Mobile application.
 * Sets up the Jetpack Compose UI and initializes the application.
 */
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            ZenithTheme {
                // Main UI will be implemented here
                ZenithHomeScreen()
            }
        }
    }
}
