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
import androidx.compose.ui.ExperimentalComposeUiApi
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
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
                else -> Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text("Compose Bench", fontSize = 22.sp)
                    Button(onClick = { panel = Panel.OpenAtOnce }, Modifier.testTag("open-panel")) { Text("Agent panel") }
                    Button(onClick = { panel = Panel.OpenOnceHidden }, Modifier.testTag("open-panel-hide")) { Text("Agent panel, hide first") }
                    Button(onClick = { agentTabs = true }, Modifier.testTag("open-agent-tabs")) { Text("Agent tabs") }
                    Button(onClick = { skill = true }, Modifier.testTag("open-skill")) { Text("Skill details") }
                    Button(onClick = { screen = "topics" }, Modifier.testTag("open-topics")) { Text("Topics") }
                    Button(onClick = { screen = "form" }, Modifier.testTag("open-form")) { Text("Form") }
                    Text(authorized, Modifier.testTag("authorized"))
                }
            }
        }
    }
    if (agentTabs) AgentTabs(onClose = { agentTabs = false })
    if (skill) SkillDetails(onClose = { skill = false })
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
        Button(onClick = onClose, Modifier.testTag("close-form")) { Text("Close form") }
    }
}
