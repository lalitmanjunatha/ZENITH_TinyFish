package ai.zenith.mobile.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.*
import androidx.compose.runtime.Composable

private val LightColors = lightColorScheme(
    primary = Color(0xFF00FFFF), // Cyan
    secondary = Color(0xFF00FF00), // Green
    background = Color.White,
    surface = Color(0xFFF5F5F5)
)

private val DarkColors = darkColorScheme(
    primary = Color(0xFF00FFFF), // Cyan
    secondary = Color(0xFF00FF00), // Green
    background = Color(0xFF000000), // Black
    surface = Color(0xFF121212)
)

@Composable
fun ZenithTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    val colors = if (darkTheme) DarkColors else LightColors

    MaterialTheme(
        colorScheme = colors,
        typography = Typography,
        content = content
    )
}

// We can also define a custom typography if needed, but for now we use the default.
private val Typography = Typography()
