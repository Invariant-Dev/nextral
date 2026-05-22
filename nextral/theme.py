DARK_CSS = """
/* ── Color Palette ─────────────────────────────────────── */
$bg:            #080c14;
$bg-panel:      #0c1220;
$bg-elevated:   #121b2e;
$bg-input:      #0f1828;
$border:        #1a2840;
$border-active: #2255a0;
$border-glow:   #3a7bd5;
$text:          #c8d8f0;
$text-muted:    #6a84a8;
$text-dim:      #2e4060;
$accent:        #4d9fff;
$accent-2:      #58d8c8;
$success:       #4ecf7e;
$warning:       #f0c040;
$danger:        #f05060;
$info:          #60c8e8;
$purple:        #b888ff;
$teal:          #40d8c0;

Screen {
    background: $bg;
    color: $text;
    layers: base overlay notifications;
}

/* ── App Header ─────────────────────────────────────────── */
#app-header {
    dock: top;
    height: 3;
    background: $bg-panel;
    border-bottom: solid $border-active;
    layout: horizontal;
    padding: 0 2;
}
#header-logo {
    color: $accent;
    text-style: bold;
    width: auto;
    content-align: left middle;
    padding-right: 3;
}
#header-spacer { width: 1fr; }
#header-stats {
    color: $text-muted;
    width: auto;
    content-align: right middle;
    padding: 0 2;
}
#header-time {
    color: $text-dim;
    width: auto;
    content-align: right middle;
    border-left: solid $border;
    padding: 0 0 0 2;
}

/* ── Right Stats Panel (the only "sidebar") ─────────────── */
StatsPanel {
    dock: right;
    width: 28;
    background: $bg-panel;
    border-left: solid $border;
    padding: 1 0;
    layout: vertical;
    overflow-y: auto;
}
StatsPanel.hidden { display: none; }

#sp-title {
    color: $accent;
    text-style: bold;
    padding: 0 2;
    height: 2;
    content-align: left middle;
}
.sp-rule {
    height: 1;
    background: $border;
    margin: 0;
}
.sp-gap  { height: 1; }
.sp-section {
    color: $text-dim;
    text-style: bold;
    padding: 0 2;
    height: 1;
    margin-top: 1;
}
.sp-bar    { height: 1; color: $text; padding: 0 0; }
.sp-spark  { height: 1; color: $text-dim; padding: 0 0; }
.sp-detail { height: 1; color: $text-dim; padding: 0 0; }
.sp-net    { height: 1; color: $text-muted; padding: 0 0; }
.sp-alert  { height: 1; color: $text-muted; padding: 0 2; }
.sp-proc   { height: 1; color: $text-dim; padding: 0 0; }

/* ── Main Content ───────────────────────────────────────── */
#main-content {
    layout: vertical;
    width: 1fr;
    height: 1fr;
}

/* ── Tabs ───────────────────────────────────────────────── */
TabbedContent {
    height: 1fr;
    background: $bg;
}
TabbedContent > TabPane {
    padding: 0;
    background: $bg;
    layout: horizontal;
}
Tabs {
    background: $bg-panel;
    border-bottom: solid $border;
    height: 2;
}
Tab {
    background: $bg-panel;
    color: $text-dim;
    padding: 0 3;
}
Tab.-active {
    background: $bg-elevated;
    color: $accent;
    text-style: bold;
    border-bottom: solid $accent;
}
Tab:hover { color: $text-muted; background: $bg-elevated; }

/* ── Terminal Pane ──────────────────────────────────────── */
TerminalPane {
    layout: vertical;
    height: 1fr;
    width: 1fr;
    border: solid $border;
    background: $bg;
}
TerminalPane:focus-within {
    border: solid $border-active;
}
TerminalPane RichLog {
    height: 1fr;
    background: $bg;
    color: $text;
    padding: 0 1;
    scrollbar-color: $border-active;
    scrollbar-background: $bg-panel;
    scrollbar-size: 1 1;
}

/* ── Input Bar ──────────────────────────────────────────── */
InputBar {
    background: $bg-panel;
    border-top: solid $border-active;
    padding: 0 1;
    layout: vertical;
    height: auto;
}
#prompt-label { display: none; }
#cmd-input {
    background: $bg-input;
    border: solid $border;
    color: $text;
    height: 3;
    padding: 0 1;
}
#cmd-input:focus {
    border: solid $border-glow;
    background: $bg-elevated;
}
#ghost-label {
    color: $text-dim;
    height: 0;
    display: none;
}
#ghost-label.visible {
    display: block;
    height: 1;
    padding: 0 2;
}

/* Slash suggestion dropdown — appears ABOVE input */
#slash-suggestions {
    background: $bg-elevated;
    border: solid $border-glow;
    border-title-color: $accent;
    max-height: 14;
    height: auto;
    scrollbar-color: $border-active;
    scrollbar-background: $bg-elevated;
    scrollbar-size: 1 1;
    margin: 0;
    padding: 0;
}
#slash-suggestions ListItem {
    background: $bg-elevated;
    padding: 0 2;
    height: 2;
    color: $text-muted;
}
#slash-suggestions ListItem:hover {
    background: $bg;
    color: $text;
}
#slash-suggestions ListItem.--highlight {
    background: $border-active;
    color: $text;
}

/* ── Status Bar ─────────────────────────────────────────── */
StatusBar {
    dock: bottom;
    height: 1;
    background: $bg-panel;
    border-top: solid $border;
    layout: horizontal;
    padding: 0 1;
    color: $text-muted;
}
#sb-left   { width: 1fr; content-align: left middle;   color: $text-muted; }
#sb-center { width: auto; content-align: center middle; color: $text-dim; }
#sb-right  { width: 1fr; content-align: right middle;   color: $text-dim; }

/* ── Full-Screen Dashboard ──────────────────────────────── */
DashboardScreen {
    background: $bg;
    layout: vertical;
    padding: 0;
}
#dash-main {
    layout: horizontal;
    height: 1fr;
    padding: 1;
}
#dash-left {
    layout: vertical;
    width: 2fr;
    padding-right: 1;
}
#dash-right {
    layout: vertical;
    width: 1fr;
}
#dash-metrics {
    layout: grid;
    grid-size: 2 2;
    grid-gutter: 1;
    height: 14;
    margin-bottom: 1;
}
#dash-procs { height: 1fr; }

CpuWidget {
    background: $bg-panel;
    border: solid $border;
    border-title-color: $accent-2;
    border-title-style: bold;
    padding: 1 2;
}
MemoryWidget {
    background: $bg-panel;
    border: solid $border;
    border-title-color: $purple;
    border-title-style: bold;
    padding: 1 2;
}
DiskWidget {
    background: $bg-panel;
    border: solid $border;
    border-title-color: $warning;
    border-title-style: bold;
    padding: 1 2;
}
NetworkWidget {
    background: $bg-panel;
    border: solid $border;
    border-title-color: $teal;
    border-title-style: bold;
    padding: 1 2;
}
ProcessWidget {
    background: $bg-panel;
    border: solid $border;
    border-title-color: $info;
    border-title-style: bold;
    height: 1fr;
}
AlertPanel {
    background: $bg-panel;
    border: solid $border;
    border-title-color: $danger;
    border-title-style: bold;
    height: 1fr;
}

/* ── Data Table ─────────────────────────────────────────── */
DataTable {
    background: $bg;
    color: $text;
    scrollbar-color: $border-active;
    scrollbar-background: $bg-panel;
    scrollbar-size: 1 1;
    height: 1fr;
}
DataTable > .datatable--header {
    background: $bg-elevated;
    color: $accent;
    text-style: bold;
}
DataTable > .datatable--cursor { background: $border-active; color: $text; }
DataTable > .datatable--odd-row { background: $bg; }
DataTable > .datatable--even-row { background: $bg-panel; }
DataTable > .datatable--hover { background: $bg-elevated; }

/* ── Command Palette ────────────────────────────────────── */
CommandPaletteModal { align: center middle; layer: overlay; }
#palette-container {
    background: $bg-elevated;
    border: solid $border-glow;
    border-title-color: $accent;
    border-title-style: bold;
    width: 72;
    max-height: 30;
    padding: 1 2;
}
#palette-input {
    background: $bg-input;
    border: solid $border-active;
    color: $text;
    margin-bottom: 1;
}
#palette-input:focus { border: solid $border-glow; }
#palette-list {
    height: auto;
    max-height: 20;
    background: $bg;
    scrollbar-color: $border-active;
}
ListView { background: $bg; padding: 0; }
ListItem {
    background: $bg;
    padding: 0 1;
    height: 2;
    color: $text-muted;
}
ListItem:hover { background: $bg-elevated; color: $text; }
ListItem.--highlight { background: $border-active; color: $text; }

/* ── Param / Confirm Dialogs ────────────────────────────── */
ParamDialog { align: center middle; layer: overlay; }
#param-box {
    background: $bg-elevated;
    border: solid $border-active;
    border-title-color: $accent;
    border-title-style: bold;
    width: 58;
    height: auto;
    padding: 1 2;
}
#param-input {
    background: $bg-input;
    border: solid $border;
    color: $text;
    margin: 1 0;
}
#param-input:focus { border: solid $border-glow; }
#param-buttons { layout: horizontal; height: 3; align: right middle; }

ConfirmModal { align: center middle; layer: overlay; }
#confirm-box {
    background: $bg-elevated;
    border: solid $danger;
    border-title-color: $danger;
    border-title-style: bold;
    width: 56;
    height: auto;
    padding: 1 2;
}
#confirm-message { color: $text; margin-bottom: 1; text-style: bold; }
#confirm-buttons { layout: horizontal; height: 3; align: right middle; }

/* ── Buttons ────────────────────────────────────────────── */
Button { min-width: 14; margin: 0 1; }
Button.-primary, Button.primary { background: $accent; color: $bg; text-style: bold; }
Button.-error,   Button.danger  { background: $danger; color: $bg; text-style: bold; }
Button.-default, Button.default { background: $bg-input; color: $text-muted; border: solid $border; }
Button:hover  { text-style: bold; }
Button:focus  { border: solid $border-glow; }

/* ── Notifications ──────────────────────────────────────── */
#notification-stack {
    dock: top;
    align: right top;
    width: auto;
    height: auto;
    margin: 4 4 0 0;
    layer: notifications;
}
.toast {
    background: $bg-elevated;
    border: solid $border-active;
    padding: 0 2;
    height: 3;
    width: 44;
    margin-bottom: 1;
}
.toast.info    { border: solid $info;    border-title-color: $info; }
.toast.success { border: solid $success; border-title-color: $success; }
.toast.warning { border: solid $warning; border-title-color: $warning; }
.toast.error   { border: solid $danger;  border-title-color: $danger; }

/* ── Log Screen ─────────────────────────────────────────── */
LogScreen { background: $bg; layout: vertical; }
#log-controls {
    height: 6;
    background: $bg-panel;
    border-bottom: solid $border;
    padding: 1 2;
    layout: vertical;
}
#log-path-input, #log-filter-input {
    background: $bg-input;
    border: solid $border;
    color: $text;
}
#log-path-input { margin-bottom: 1; }
#log-path-input:focus, #log-filter-input:focus { border: solid $border-glow; }
#log-status { color: $text-dim; height: 1; margin-top: 1; }
#log-output {
    background: $bg;
    height: 1fr;
    padding: 0 1;
    scrollbar-color: $border-active;
    scrollbar-background: $bg-panel;
}

/* ── Plugin Screen ──────────────────────────────────────── */
PluginScreen { background: $bg; }
#plugin-title {
    background: $bg-panel;
    border-bottom: solid $border;
    padding: 1 2;
    color: $accent;
    text-style: bold;
    height: 3;
    content-align: left middle;
}
#plugin-table { height: 1fr; padding: 1; }

/* ── Welcome Screen ─────────────────────────────────────── */
WelcomeScreen { background: $bg; align: center middle; }
#welcome-container {
    background: $bg-panel;
    border: solid $border-glow;
    border-title-color: $accent;
    border-title-style: bold;
    width: 70;
    height: auto;
    padding: 2 4;
}
#welcome-logo {
    color: $accent;
    text-style: bold;
    content-align: center middle;
    width: 100%;
    height: 8;
}
#welcome-tagline {
    color: $text-muted;
    content-align: center middle;
    width: 100%;
    margin-bottom: 2;
}
.setup-step {
    height: 3;
    padding: 0 2;
    layout: horizontal;
    border: solid $border;
    margin-bottom: 1;
    background: $bg-elevated;
}
.setup-step.done { border: solid $success; }
.step-icon   { width: 4;  content-align: left  middle; color: $accent; }
.step-label  { width: 1fr; content-align: left  middle; color: $text-muted; }
.step-status { width: 10; content-align: right middle; color: $text-dim; }
.step-status.done { color: $success; }
#welcome-steps   { height: auto; margin: 1 0; }
#welcome-actions { layout: horizontal; height: 3; align: center middle; margin-top: 2; }

/* ── Utility Classes ────────────────────────────────────── */
.label--muted  { color: $text-muted; }
.label--dim    { color: $text-dim; }
.label--accent { color: $accent; text-style: bold; }
.badge--success { color: $success; }
.badge--warning { color: $warning; }
.badge--danger  { color: $danger; }
.badge--info    { color: $info; }
.section-title  { color: $text-dim; text-style: bold; padding: 0 1; height: 1; }
"""

LIGHT_CSS = """
$bg:            #f4f6fa;
$bg-panel:      #eaeef5;
$bg-elevated:   #dce3ef;
$bg-input:      #ffffff;
$border:        #c0ccdc;
$border-active: #2a6fd4;
$border-glow:   #4a8fe8;
$text:          #1a2640;
$text-muted:    #4a6080;
$text-dim:      #8090a8;
$accent:        #1a6fd4;
$success:       #1a8f50;
$warning:       #c07010;
$danger:        #c03040;
$info:          #1090b8;
$purple:        #6040c0;
$teal:          #0090a0;

Screen { background: $bg; color: $text; layers: base overlay notifications; }

#app-header {
    dock: top; height: 3; background: $bg-panel;
    border-bottom: solid $border-active; layout: horizontal; padding: 0 2;
}
#header-logo { color: $accent; text-style: bold; width: auto; content-align: left middle; padding-right: 3; }
#header-spacer { width: 1fr; }
#header-stats { color: $text-muted; width: auto; content-align: right middle; padding: 0 2; }
#header-time { color: $text-dim; width: auto; content-align: right middle; border-left: solid $border; padding: 0 0 0 2; }

StatsPanel {
    dock: right; width: 28; background: $bg-panel;
    border-left: solid $border; padding: 1 0; layout: vertical; overflow-y: auto;
}
StatsPanel.hidden { display: none; }
#sp-title { color: $accent; text-style: bold; padding: 0 2; height: 2; content-align: left middle; }
.sp-rule { height: 1; background: $border; }
.sp-gap { height: 1; }
.sp-section { color: $text-dim; text-style: bold; padding: 0 2; height: 1; margin-top: 1; }
.sp-bar { height: 1; color: $text; }
.sp-spark { height: 1; color: $text-dim; }
.sp-detail { height: 1; color: $text-dim; }
.sp-net { height: 1; color: $text-muted; }
.sp-alert { height: 1; color: $text-muted; padding: 0 2; }
.sp-proc { height: 1; color: $text-dim; }

#main-content { layout: vertical; width: 1fr; height: 1fr; }
TabbedContent { height: 1fr; background: $bg; }
TabbedContent > TabPane { padding: 0; background: $bg; layout: horizontal; }
Tabs { background: $bg-panel; border-bottom: solid $border; height: 2; }
Tab { background: $bg-panel; color: $text-dim; padding: 0 3; }
Tab.-active { background: $bg-elevated; color: $accent; text-style: bold; border-bottom: solid $accent; }
Tab:hover { color: $text-muted; background: $bg-elevated; }

TerminalPane { border: solid $border; layout: vertical; height: 1fr; width: 1fr; }
TerminalPane:focus-within { border: solid $border-active; }
TerminalPane RichLog { background: $bg; color: $text; height: 1fr; padding: 0 1; }

InputBar { background: $bg-panel; border-top: solid $border-active; padding: 0 1; height: auto; layout: vertical; }
#prompt-label { display: none; }
#cmd-input { background: $bg-input; border: solid $border; color: $text; height: 3; padding: 0 1; }
#cmd-input:focus { border: solid $border-glow; }
#ghost-label { color: $text-dim; height: 0; display: none; }
#ghost-label.visible { display: block; height: 1; padding: 0 2; }
#slash-suggestions {
    background: $bg-elevated; border: solid $border-glow;
    max-height: 14; height: auto; margin: 0; padding: 0;
}
#slash-suggestions ListItem { background: $bg-elevated; padding: 0 2; height: 2; color: $text-muted; }
#slash-suggestions ListItem:hover { background: $bg; color: $text; }
#slash-suggestions ListItem.--highlight { background: $border-active; color: $bg; }

StatusBar { dock: bottom; height: 1; background: $bg-panel; border-top: solid $border; layout: horizontal; padding: 0 1; }
#sb-left { width: 1fr; content-align: left middle; }
#sb-center { width: auto; content-align: center middle; }
#sb-right { width: 1fr; content-align: right middle; }

DataTable { background: $bg; color: $text; height: 1fr; }
DataTable > .datatable--header { background: $bg-elevated; color: $accent; text-style: bold; }
DataTable > .datatable--cursor { background: $border-active; color: $bg; }

CommandPaletteModal { align: center middle; layer: overlay; }
#palette-container {
    background: $bg-elevated; border: solid $border-glow;
    border-title-color: $accent; width: 72; max-height: 30; padding: 1 2;
}
#palette-input { background: $bg-input; border: solid $border-active; color: $text; margin-bottom: 1; }
#palette-input:focus { border: solid $border-glow; }
#palette-list { height: auto; max-height: 20; background: $bg; }
ListView { background: $bg; padding: 0; }
ListItem { background: $bg; padding: 0 1; height: 2; color: $text-muted; }
ListItem:hover { background: $bg-elevated; color: $text; }
ListItem.--highlight { background: $border-active; color: $bg; }

ParamDialog { align: center middle; layer: overlay; }
#param-box { background: $bg-elevated; border: solid $border-active; border-title-color: $accent; width: 58; height: auto; padding: 1 2; }
#param-input { background: $bg-input; border: solid $border; color: $text; margin: 1 0; }
#param-input:focus { border: solid $border-glow; }
#param-buttons { layout: horizontal; height: 3; align: right middle; }

ConfirmModal { align: center middle; layer: overlay; }
#confirm-box { background: $bg-elevated; border: solid $danger; border-title-color: $danger; width: 56; height: auto; padding: 1 2; }
#confirm-message { color: $text; margin-bottom: 1; text-style: bold; }
#confirm-buttons { layout: horizontal; height: 3; align: right middle; }

Button { min-width: 14; margin: 0 1; }
Button.-primary, Button.primary { background: $accent; color: $bg; text-style: bold; }
Button.-error, Button.danger { background: $danger; color: $bg; text-style: bold; }
Button.-default, Button.default { background: $bg-input; color: $text-muted; border: solid $border; }
Button:hover { text-style: bold; }
Button:focus { border: solid $border-glow; }

LogScreen { background: $bg; layout: vertical; }
#log-controls { height: 6; background: $bg-panel; border-bottom: solid $border; padding: 1 2; layout: vertical; }
#log-path-input, #log-filter-input { background: $bg-input; border: solid $border; color: $text; }
#log-path-input { margin-bottom: 1; }
#log-path-input:focus, #log-filter-input:focus { border: solid $border-glow; }
#log-status { color: $text-dim; height: 1; margin-top: 1; }
#log-output { background: $bg; height: 1fr; padding: 0 1; }

PluginScreen { background: $bg; }
#plugin-title { background: $bg-panel; border-bottom: solid $border; padding: 1 2; color: $accent; text-style: bold; height: 3; content-align: left middle; }
#plugin-table { height: 1fr; padding: 1; }

WelcomeScreen { background: $bg; align: center middle; }
#welcome-container { background: $bg-panel; border: solid $border-glow; width: 70; height: auto; padding: 2 4; }
#welcome-logo { color: $accent; text-style: bold; content-align: center middle; width: 100%; height: 8; }
#welcome-tagline { color: $text-muted; content-align: center middle; width: 100%; margin-bottom: 2; }
.setup-step { height: 3; padding: 0 2; layout: horizontal; border: solid $border; margin-bottom: 1; background: $bg-elevated; }
.setup-step.done { border: solid $success; }
.step-icon { width: 4; content-align: left middle; color: $accent; }
.step-label { width: 1fr; content-align: left middle; color: $text-muted; }
.step-status { width: 10; content-align: right middle; color: $text-dim; }
.step-status.done { color: $success; }
#welcome-steps { height: auto; margin: 1 0; }
#welcome-actions { layout: horizontal; height: 3; align: center middle; margin-top: 2; }

DashboardScreen { background: $bg; layout: vertical; padding: 0; }
#dash-main { layout: horizontal; height: 1fr; padding: 1; }
#dash-left { layout: vertical; width: 2fr; padding-right: 1; }
#dash-right { layout: vertical; width: 1fr; }
#dash-metrics { layout: grid; grid-size: 2 2; grid-gutter: 1; height: 14; margin-bottom: 1; }
#dash-procs { height: 1fr; }
CpuWidget { background: $bg-panel; border: solid $border; padding: 1 2; }
MemoryWidget { background: $bg-panel; border: solid $border; padding: 1 2; }
DiskWidget { background: $bg-panel; border: solid $border; padding: 1 2; }
NetworkWidget { background: $bg-panel; border: solid $border; padding: 1 2; }
ProcessWidget { background: $bg-panel; border: solid $border; height: 1fr; }
AlertPanel { background: $bg-panel; border: solid $border; height: 1fr; }
"""


def get_css(theme: str) -> str:
    return LIGHT_CSS if theme == "light" else DARK_CSS
