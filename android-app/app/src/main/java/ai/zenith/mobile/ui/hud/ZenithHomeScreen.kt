package ai.zenith.mobile.ui.hud

import android.content.Context
import android.os.VibrationEffect
import android.os.Vibrator
import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.*
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.node.*
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.*
import ai.zenith.mobile.R
import ai.zenith.mobile.ui.theme.ZenithTheme

/**
 * The main home screen of ZENITH Mobile, displaying the HUD.
 */
@Composable
fun ZenithHomeScreen(
    viewModel: ZenithHomeViewModel = androidx.lifecycle.hiltViewModel()
) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()

    ZenithTheme {
        // We use a Box to layer the HUD elements
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(Color(0xFF000000)) // Dark background
        ) {
            // Background elements (if any) go here

            // Central Orb
            ZenithOrb(
                state = state.orbState,
                modifier = Modifier
                    .align(alignment = Alignment.Center)
                    .size(200.dp)
            )

            // Activity Log (at the bottom)
            ActivityLog(
                activities = state.activityLog,
                modifier = Modifier
                    .align(alignment = Alignment.BottomCenter)
                    .fillMaxWidth()
                    .height(200.dp)
                    .padding(16.dp)
            )

            // Control Buttons (at the bottom, above the activity log or integrated)
            ControlButtons(
                isListening = state.isListening,
                isInterrupted = state.isInterrupted,
                onMicrophoneClick = { viewModel.onMicrophoneClicked() },
                onInterruptClick = { viewModel.onInterruptClicked() },
                onTextInputClick = { viewModel.onTextInputClicked() },
                modifier = Modifier
                    .align(alignment = Alignment.BottomCenter)
                    .fillMaxWidth()
                    .height(80.dp)
                    .padding(16.dp)
            )

            // Time at the top
            Text(
                text = state.currentTime,
                color = Color.White,
                modifier = Modifier
                    .align(alignment = Alignment.TopEnd)
                    .padding(16.dp)
            )
        }
    }
}
