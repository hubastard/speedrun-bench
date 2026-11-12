package dev.speedrun.composebench

import android.content.Intent
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.BackHandler
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.ui.draw.drawBehind
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.pager.HorizontalPager
import androidx.compose.foundation.pager.rememberPagerState
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Tab
import androidx.compose.material3.TabRow
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TextField
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import android.view.WindowManager
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.platform.LocalView
import androidx.compose.ui.window.DialogWindowProvider
import androidx.compose.foundation.layout.Spacer
import androidx.compose.material3.OutlinedButton
import androidx.compose.ui.window.DialogProperties
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.ExperimentalComposeUiApi
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.material3.AlertDialog
import androidx.compose.ui.input.pointer.PointerEventPass
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.semantics.testTagsAsResourceId
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

// Compose Bench: a Jetpack Compose app (no other UI toolkit around it) with the Compose
// patterns UI test tools trip on, one screen each. Test tags are resource ids (`id:` in a flow),
// set again in the bottom sheet: it is a window of its own, which the root's setting misses.
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        enableEdgeToEdge()
        super.onCreate(savedInstanceState)
        setContent { MaterialTheme { App() } }
    }
}

private val PANEL_ROWS = listOf(
    "Inbox", "Today", "Calendar", "Tasks", "Notes", "Reminders", "Contacts", "Messages", "Files",
    "Photos", "Music", "Podcasts", "News", "Weather", "Travel", "Expenses", "Health", "Habits",
    "Morning briefing", "Evening recap", "Settings",
)

private enum class Panel { Closed, OpenAtOnce, OpenOnceHidden }

@OptIn(ExperimentalComposeUiApi::class)
@Composable
fun App() {
    var screen by remember { mutableStateOf("home") }
    var panel by remember { mutableStateOf(Panel.Closed) }
    var detail by remember { mutableStateOf<String?>(null) }
    var authorized by remember { mutableStateOf("Not authorized") }
    var agentTabs by remember { mutableStateOf(false) }
    var skill by remember { mutableStateOf(false) }
    var asking by remember { mutableStateOf(false) }
    var consent by remember { mutableStateOf("Consent: not asked") }
    var sends by remember { mutableIntStateOf(0) }
    var sent by remember { mutableStateOf("Sent: none") }
    val scope = rememberCoroutineScope()
    var notifications by remember { mutableStateOf("Notifications: not asked") }
    // Android's own permission dialog (Android 13+), another app's window over this one.
    val askNotifications = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) {
        notifications = if (it) "Notifications: allowed" else "Notifications: denied"
    }
    BackHandler(enabled = detail != null || screen != "home") {
        if (detail != null) detail = null else screen = "home"
    }
    Scaffold(Modifier.semantics { testTagsAsResourceId = true }) { padding ->
        Box(Modifier.padding(padding).fillMaxSize()) {
            val d = detail
            when {
                d != null -> Detail(d, onBack = { detail = null })
                screen == "topics" -> Topics(onClose = { screen = "home" })
                screen == "form" -> Form(onClose = { screen = "home" })
                screen == "tasks" -> Tasks(onClose = { screen = "home" })
                screen == "notes" -> Notes(onClose = { screen = "home" })
                else -> Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text("Compose Bench", fontSize = 22.sp)
                    Button(onClick = { panel = Panel.OpenAtOnce }, Modifier.testTag("open-panel")) { Text("Agent panel") }
                    Button(onClick = { panel = Panel.OpenOnceHidden }, Modifier.testTag("open-panel-hide")) { Text("Agent panel, hide first") }
                    Button(onClick = { agentTabs = true }, Modifier.testTag("open-agent-tabs")) { Text("Agent tabs") }
                    Button(onClick = { skill = true }, Modifier.testTag("open-skill")) { Text("Skill details") }
                    Button(onClick = { screen = "topics" }, Modifier.testTag("open-topics")) { Text("Topics") }
                    Button(onClick = { screen = "form" }, Modifier.testTag("open-form")) { Text("Form") }
                    Button(onClick = { screen = "tasks" }, Modifier.testTag("open-tasks")) { Text("Tasks") }
                    Button(onClick = { screen = "notes" }, Modifier.testTag("open-notes")) { Text("Notes") }
                    // Send: a press that shows nothing (no ripple, no state drawn) and acts 2 s later,
                    // as a request sent: a second tap sends it twice. Beside the consent's rows, so
                    // the last text still shows on a short screen (Api35's: 2340 px at 440 dpi).
                    Row(horizontalArrangement = Arrangement.spacedBy(24.dp), verticalAlignment = Alignment.CenterVertically) {
                        Button(onClick = { asking = true }, Modifier.testTag("ask-consent")) { Text("Ask consent") }
                        Text(
                            "Send",
                            Modifier.testTag("send")
                                .clickable(interactionSource = null, indication = null) {
                                    sends++
                                    scope.launch { delay(2000); sent = "Sent: $sends" }
                                }
                                .padding(12.dp),
                        )
                    }
                    Row(horizontalArrangement = Arrangement.spacedBy(24.dp)) {
                        Text(consent, Modifier.testTag("consent"))
                        Text(sent, Modifier.testTag("sent"))
                    }
                    Button(onClick = { askNotifications.launch(android.Manifest.permission.POST_NOTIFICATIONS) }, Modifier.testTag("ask-notifications")) { Text("Ask notifications") }
                    Text(notifications, Modifier.testTag("notifications"))
                    Text(authorized, Modifier.testTag("authorized"))
                }
            }
        }
    }
    if (agentTabs) AgentTabs(onClose = { agentTabs = false })
    if (skill) SkillDetails(onClose = { skill = false })
    if (asking) ConsentDialog(onAnswer = { consent = it; asking = false })
    if (panel != Panel.Closed) {
        AgentPanel(
            mode = panel,
            onOpen = { detail = it },
            onAuthorized = { authorized = it },
            onClose = { panel = Panel.Closed },
        )
    }
}

// A modal bottom sheet (its own window) with a lazy list longer than the screen (speedrun issue
// #9). Each row is a Material 3 Surface with an onClick, and opens its detail screen: at once,
// or once the sheet has hidden (hide(), then invokeOnCompletion, as Material's docs show). The
// header's button starts a plain Activity for a result (CloseActivity).
@OptIn(ExperimentalMaterial3Api::class, ExperimentalComposeUiApi::class)
@Composable
private fun AgentPanel(mode: Panel, onOpen: (String) -> Unit, onAuthorized: (String) -> Unit, onClose: () -> Unit) {
    val state = rememberModalBottomSheetState()
    val scope = rememberCoroutineScope()
    val context = LocalContext.current
    val authorize = rememberLauncherForActivityResult(ActivityResultContracts.StartActivityForResult()) {
        onAuthorized("Authorization browser closed")
    }
    ModalBottomSheet(onDismissRequest = onClose, sheetState = state) {
        Column(Modifier.fillMaxWidth().semantics { testTagsAsResourceId = true }) {
            Row(Modifier.fillMaxWidth().padding(horizontal = 16.dp), verticalAlignment = Alignment.CenterVertically) {
                Text("Agent panel", Modifier.weight(1f), fontSize = 20.sp)
                TextButton(
                    onClick = { authorize.launch(Intent(context, CloseActivity::class.java)) },
                    Modifier.testTag("authorize"),
                ) { Text("Authorize") }
            }
            LazyColumn(Modifier.fillMaxWidth().testTag("panel-list")) {
                items(PANEL_ROWS.size) { k ->
                    val label = PANEL_ROWS[k]
                    Surface(
                        onClick = {
                            if (mode == Panel.OpenAtOnce) {
                                onClose()
                                onOpen(label)
                            } else scope.launch { state.hide() }.invokeOnCompletion {
                                if (!state.isVisible) {
                                    onClose()
                                    onOpen(label)
                                }
                            }
                        },
                        modifier = Modifier.fillMaxWidth().height(64.dp).testTag("panel-row-${k + 1}"),
                    ) {
                        Box(contentAlignment = Alignment.CenterStart) {
                            Text(label, Modifier.padding(horizontal = 16.dp))
                        }
                    }
                }
            }
        }
    }
}

// Tabs in a bottom sheet (speedrun issue #9): leaving the Agents tab shows a dot on it, a
// 13 px node of its own. Compose sends accessibility events only while an accessibility service
// is on, so a test tool's node cache does not hear of the dot: the sheet's window has no class
// a tool can tell Compose by, and 60 numbers come first, past the ~50 nodes a read refreshes.
@OptIn(ExperimentalMaterial3Api::class, ExperimentalComposeUiApi::class)
@Composable
private fun AgentTabs(onClose: () -> Unit) {
    var tab by remember { mutableIntStateOf(1) }
    ModalBottomSheet(onDismissRequest = onClose, sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = true)) {
        Column(Modifier.fillMaxWidth().semantics { testTagsAsResourceId = true }) {
            Text("Agent tabs", Modifier.padding(16.dp), fontSize = 20.sp)
            repeat(6) { row ->
                Row(Modifier.padding(horizontal = 16.dp)) { repeat(10) { Text("${row * 10 + it} ", fontSize = 12.sp) } }
            }
            TabRow(selectedTabIndex = tab) {
                listOf("Activity", "Agents").forEachIndexed { k, label ->
                    Tab(selected = tab == k, onClick = { tab = k }, modifier = Modifier.testTag("agent-tab-$k")) {
                        Row(Modifier.height(48.dp), verticalAlignment = Alignment.CenterVertically) {
                            if (k == 1 && tab != 1) {
                                Box(
                                    Modifier.size(5.dp).clip(CircleShape).background(Color.Red)
                                        .semantics { contentDescription = "Agents, attention needed" }
                                )
                            }
                            Text(label, Modifier.padding(start = 6.dp))
                        }
                    }
                }
            }
            Text(if (tab == 0) "Recent activity" else "Your agents", Modifier.padding(16.dp))
        }
    }
}

// A detail sheet, and an editor sheet over it: the system back closes the editor, then the
// detail.
@OptIn(ExperimentalMaterial3Api::class, ExperimentalComposeUiApi::class)
@Composable
private fun SkillDetails(onClose: () -> Unit) {
    var editing by remember { mutableStateOf(false) }
    ModalBottomSheet(onDismissRequest = onClose) {
        Column(Modifier.fillMaxWidth().padding(16.dp).semantics { testTagsAsResourceId = true }, verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text("Daily tide report", fontSize = 20.sp)
            Text("Every morning, look up the tide tables and send a summary.")
            Button(onClick = { editing = true }, Modifier.testTag("edit-skill")) { Text("Edit skill") }
        }
    }
    if (editing) {
        var name by remember { mutableStateOf("Daily tide report") }
        ModalBottomSheet(onDismissRequest = { editing = false }, sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = true)) {
            Column(Modifier.fillMaxWidth().padding(16.dp).semantics { testTagsAsResourceId = true }, verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text("Edit the skill", fontSize = 20.sp)
                OutlinedTextField(name, { name = it }, Modifier.testTag("skill-name"), label = { Text("Skill name") })
                Button(onClick = { editing = false }, Modifier.testTag("save-skill")) { Text("Save") }
            }
        }
    }
}

// Tabs drawn over a list that runs under them (its top padding the tabs' height), whose
// running tasks show a small spinner each. The tabs are inset: what of the list they leave
// uncovered goes around them, and Compose reports the list's frame as that part's bounding
// box, the whole list. So the list's frame holds the tabs, and it holds spinners, but it is
// no loading overlay (a tap on a tab waited ~17 s in an app built so).
@Composable
private fun Tasks(onClose: () -> Unit) {
    var tab by remember { mutableIntStateOf(0) }
    Column(Modifier.fillMaxSize()) {
        Button(onClick = onClose, Modifier.padding(16.dp).testTag("close-tasks")) { Text("Close tasks") }
        Box(Modifier.fillMaxSize()) {
            LazyColumn(Modifier.fillMaxSize().testTag("task-list"), contentPadding = PaddingValues(top = 88.dp)) {
                items(12) { k ->
                    Row(Modifier.fillMaxWidth().padding(16.dp), verticalAlignment = Alignment.CenterVertically) {
                        Text(if (tab == 0) "Running task ${k + 1}" else "Done task ${k + 1}", Modifier.weight(1f))
                        if (tab == 0 && k % 3 == 0) CircularProgressIndicator(Modifier.size(16.dp))
                    }
                }
            }
            TabRow(selectedTabIndex = tab, Modifier.padding(horizontal = 24.dp, vertical = 16.dp).height(56.dp)) {
                listOf("Running", "Done").forEachIndexed { k, label ->
                    Tab(selected = tab == k, onClick = { tab = k }, text = { Text(label) })
                }
            }
        }
    }
}

// A dialog that takes no touch right after it comes, as Android's permission dialog ignored a
// tap ~150 ms after it came on CI's emulators: the first touch in its first second reaches no
// button (no ripple, nothing changes), and only a later one answers.
@Composable
private fun ConsentDialog(onAnswer: (String) -> Unit) {
    val shownAt = remember { android.os.SystemClock.uptimeMillis() }
    var ignored by remember { mutableStateOf(false) }
    AlertDialog(
        onDismissRequest = {},
        modifier = Modifier.pointerInput(Unit) {
            awaitPointerEventScope {
                var ignoring = false
                while (true) {
                    val event = awaitPointerEvent(PointerEventPass.Initial)
                    val down = event.changes.any { it.pressed && !it.previousPressed }
                    if (down) ignoring = !ignored && android.os.SystemClock.uptimeMillis() - shownAt < 1000
                    if (ignoring) {
                        ignored = true
                        event.changes.forEach { it.consume() }
                    }
                }
            }
        },
        title = { Text("Allow notifications?") },
        confirmButton = { TextButton(onClick = { onAnswer("Consent: given") }, Modifier.testTag("consent-allow")) { Text("Allow") } },
        dismissButton = { TextButton(onClick = { onAnswer("Consent: refused") }) { Text("Don't allow") } },
    )
}

@Composable
private fun Detail(label: String, onBack: () -> Unit) {
    Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text("Detail: $label", fontSize = 20.sp)
        Button(onClick = {}, Modifier.testTag("more-actions")) { Text("More actions") }
        Button(onClick = onBack, Modifier.testTag("detail-back")) { Text("Back to home") }
    }
}

// Material 3 tabs over a pager that follows the selected tab (speedrun issue #9). A page loads
// its content once the pager has settled on it, and the selected tab follows the settled page
// (a swipe). Each tab's label is listed beside the tab's own node, which covers it.
@Composable
private fun Topics(onClose: () -> Unit) {
    val pager = rememberPagerState { 4 }
    var selected by remember { mutableIntStateOf(0) }
    LaunchedEffect(selected) { pager.animateScrollToPage(selected) }
    LaunchedEffect(pager.settledPage) { selected = pager.settledPage }
    Column(Modifier.fillMaxSize()) {
        Button(onClick = onClose, Modifier.padding(16.dp).testTag("close-topics")) { Text("Close topics") }
        TabRow(selectedTabIndex = selected) {
            repeat(4) { k ->
                Tab(selected = selected == k, onClick = { selected = k }, text = { Text("Topic ${k + 1}") })
            }
        }
        HorizontalPager(pager, Modifier.fillMaxSize()) { page ->
            var loaded by remember { mutableStateOf(false) }
            LaunchedEffect(pager.settledPage) {
                if (pager.settledPage == page && !loaded) {
                    delay(300)
                    loaded = true
                }
            }
            Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                if (loaded) Text("Topic ${page + 1} loaded") else CircularProgressIndicator()
            }
        }
    }
}

// Material 3 text fields (speedrun issue #8): a tap on the second moves the focus there, and
// what is typed next goes to it. The third's test tag is on a column around it, as a design
// system's input puts it.
@Composable
private fun Form(onClose: () -> Unit) {
    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var code by remember { mutableStateOf("") }
    var handle by remember { mutableStateOf("") }
    var signedIn by remember { mutableStateOf("Not signed in") }
    var clearing by remember { mutableStateOf(false) }
    var cleared by remember { mutableStateOf("Not cleared") }
    val emailFocus = remember { FocusRequester() }
    LaunchedEffect(Unit) { emailFocus.requestFocus() }
    Column(Modifier.fillMaxSize().padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        OutlinedTextField(email, { email = it }, Modifier.testTag("email").focusRequester(emailFocus), label = { Text("Email") })
        OutlinedTextField(password, { password = it }, Modifier.testTag("password"), label = { Text("Password") })
        Column(Modifier.testTag("code").padding(4.dp)) {
            Text("Code")
            TextField(code, { code = it })
        }
        // The app changes what is typed (upper case): Compose restarts the keyboard's input on
        // each key.
        OutlinedTextField(
            handle, { handle = it.uppercase() }, Modifier.testTag("handle"), label = { Text("Handle") },
            supportingText = { Text(if (handle.length > 64) "Must be 64 characters or less." else "${handle.length} / 64") },
            isError = handle.length > 64,
        )
        Button(onClick = { signedIn = "Signed in as $email / $password / $code" }, Modifier.testTag("sign-in")) { Text("Sign in") }
        Text(signedIn, Modifier.testTag("signed-in"))
        Row(horizontalArrangement = Arrangement.spacedBy(16.dp), verticalAlignment = Alignment.CenterVertically) {
            Button(onClick = onClose, Modifier.testTag("close-form")) { Text("Close form") }
            Button(onClick = { clearing = true }, Modifier.testTag("open-clear")) { Text("Clear") }
            Text(cleared, Modifier.testTag("cleared"))
        }
    }
    if (clearing) ClearDialog(onAnswer = { cleared = it; clearing = false })
}

// A dialog whose field takes the focus as it opens, as wide as the screen, its window left where
// it is when the keyboard comes (adjust nothing): the keyboard covers its buttons, and a tap on
// one at its center lands on the keyboard. A Material AlertDialog moves up out of its way. Compose
// leaves out of the tree what the keyboard covers all of (a button's text, a whole button): on
// Api35 Cancel's top edge shows above the keyboard, its center under it, and it is found by its
// id; on a taller screen it is clear of the keyboard.
@Composable
private fun ClearDialog(onAnswer: (String) -> Unit) {
    var typed by remember { mutableStateOf("") }
    val focus = remember { FocusRequester() }
    LaunchedEffect(Unit) { focus.requestFocus() }
    Dialog(onDismissRequest = {}, properties = DialogProperties(usePlatformDefaultWidth = false)) {
        val window = (LocalView.current.parent as? DialogWindowProvider)?.window
        SideEffect { window?.setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_NOTHING) }
        Surface(Modifier.fillMaxWidth().padding(16.dp).semantics { testTagsAsResourceId = true }, shape = MaterialTheme.shapes.large) {
            Column(Modifier.padding(24.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                Text("Clear the form?", fontSize = 22.sp)
                Text(
                    "Everything typed in the form goes: the email, the password, the code and the " +
                        "handle. The fields start empty again, as when the form first opened, and " +
                        "nothing typed before can be brought back. Signing in again then needs " +
                        "every field typed anew. Clearing cannot be undone.",
                )
                Text("Enter your password to clear it.")
                OutlinedTextField(typed, { typed = it }, Modifier.fillMaxWidth().focusRequester(focus), label = { Text("Your password") })
                Spacer(Modifier.height(48.dp))
                Button(onClick = { onAnswer("Clear: done") }, Modifier.fillMaxWidth(), enabled = typed.isNotEmpty()) { Text("Clear") }
                OutlinedButton(onClick = { onAnswer("Clear: cancelled") }, Modifier.fillMaxWidth().testTag("clear-cancel")) { Text("Cancel") }
            }
        }
    }
}

// A text field that misses a key: its 10th edit, once, as a keyboard app on a slow emulator
// lost one now and then (one in ~200 keys, never the first of a word). Typing checks the field
// and types again from the character missed.
// For a slow app (not in a flow): `adb shell setprop debug.composebench.busy <ms>` holds the
// main thread that long on each edit, `debug.composebench.draw <ms>` on each frame of the dot's
// endless animation (an emulator with a software GPU drew the reporter's screens at 0.5-1 s a
// frame; at 800 ms, keys queued 10 s and the dispatcher dropped them).
private const val NOTES_MISSED_EDIT = 10

private fun prop(name: String): Long = try {
    Class.forName("android.os.SystemProperties").getMethod("get", String::class.java)
        .invoke(null, name).toString().toLongOrNull() ?: 0L
} catch (e: Exception) { 0L }

@Composable
private fun Notes(onClose: () -> Unit) {
    var notes by remember { mutableStateOf("") }
    var edits by remember { mutableIntStateOf(0) }
    Column(Modifier.fillMaxSize().padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        OutlinedTextField(
            notes,
            {
                if (++edits != NOTES_MISSED_EDIT) notes = it
                Thread.sleep(prop("debug.composebench.busy"))
            },
            Modifier.fillMaxWidth().testTag("notes"),
            label = { Text("Notes") },
        )
        Text("Saved: $notes", Modifier.testTag("saved"))
        val pulse by rememberInfiniteTransition().animateFloat(0.2f, 1f, infiniteRepeatable(tween(800), RepeatMode.Reverse))
        Box(Modifier.size(24.dp).drawBehind {
            Thread.sleep(prop("debug.composebench.draw"))
            drawCircle(Color(0xFF6750A4), radius = size.minDimension / 2 * pulse)
        })
        Button(onClick = onClose, Modifier.testTag("close-notes")) { Text("Close notes") }
    }
}
