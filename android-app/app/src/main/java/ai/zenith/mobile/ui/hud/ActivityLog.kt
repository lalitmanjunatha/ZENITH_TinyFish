package ai.zenith.mobile.ui.hud

import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.Text
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

/**
 * Displays the activity log.
 * @param activities List of activity strings to display.
 * @param modifier The modifier to apply to the activity log.
 */
@Composable
fun ActivityLog(
    activities: List<String>,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .background(Color(0xFF1A1A1A), shape = MaterialTheme.shapes.medium)
            .padding(8.dp)
    ) {
        Text(
            text = "ACTIVITY LOG",
            color = Color(0xFF00FFFF),
            fontSize = 14.sp,
            modifier = Modifier
                .fillMaxWidth()
                .padding(8.dp)
        )
        Divider(color = Color(0xFF00FFFF), thickness = 1.dp)
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(vertical = 4.dp)
        ) {
            items(activities) { activity ->
                Text(
                    text = activity,
                    color = Color.White,
                    fontSize = 12.sp,
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 8.dp, vertical = 2.dp)
                )
            }
        }
    }
}
