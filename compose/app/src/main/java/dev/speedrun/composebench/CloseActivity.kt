package dev.speedrun.composebench

import android.os.Bundle
import android.widget.Button
import androidx.activity.ComponentActivity

// A plain Activity whose whole content is one View Button that finishes it (speedrun issue
// #9), started for a result from the agent panel's sheet: its window opens over the sheet's,
// and a tap while that transition runs reaches no window at all.
class CloseActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(Button(this).apply {
            text = "Close authorization browser"
            setOnClickListener { finish() }
        })
    }
}
