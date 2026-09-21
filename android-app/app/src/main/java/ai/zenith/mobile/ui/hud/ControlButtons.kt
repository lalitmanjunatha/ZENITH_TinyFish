package ai.zenith.mobile.ui.hud

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.clickable
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

/**
 * Control buttons for the ZENITH HUD: Microphone, Interrupt, and Text Input.
 * @param isListening Whether the microphone is currently listening.
 * @param isInterrupted Whether the system is currently in an interrupted state.
 * @param onMicrophoneClick Callback for when the microphone button is clicked.
 * @param onInterruptClick Callback for when the interrupt button is clicked.
 * @param onTextInputClick Callback for when the text input button is clicked.
 * @param modifier The modifier to apply to the button container.
 */
@Composable
fun ControlButtons(
    isListening: Boolean,
    isInterrupted: Boolean,
    onMicrophoneClick: () -> Unit,
    onInterruptClick: () -> Unit,
    onTextInputClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier
            .background(Color(0xFF1A1A1A), shape = MaterialTheme.shapes.medium)
            .padding(8.dp)
    ) {
        Spacer(modifier = Modifier.weight(1f))
        IconButton(
            onClick = onMicrophoneClick,
            modifier = Modifier.size(48.dp)
        ) {
            Icon(
                imageVector = if (isListening) Icons.Default.Mic else Icons.Default.MicOff,
                contentDescription = if (isListening) "Microphone On" else "Microphone Off",
                tint = if (isListening) Color.Green else Color.Red
            )
        }
        Spacer(modifier = Modifier.width(16.dp))
        IconButton(
            onClick = onInterruptClick,
            modifier = Modifier.size(48.dp)
        ) {
            Icon(
                imageVector = Icons.Default.Close,
                contentDescription = "Interrupt",
                tint = if (isInterrupted) Color.Yellow else Color.White
            )
        }
        Spacer(modifier = Modifier.width(16.dp))
        IconButton(
            onClick = onTextInputClick,
            modifier = Modifier.size(48.dp)
        ) {
            Icon(
                imageVector = Icons.Default.Edit,
                contentDescription = "Text Input",
                tint = Color.White
            )
        }
        Spacer(modifier = Modifier.weight(1f))
    }
}
