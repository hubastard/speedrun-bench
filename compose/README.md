# Compose Bench

A Jetpack Compose app, with no other UI toolkit around it, holding the Compose patterns UI test
tools trip on, one screen each, and the flows that test Speedrun on it (`flows/`). It is an
Android app. Speedrun Bench (`../app`) shows Compose too, but inside a React Native app.

| Screen | What it has |
|---|---|
| Agent panel | A modal bottom sheet (a window of its own) with a lazy list longer than the screen, whose rows are Material 3 `Surface`s with an `onClick`. A row opens its detail screen at once, or once the sheet has hidden (`hide()`, then `invokeOnCompletion`). Its Authorize button starts a plain `Activity` for a result: one View `Button` that finishes it. |
| Agent tabs | Tabs in a bottom sheet, below 60 numbers: leaving the Agents tab shows a 5 dp dot on it, a node of its own |
| Skill details | A detail sheet, and an editor sheet opened over it: the system back closes one, then the other |
| Topics | Material 3 tabs over a `HorizontalPager` that follows the selected tab; a page loads its content once the pager has settled on it |
| Form | Material 3 text fields: the focus moves on a tap, the third field's test tag is on a column around it, and the fourth changes what is typed (upper case, a 64-character counter), which restarts the keyboard's input on each key |

The flows come from issues filed against Speedrun: rows tapped after a scroll and a swipe in a
sheet, tabs, a dot that comes on a tab in a sheet, and an Activity's button tapped as its
window opens ([#9](https://github.com/hubastard/speedrun/issues/9)), and text fields that kept the focus
([#8](https://github.com/hubastard/speedrun/issues/8)).

## Run

```sh
./bench.sh build android   # a release build, installed on the first adb device
./bench.sh test android    # the flows with ../../speedrun
BOM=2025.06.00 ./bench.sh build android   # with older Compose libraries (a Compose BOM)
```

## Results

Each flow's time with Speedrun, from [`../results`](../results), written again on every full
run (where Speedrun's last runs are too); this README takes them when Speedrun ships a version.

<!-- results:compose -->
- Android: Speedrun v0.4.9 on 2026-11-06, on Apple M1 Pro (16 GB) with the Api35 emulator (Android 15).

| Flow | Android |
|---|---:|
| Agent tabs | 2.8 s |
| Authorize | 2.1 s |
| Form | 4.6 s |
| Sheet rows | 4.3 s |
| Skill back | 2.4 s |
| Tabs | 4.0 s |
| **All flows** | **20.3 s** |
<!-- /results:compose -->

## What Compose's tree looks like to a flow

- **A test tag is an `id:` only where `testTagsAsResourceId` is set.** Set on the screen's
  root, it does not reach a `ModalBottomSheet` or a `Dialog`: each is a window of its own.
  Set it in their content too.
- **A Material 3 button's or tab's label is listed beside the control's own node.** Speedrun's
  debug log says the label is "covered by" the button or the tab. The tap still goes to the
  label's center, which is inside the control.
- **Compose sends accessibility events only while an accessibility service is on**, and a
  test tool's connection is none. A tool's node cache then keeps nodes as they were, and a
  bottom sheet's or dialog's window has no `ComposeView` to tell Compose by: Speedrun knows
  Compose's nodes by their extra data keys (`androidx.compose.ui.semantics.id`).
- **A node fully covered by a sibling drawn after it is left out of the tree.** A clickable
  `Box` laid over a `Text` (its sibling, drawn after it) hides the text from every test tool:
  no flow can find it by its text. Put the click on the text's parent instead.
