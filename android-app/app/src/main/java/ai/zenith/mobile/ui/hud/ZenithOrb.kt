package ai.zenith.mobile.ui.hud

import androidx.compose.animation.*
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.*
import androidx.compose.ui.unit.*
import ai.zenith.mobile.R

/**
 * Represents the visual state of the ZENITH orb.
 */
enum class OrbState {
    IDLE,
    LISTENING,
    HEARING,
    THINKING,
    PLANNING,
    EXECUTING,
    SPEAKING,
    INTERRUPTED,
    REMOTE,
    ERROR,
    DND
}

/**
 * The central animated orb of ZENITH.
 * @param state The current state of the orb.
 * @param modifier The modifier to apply to the orb.
 */
@Composable
fun ZenithOrb(
    state: OrbState,
    modifier: Modifier = Modifier
) {
    val color by remember { state } {
        when (state) {
            OrbState.IDLE -> Color(0xFF00FFFF) // Cyan
            OrbState.LISTENING -> Color(0xFF00FF00) // Green
            OrbState.HEARING -> Color(0xFFFF00FF) // Magenta
            OrbState.THINKING -> Color(0xFFFFFF00) // Yellow
            OrbState.PLANNING -> Color(0xFFFF00FFFF) // Orange
            OrbState.EXECUTING -> Color(0xFFFF0000) // Red
            OrbState.SPEAKING -> Color(0xFF00FFFFFF) // Light Blue
            OrbState.INTERRUPTED -> Color(0xFF800080) // Purple
            OrbState.REMOTE -> Color(0xFF008000) // Dark Green
            OrbState.ERROR -> Color(0xFFFF0000) // Red (same as EXECUTING, but we can differentiate by animation)
            OrbState.DND -> Color(0xFF808080) // Gray
        }
    }

    // We'll use a simple animation for demonstration. In a real app, we'd use more complex animations.
    val infiniteTransition = rememberInfiniteTransition()
    val scale by infiniteTransition.animateFloat(
        initialValue = 0.9f,
        targetValue = 1.1f,
        animationSpec = infiniteRepeatable(
            animation = tween(1000, easingLinear),
            repeatMode = RepeatMode.Reverse
        )
    )

    Canvas(
        modifier = modifier
            .scale(scale)
            .size(200.dp)
    ) {
        // Draw outer ring
        drawCircle(
            color = color.copy(alpha = 0.2f),
            center = Offset(x = size.width / 2, y = size.height / 2),
            radius = size.width / 2 * 0.9f
        )
        // Draw inner circle
        drawCircle(
            color = color,
            center = Offset(x = size.width / 2, y = size.height / 2),
            radius = size.width / 2 * 0.5f
        )
        // Draw scanning lines (example for EXECUTING state)
        if (state == OrbState.EXECUTING) {
            val sweepAngle = (infiniteTransition.currentValue * 360) % 360
            drawArc(
                color = color,
                startAngle = sweepAngle,
                sweepAngle = 30f,
                useCenter = false,
                topLeft = Offset(
                    x = size.width / 2 * 0.1f,
                    y = size.height / 2 * 0.1f
                ),
                size = Size(
                    width = size.width * 0.8f,
                    height = size.height * 0.8f
                )
            )
        }
    }
}
