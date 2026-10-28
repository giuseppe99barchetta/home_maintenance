const VERSION = "2.3.0";
const DAY_MS = 86_400_000;
const PRIORITY_WEIGHT = { high: 100, normal: 50, low: 0 };
const INTERVALS = ["days", "weeks", "months", "years"];

const I18N = {
  en: {
    now: "Up next", nothingNow: "Nothing to do right now", nothingNowHint: "Next one: {title}, {when}.", allClear: "No maintenance scheduled yet.",
    summary: "{overdue} overdue, {soon} in the next 7 days, {completed} completed so far",
    streakUnit: "weeks in a row", streakUnit1: "week in a row", streakBest: "Best: {n}", streakHint: "Weeks with no high-priority task left overdue.", streakEmpty: "Set some tasks to high priority to start a streak.", thisWeekOk: "This week is on track", thisWeekOpen: "Something is still open this week",
    search: "Search tasks", all: "All", overdue: "Overdue", dueSoon: "Next 7 days", snoozed: "Snoozed", timeline: "By date", labelsView: "By label",
    newTask: "New task", editTask: "Edit task", import: "Import", export: "Export",
    done: "Done", later2h: "In 2 hours", tomorrow: "Tomorrow", skip: "Skip", edit: "Edit", history: "History", delete: "Delete", save: "Save changes", create: "Create task", cancel: "Cancel", close: "Close",
    tabBasics: "Basics", tabSchedule: "Schedule", tabChecklist: "Checklist", tabMore: "More",
    title: "Name", titlePh: "e.g. Clean the bathroom", icon: "Icon", description: "Notes", url: "Reference link", openLink: "Open reference link", labels: "Labels", noLabels: "No labels yet. Create them in Settings → Labels.",
    every: "Repeat every", everyN: "Every {n} {unit}", every1_days: "Every day", every1_weeks: "Every week", every1_months: "Every month", every1_years: "Every year", lastPerformed: "Last done", days: "days", weeks: "weeks", months: "months", years: "years",
    scheduleMode: "How the next date is set", modeInterval: "From when I do it", modeIntervalHint: "Done late? The next one moves later too.", modeFixed: "Fixed rhythm", modeFixedHint: "Keeps the same weekday or day of the month.",
    priority: "Priority", prioHigh: "High", prioNormal: "Normal", prioLow: "Low", duration: "Estimated minutes",
    activeMonths: "Active months", activeMonthsHint: "Leave all off to keep it active all year.", allYear: "All year",
    steps: "Steps", stepPh: "Step {n}", addStep: "Add step", removeStep: "Remove step", noSteps: "Split a long task into small steps you can tick one by one.", autocomplete: "Mark the task done when the last step is ticked",
    notify: "Notify before it's due", notifyDays: "Days before", tag: "NFC tag", noTag: "No tag", smartEntity: "Complete automatically when this entity…", smartState: "…reaches this state",
    presets: "Start from a preset",
    aiTitle: "Describe the task", aiPh: "e.g. clean the dishwasher filter", aiFill: "Fill in with AI", aiWorking: "Preparing a proposal…", aiHint: "Uses the AI set up in Home Assistant. Local models can take a minute.", aiDone: "Proposal ready: check the fields, then create the task.", aiSteps: "Suggest steps with AI", aiStepsWorking: "Thinking of steps…", aiStepsDone: "Added {n} steps. Edit them as you like.", aiStepsNone: "No new steps to add.", aiNeedText: "Describe the task first.", aiNeedTitle: "Give the task a name first.", aiError: "The AI didn't answer: {msg}",
    dueToday: "Due today", overdueBy: "{days} days late", overdueBy1: "1 day late", dueIn: "In {days} days", dueIn1: "Tomorrow", offSeason: "Off season", snoozedUntil: "Snoozed", unknown: "No date",
    neverDone: "Never done", lastDone: "Last done {date}", minutes: "{n} min", stepsProgress: "{done}/{total} steps",
    noTasks: "Nothing here yet", noTasksHint: "Create your first recurring task, or start from a preset.", noMatch: "No tasks match this search.",
    created: "Task created", saved: "Changes saved", removed: "Task deleted", completedToast: "Marked as done", laterToast: "Snoozed for 2 hours", tomorrowToast: "Moved to tomorrow", skippedToast: "Skipped this time", imported: "Tasks imported", error: "That didn't work. Check the Home Assistant log.", titleRequired: "Give the task a name.",
    deleteQuestion: "Delete “{title}”?", deleteCopy: "Its history and settings are removed for good.", historyEmpty: "Not done yet.", historyDone: "Done", historySkipped: "Skipped", unlabelled: "No label", results: "{count} tasks", retry: "Try again",
  },
  it: {
    now: "Adesso", nothingNow: "Niente da fare adesso", nothingNowHint: "La prossima: {title}, {when}.", allClear: "Nessuna manutenzione in programma.",
    summary: "{overdue} scadute, {soon} nei prossimi 7 giorni, {completed} completate finora",
    streakUnit: "settimane di fila", streakUnit1: "settimana di fila", streakBest: "Record: {n}", streakHint: "Settimane senza attività ad alta priorità lasciate in ritardo.", streakEmpty: "Imposta priorità alta sulle attività importanti per iniziare una serie.", thisWeekOk: "Questa settimana è in regola", thisWeekOpen: "Questa settimana c'è ancora qualcosa da fare",
    search: "Cerca attività", all: "Tutte", overdue: "Scadute", dueSoon: "Prossimi 7 giorni", snoozed: "Rimandate", timeline: "Per data", labelsView: "Per etichetta",
    newTask: "Nuova attività", editTask: "Modifica attività", import: "Importa", export: "Esporta",
    done: "Fatto", later2h: "Tra 2 ore", tomorrow: "Domani", skip: "Salta", edit: "Modifica", history: "Storico", delete: "Elimina", save: "Salva modifiche", create: "Crea attività", cancel: "Annulla", close: "Chiudi",
    tabBasics: "Base", tabSchedule: "Pianificazione", tabChecklist: "Checklist", tabMore: "Avanzate",
    title: "Nome", titlePh: "es. Pulizia bagno", icon: "Icona", description: "Note", url: "Link di riferimento", openLink: "Apri il link di riferimento", labels: "Etichette", noLabels: "Nessuna etichetta. Puoi crearle da Impostazioni → Etichette.",
    every: "Ripeti ogni", everyN: "Ogni {n} {unit}", every1_days: "Ogni giorno", every1_weeks: "Ogni settimana", every1_months: "Ogni mese", every1_years: "Ogni anno", lastPerformed: "Ultima volta", days: "giorni", weeks: "settimane", months: "mesi", years: "anni",
    scheduleMode: "Come si calcola la prossima data", modeInterval: "Da quando la faccio", modeIntervalHint: "Se la fai in ritardo, slitta anche la successiva.", modeFixed: "Ritmo fisso", modeFixedHint: "Resta sempre lo stesso giorno della settimana o del mese.",
    priority: "Priorità", prioHigh: "Alta", prioNormal: "Media", prioLow: "Bassa", duration: "Minuti stimati",
    activeMonths: "Mesi attivi", activeMonthsHint: "Lasciali tutti spenti per tenerla attiva tutto l'anno.", allYear: "Tutto l'anno",
    steps: "Passaggi", stepPh: "Passaggio {n}", addStep: "Aggiungi passaggio", removeStep: "Rimuovi passaggio", noSteps: "Dividi un'attività lunga in piccoli passaggi da spuntare uno alla volta.", autocomplete: "Segna l'attività come fatta quando spunto l'ultimo passaggio",
    notify: "Notifica prima della scadenza", notifyDays: "Giorni prima", tag: "Tag NFC", noTag: "Nessun tag", smartEntity: "Completa da sola quando questa entità…", smartState: "…raggiunge questo stato",
    presets: "Parti da un preset",
    aiTitle: "Descrivi l'attività", aiPh: "es. pulire il filtro della lavastoviglie", aiFill: "Compila con AI", aiWorking: "Sto preparando la proposta…", aiHint: "Usa l'AI configurata in Home Assistant. Con i modelli locali può volerci un minuto.", aiDone: "Proposta pronta: controlla i campi e poi crea l'attività.", aiSteps: "Suggerisci passaggi con AI", aiStepsWorking: "Sto pensando ai passaggi…", aiStepsDone: "Ho aggiunto {n} passaggi: modificali come preferisci.", aiStepsNone: "Nessun passaggio nuovo da aggiungere.", aiNeedText: "Prima descrivi l'attività.", aiNeedTitle: "Prima dai un nome all'attività.", aiError: "L'AI non ha risposto: {msg}",
    dueToday: "Scade oggi", overdueBy: "In ritardo di {days} giorni", overdueBy1: "In ritardo di 1 giorno", dueIn: "Tra {days} giorni", dueIn1: "Domani", offSeason: "Fuori stagione", snoozedUntil: "Rimandata", unknown: "Senza data",
    neverDone: "Mai fatta", lastDone: "Ultima volta {date}", minutes: "{n} min", stepsProgress: "{done}/{total} passaggi",
    noTasks: "Ancora nessuna attività", noTasksHint: "Crea la prima attività ricorrente o parti da un preset.", noMatch: "Nessuna attività corrisponde alla ricerca.",
    created: "Attività creata", saved: "Modifiche salvate", removed: "Attività eliminata", completedToast: "Segnata come fatta", laterToast: "Rimandata di 2 ore", tomorrowToast: "Spostata a domani", skippedToast: "Saltata per questa volta", imported: "Attività importate", error: "Non è andata. Controlla il log di Home Assistant.", titleRequired: "Dai un nome all'attività.",
    deleteQuestion: "Eliminare «{title}»?", deleteCopy: "Storico e impostazioni vengono cancellati definitivamente.", historyEmpty: "Non ancora fatta.", historyDone: "Fatta", historySkipped: "Saltata", unlabelled: "Senza etichetta", results: "{count} attività", retry: "Riprova",
  },
};

const STYLES = `
:host{
  display:block;min-height:100vh;
  --bg:var(--primary-background-color,#111418);
  --card:var(--card-background-color,#1b1f24);
  --raise:color-mix(in srgb,var(--card) 90%,var(--primary-text-color,#fff) 10%);
  --line:color-mix(in srgb,var(--divider-color,#ffffff1f) 85%,transparent);
  --ink:var(--primary-text-color,#e8eaed);
  --mute:var(--secondary-text-color,#9aa0a6);
  --accent:var(--primary-color,#03a9f4);
  --on-accent:var(--text-primary-color,#fff);
  --ok:var(--success-color,#43a047);
  --warn:var(--warning-color,#f9ab00);
  --bad:var(--error-color,#db4437);
  --r-sm:8px;--r-md:12px;--r-lg:18px;
  background:var(--bg);color:var(--ink);
  font-family:var(--ha-font-family-body,var(--paper-font-body1_-_font-family,system-ui,-apple-system,"Segoe UI",sans-serif));
  font-size:15px;line-height:1.45;
}
*{box-sizing:border-box}
button,input,select,textarea{font:inherit;color:inherit}
button{cursor:pointer}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
[hidden]{display:none!important}

.top{position:sticky;top:0;z-index:20;height:56px;display:flex;align-items:center;gap:8px;padding:0 12px;background:color-mix(in srgb,var(--card) 94%,transparent);backdrop-filter:blur(14px);border-bottom:1px solid var(--line)}
.top h1{flex:1;min-width:0;margin:0;font-size:18px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.page{max-width:1180px;margin:0 auto;padding:24px 20px 72px}

.btn{display:inline-flex;align-items:center;justify-content:center;gap:6px;min-height:38px;padding:0 14px;border:1px solid var(--line);background:transparent;border-radius:var(--r-sm);font-weight:600;font-size:14px;white-space:nowrap}
.btn:hover{background:var(--raise)}
.btn.primary{background:var(--accent);border-color:var(--accent);color:var(--on-accent)}
.btn.primary:hover{filter:brightness(1.08)}
.btn.good{background:var(--ok);border-color:var(--ok);color:#fff}
.btn.due{color:var(--ok);border-color:color-mix(in srgb,var(--ok) 55%,var(--line))}
.btn.quiet{border-color:transparent;color:var(--mute)}
.btn.quiet:hover{color:var(--ink)}
.btn.danger{color:var(--bad)}
.btn.icon{width:38px;padding:0}
.btn[disabled]{opacity:.5;pointer-events:none}
.btn ha-icon{--mdc-icon-size:18px}

/* Up next: the one place with weight */
.now{display:grid;grid-template-columns:minmax(0,1fr) 300px;gap:16px;margin-bottom:28px}
.focus{position:relative;background:var(--card);border:1px solid var(--line);border-radius:var(--r-lg);padding:22px 24px 20px 28px;overflow:hidden}
.focus::before{content:"";position:absolute;left:0;top:0;bottom:0;width:6px;background:var(--prio,var(--accent))}
.focus.high{--prio:var(--bad)} .focus.low{--prio:var(--mute)} .focus.empty{--prio:var(--ok)}
.eyebrow{font-size:13px;color:var(--mute);margin:0 0 6px}
.focus h2{margin:0;font-size:clamp(24px,3.2vw,34px);line-height:1.15;font-weight:650;letter-spacing:-.015em}
.focus .facts{display:flex;flex-wrap:wrap;gap:6px 14px;margin:10px 0 0;color:var(--mute);font-size:14px}
.focus .facts .late{color:var(--bad);font-weight:600}
.focus .note{margin:10px 0 0;color:var(--mute);max-width:70ch}
.link{display:inline-flex;align-items:center;gap:6px;color:var(--accent);font-weight:600;text-decoration:none}
.link:hover{text-decoration:underline}
.link ha-icon{--mdc-icon-size:16px}
a.btn{color:inherit;text-decoration:none}
.focus .do{display:flex;flex-wrap:wrap;gap:8px;margin-top:18px}
.focus .do .btn.good{min-width:120px}

.steps{list-style:none;margin:16px 0 0;padding:0;display:flex;flex-direction:column;gap:2px;max-width:560px}
.step{position:relative;display:flex;align-items:center;gap:10px;padding:7px 8px;border-radius:var(--r-sm);cursor:pointer;user-select:none}
.step:hover{background:var(--raise)}
.step input{position:absolute;opacity:0;pointer-events:none}
.tick{flex:none;width:22px;height:22px;border-radius:6px;border:2px solid var(--line);display:grid;place-items:center;transition:background .12s,border-color .12s}
.tick svg{width:14px;height:14px;opacity:0}
.step input:checked + .tick{background:var(--ok);border-color:var(--ok)}
.step input:checked + .tick svg{opacity:1}
.step input:checked ~ span{color:var(--mute);text-decoration:line-through}
.step input:focus-visible + .tick{outline:2px solid var(--accent);outline-offset:2px}
.steps.compact .step{padding:4px 6px;font-size:14px}
.steps.compact .tick{width:18px;height:18px;border-radius:5px}

.streak{align-self:start;background:var(--card);border:1px solid var(--line);border-radius:var(--r-lg);padding:20px 20px 18px;display:flex;flex-direction:column;gap:10px}
.streak .big{display:flex;align-items:baseline;gap:8px}
.streak .big strong{font-size:44px;line-height:1;font-weight:700;letter-spacing:-.03em;font-variant-numeric:tabular-nums}
.streak .big span{color:var(--mute)}
.weeks{display:grid;grid-template-columns:repeat(9,1fr);grid-auto-rows:10px;gap:5px;height:10px;margin:2px 0}
.wk{display:block;height:10px;border-radius:3px;background:color-mix(in srgb,var(--bad) 35%,transparent)}
.wk.ok{background:var(--ok)}
.wk.pad{background:var(--line)}
.wk.now{background:transparent;border:2px dashed var(--line)}
.wk.now.ok{border-color:var(--ok)}
.streak small{color:var(--mute);font-size:13px}

.summary{color:var(--mute);margin:-14px 0 22px;font-size:14px}

/* List */
.listbar{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin-bottom:10px}
.search{flex:1 1 260px;min-width:0;height:40px;border:1px solid var(--line);background:var(--card);border-radius:var(--r-sm);padding:0 12px}
.seg{display:inline-flex;border:1px solid var(--line);border-radius:var(--r-sm);padding:2px;gap:2px;background:var(--card)}
.seg button{border:0;background:transparent;border-radius:6px;padding:6px 11px;font-size:13.5px;color:var(--mute);font-weight:550}
.seg button[aria-pressed="true"]{background:var(--raise);color:var(--ink)}
.group{margin-top:18px}
.group h3{display:flex;align-items:center;gap:8px;margin:0 0 6px;padding:0 4px;font-size:14px;font-weight:600;color:var(--mute)}
.group h3 .n{font-variant-numeric:tabular-nums}
.group.overdue h3{color:var(--bad)}
.rows{background:var(--card);border:1px solid var(--line);border-radius:var(--r-md);overflow:hidden}
.task{display:grid;grid-template-columns:40px minmax(0,1fr) auto;gap:12px;align-items:start;padding:12px 14px;border-top:1px solid var(--line)}
.task:first-child{border-top:0}
.ico{width:40px;height:40px;border-radius:10px;background:var(--raise);display:grid;place-items:center;color:var(--accent)}
.task.high .ico{color:var(--bad)}
.t-title{font-weight:600;overflow-wrap:anywhere}
.t-meta{display:flex;flex-wrap:wrap;gap:4px 12px;margin-top:3px;color:var(--mute);font-size:13.5px}
.t-meta .late{color:var(--bad);font-weight:600}
.t-meta .soon{color:var(--warn);font-weight:600}
.pill{display:inline-flex;align-items:center;gap:4px;font-size:12px;font-weight:600;padding:1px 8px;border-radius:999px;background:var(--raise);color:var(--mute)}
.pill.high{color:var(--bad);background:color-mix(in srgb,var(--bad) 14%,transparent)}
.labels{display:flex;flex-wrap:wrap;gap:4px;margin-top:6px}
.t-actions{display:flex;gap:4px;align-items:center}
.t-actions .more{display:flex;gap:2px}
.task .steps{margin-top:8px}
.bar{height:4px;border-radius:2px;background:var(--line);margin-top:8px;max-width:220px;overflow:hidden}
.bar i{display:block;height:100%;background:var(--ok)}
.empty{padding:48px 20px;text-align:center;color:var(--mute)}
.empty h3{color:var(--ink);margin:0 0 6px;font-size:18px}
.empty .btn{margin-top:14px}

/* Sheet (create / edit) */
.scrim{position:fixed;inset:0;z-index:60;background:color-mix(in srgb,#000 55%,transparent);animation:fade .16s ease-out}
.sheet{position:fixed;z-index:61;top:0;right:0;bottom:0;width:min(560px,100vw);display:flex;flex-direction:column;background:var(--card);border-left:1px solid var(--line);box-shadow:-24px 0 60px #0006;animation:slide-in .2s cubic-bezier(.2,.8,.2,1)}
.sheet-head{display:flex;align-items:center;gap:12px;padding:16px 16px 0 20px}
.sheet-head .ico{flex:none}
.sheet-head h2{flex:1;min-width:0;margin:0;font-size:19px;font-weight:650;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.tabs{display:flex;gap:2px;padding:12px 16px 0 16px;border-bottom:1px solid var(--line);overflow-x:auto;scrollbar-width:none}
.tabs button{position:relative;border:0;background:transparent;padding:10px 12px 12px;font-weight:600;font-size:14px;color:var(--mute);white-space:nowrap}
.tabs button[aria-selected="true"]{color:var(--ink)}
.tabs button[aria-selected="true"]::after{content:"";position:absolute;left:10px;right:10px;bottom:-1px;height:3px;border-radius:3px 3px 0 0;background:var(--accent)}
.tabs .count{margin-left:4px;color:var(--mute);font-weight:500}
.sheet-body{flex:1;overflow:auto;padding:20px}
.sheet-foot{display:flex;align-items:center;gap:8px;padding:12px 16px;border-top:1px solid var(--line);background:var(--card)}
.sheet-foot .spacer{flex:1}
.err{color:var(--bad);font-size:13.5px}

.field{display:flex;flex-direction:column;gap:6px;margin-bottom:18px}
.field > label,.field > .lbl{font-size:13.5px;font-weight:600}
.field small{color:var(--mute);font-size:13px}
.input,.field input:not([type=checkbox]):not([type=radio]),.field select,.field textarea{width:100%;min-height:42px;border:1px solid var(--line);background:var(--bg);border-radius:var(--r-sm);padding:9px 11px}
.field textarea{min-height:84px;resize:vertical}
.row2{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.with-icon{display:flex;gap:8px;align-items:center}
.with-icon .ico{flex:none;width:42px;height:42px}
input:focus,select:focus,textarea:focus{outline:none;border-color:var(--accent)!important;box-shadow:0 0 0 3px color-mix(in srgb,var(--accent) 22%,transparent)}

.choice{display:grid;gap:8px}
.choice.cols3{grid-template-columns:repeat(3,1fr)}
.choice.cols2{grid-template-columns:1fr 1fr}
.opt{position:relative;display:flex;flex-direction:column;gap:2px;border:1px solid var(--line);border-radius:var(--r-sm);padding:10px 12px;cursor:pointer;background:var(--bg)}
.opt input{position:absolute;opacity:0;pointer-events:none}
.opt b{font-weight:600;font-size:14px}
.opt span{color:var(--mute);font-size:12.5px;line-height:1.35}
.opt:has(input:checked){border-color:var(--accent);background:color-mix(in srgb,var(--accent) 10%,var(--bg))}
.opt.high:has(input:checked){border-color:var(--bad);background:color-mix(in srgb,var(--bad) 10%,var(--bg))}
.opt:has(input:focus-visible){outline:2px solid var(--accent);outline-offset:2px}

.months{display:grid;grid-template-columns:repeat(6,1fr);gap:6px}
.toggle{position:relative;display:grid;place-items:center;height:38px;border:1px solid var(--line);border-radius:var(--r-sm);font-size:13.5px;font-weight:550;cursor:pointer;background:var(--bg);color:var(--mute)}
.toggle input{position:absolute;opacity:0;pointer-events:none}
.toggle:has(input:checked){background:var(--accent);border-color:var(--accent);color:var(--on-accent)}
.toggle:has(input:focus-visible){outline:2px solid var(--accent);outline-offset:2px}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chips .toggle{height:34px;padding:0 12px}

.step-edit{display:flex;flex-direction:column;gap:6px;margin-bottom:10px}
.step-row{display:grid;grid-template-columns:22px minmax(0,1fr) 38px;gap:8px;align-items:center}
.step-row .num{color:var(--mute);font-size:13px;text-align:right;font-variant-numeric:tabular-nums}
.switch{display:flex;gap:10px;align-items:flex-start;cursor:pointer}
.switch input{width:18px;height:18px;margin-top:2px;accent-color:var(--accent)}
.ai{padding:14px;border:1px solid color-mix(in srgb,var(--accent) 35%,var(--line));border-radius:var(--r-md);background:color-mix(in srgb,var(--accent) 6%,var(--card))}
.ai-row{display:flex;gap:8px;align-items:flex-start}
.ai-row textarea{flex:1;min-height:42px!important}
.ai-row .btn{flex:none;min-height:42px}
.ai small,#ai-steps-msg{color:var(--mute)}
small.err,.ai small.err{color:var(--bad)}
.row-btns{display:flex;flex-wrap:wrap;gap:8px}
#ai-steps-msg:empty{display:none}
@media(max-width:640px){.ai-row{flex-direction:column}.ai-row .btn{width:100%}}
.presets{display:flex;flex-wrap:wrap;gap:6px}
.presets button{border:1px dashed var(--line);background:transparent;border-radius:999px;padding:6px 12px;font-size:13.5px}
.presets button:hover{border-style:solid;background:var(--raise)}

/* Dialogs (history, delete) */
.dialog{position:fixed;z-index:61;left:50%;top:50%;transform:translate(-50%,-50%);width:min(460px,calc(100vw - 32px));max-height:min(80vh,640px);display:flex;flex-direction:column;background:var(--card);border:1px solid var(--line);border-radius:var(--r-lg);box-shadow:0 24px 70px #0007;animation:pop .16s ease-out}
.dialog header{display:flex;align-items:center;gap:10px;padding:16px 16px 12px 20px}
.dialog header h2{flex:1;margin:0;font-size:18px;font-weight:650}
.dialog .body{padding:0 20px 16px;overflow:auto;color:var(--mute)}
.dialog footer{display:flex;justify-content:flex-end;gap:8px;padding:12px 16px;border-top:1px solid var(--line)}
.timeline{list-style:none;margin:0;padding:0}
.timeline li{display:flex;justify-content:space-between;gap:12px;padding:10px 0;border-top:1px solid var(--line);color:var(--ink)}
.timeline li:first-child{border-top:0}
.timeline li.skip{color:var(--mute)}

.toast{position:fixed;left:50%;bottom:24px;z-index:80;transform:translate(-50%,12px);background:var(--ink);color:var(--bg);border-radius:var(--r-sm);padding:10px 16px;font-weight:550;opacity:0;pointer-events:none;transition:opacity .18s,transform .18s}
.toast.show{opacity:1;transform:translate(-50%,0)}
.loading{padding:80px 20px;text-align:center;color:var(--mute)}

@keyframes fade{from{opacity:0}}
@keyframes slide-in{from{transform:translateX(40px);opacity:.4}}
@keyframes pop{from{opacity:0;transform:translate(-50%,-48%)}}
@keyframes rise{from{transform:translateY(40px);opacity:.4}}

@media(max-width:900px){.now{grid-template-columns:1fr}}
@media(max-width:640px){
  .page{padding:16px 12px 64px}
  .focus{padding:18px 16px 16px 22px}
  .task{grid-template-columns:36px minmax(0,1fr);padding:12px}
  .task .t-actions{grid-column:1 / -1;justify-content:flex-start;flex-wrap:wrap}
  .ico{width:36px;height:36px}
  .top .btn .txt{display:none}
  .sheet{top:auto;left:0;width:100vw;height:min(92vh,100%);border-left:0;border-top:1px solid var(--line);border-radius:var(--r-lg) var(--r-lg) 0 0;animation:rise .22s cubic-bezier(.2,.8,.2,1)}
  .sheet-head::before{content:"";position:absolute;left:50%;top:6px;width:40px;height:4px;margin-left:-20px;border-radius:2px;background:var(--line)}
  .sheet-head{position:relative;padding-top:20px}
  .row2,.choice.cols2{grid-template-columns:1fr}
  .months{grid-template-columns:repeat(4,1fr)}
}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
`;

const TICK = `<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3.5 8.5l3 3 6-7" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>`;

const esc = (v) => String(v ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const parseDate = (v) => { if (!v) return null; const d = new Date(v); return Number.isNaN(d.getTime()) ? null : d; };
const localInput = (v = new Date()) => { const d = v instanceof Date ? v : parseDate(v); if (!d) return ""; return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`; };
const dayNum = (d) => Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()) / DAY_MS;
const startOfToday = () => { const d = new Date(); d.setHours(0, 0, 0, 0); return d; };

function addInterval(date, value, type) {
  const d = new Date(date);
  if (type === "days") d.setDate(d.getDate() + value);
  else if (type === "weeks") d.setDate(d.getDate() + value * 7);
  else {
    const day = d.getDate(), months = type === "years" ? value * 12 : value;
    d.setDate(1); d.setMonth(d.getMonth() + months);
    d.setDate(Math.min(day, new Date(d.getFullYear(), d.getMonth() + 1, 0).getDate()));
  }
  d.setHours(0, 0, 0, 0);
  return d;
}

/** Mirrors schedule.effective_due_date in the integration. */
function dueDate(task) {
  let due = task.next_due_override ? parseDate(task.next_due_override) : null;
  if (!due) { const last = parseDate(task.last_performed); if (!last) return null; due = addInterval(last, Number(task.interval_value), task.interval_type); }
  const snooze = parseDate(task.snoozed_until); if (snooze && snooze > due) due = new Date(snooze);
  const months = Array.isArray(task.active_months) ? task.active_months : [];
  const seasonal = months.length && months.length < 12;
  const nextActive = (from) => { const d = new Date(from.getFullYear(), from.getMonth(), 1); for (let i = 0; i < 12; i++) { d.setMonth(d.getMonth() + 1); if (months.includes(d.getMonth() + 1)) return d; } return from; };
  if (seasonal && !months.includes(due.getMonth() + 1)) due = nextActive(due);
  const today = startOfToday();
  if (seasonal && !months.includes(today.getMonth() + 1) && due <= today) due = nextActive(today);
  due.setHours(0, 0, 0, 0);
  return due;
}

const safeUrl = (u) => { try { const x = new URL(String(u || "")); return x.protocol === "http:" || x.protocol === "https:" ? x.href : ""; } catch { return ""; } };
const priorityOf = (t) => (["high", "normal", "low"].includes(t.priority) ? t.priority : "normal");
const snoozedNow = (t) => { const s = parseDate(t.snoozed_until); return !!s && s > new Date(); };
const offSeason = (t) => Array.isArray(t.active_months) && t.active_months.length > 0 && t.active_months.length < 12 && !t.active_months.includes(new Date().getMonth() + 1);

class HomeMaintenancePanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    Object.assign(this, { _hass: null, _narrow: false, _loaded: false, _tasks: [], _registry: [], _labels: [], _presets: [], _stats: {}, _config: {}, _search: "", _filter: "all", _view: "timeline", _sheet: null, _dialog: null, _busy: null, _toastTimer: null, _ai: { available: false } });
    this._onKey = (e) => { if (e.key === "Escape" && (this._sheet || this._dialog)) { e.stopPropagation(); this._closeOverlay(); } };
    // Delegated listeners live on the shadow root, which survives re-renders.
    this.shadowRoot.addEventListener("click", (e) => { const el = e.target.closest("[data-act]"); if (el) { e.preventDefault(); this._act(el.dataset.act, el.dataset.id, el); } });
    this.shadowRoot.addEventListener("change", (e) => { const box = e.target.closest("input[data-step]"); if (box) this._checkStep(box.dataset.id, Number(box.dataset.step), box.checked); });
  }

  set hass(value) { this._hass = value; if (!this._loaded) { this._loaded = true; this._load(); } else this._wireMenu(); }
  set narrow(v) { this._narrow = v; this._wireMenu(); }
  set route(_v) {}
  set panel(_v) {}
  connectedCallback() { document.addEventListener("keydown", this._onKey, true); }
  disconnectedCallback() { document.removeEventListener("keydown", this._onKey, true); }

  /* ---------- i18n & formatting ---------- */
  _lang() { return (this._hass?.locale?.language || this._hass?.language || "en").split("-")[0] === "it" ? "it" : "en"; }
  _t(k, vars = {}) { let s = I18N[this._lang()][k] ?? I18N.en[k] ?? k; for (const [a, b] of Object.entries(vars)) s = s.replaceAll(`{${a}}`, String(b)); return s; }
  _date(v) { const d = v instanceof Date ? v : parseDate(v); if (!d) return "—"; try { return new Intl.DateTimeFormat(this._hass?.locale?.language || undefined, { day: "numeric", month: "short", year: d.getFullYear() === new Date().getFullYear() ? undefined : "numeric" }).format(d); } catch { return localInput(d); } }
  _months() { try { const f = new Intl.DateTimeFormat(this._hass?.locale?.language || undefined, { month: "short" }); return Array.from({ length: 12 }, (_, i) => f.format(new Date(2026, i, 15)).replace(".", "")); } catch { return ["1","2","3","4","5","6","7","8","9","10","11","12"]; } }
  _interval(t) { const n = Number(t.interval_value) || 1; return n === 1 ? this._t(`every1_${t.interval_type}`) : this._t("everyN", { n, unit: this._t(t.interval_type) }); }
  _prio(p) { return this._t(p === "high" ? "prioHigh" : p === "low" ? "prioLow" : "prioNormal"); }

  _status(task) {
    const due = dueDate(task);
    if (!due) return { kind: "unknown", delta: null, label: this._t("unknown"), due: null };
    const delta = dayNum(due) - dayNum(startOfToday());
    if (delta < 0) return { kind: "overdue", delta, label: delta === -1 ? this._t("overdueBy1") : this._t("overdueBy", { days: -delta }), due };
    if (delta === 0) return { kind: "today", delta, label: this._t("dueToday"), due };
    if (delta === 1) return { kind: "soon", delta, label: this._t("dueIn1"), due };
    if (delta <= 7) return { kind: "soon", delta, label: this._t("dueIn", { days: delta }), due };
    return { kind: "later", delta, label: this._date(due), due };
  }
  _isDue(t) { const s = this._status(t); return (s.kind === "overdue" || s.kind === "today" || s.kind === "unknown") && !snoozedNow(t); }
  _score(t) { const s = this._status(t); const late = s.delta !== null && s.delta < 0 ? Math.min(-s.delta, 10) : 0; return PRIORITY_WEIGHT[priorityOf(t)] + late * 5; }
  /** Same order as sensor.home_maintenance_next_task. */
  _queue() {
    return this._tasks.filter((t) => this._isDue(t)).sort((a, b) => {
      const sa = this._status(a), sb = this._status(b);
      return this._score(b) - this._score(a) || (sa.delta ?? 0) - (sb.delta ?? 0) || (Number(a.duration_minutes) || 1e4) - (Number(b.duration_minutes) || 1e4);
    });
  }
  _labelsFor(task) { const ent = this._registry.find((e) => e.unique_id === task.id && e.platform === "home_maintenance"); const ids = Array.isArray(ent?.labels) ? ent.labels : []; return ids.map((id) => this._labels.find((l) => l.label_id === id)).filter(Boolean); }

  /* ---------- data ---------- */
  async _load() {
    this.shadowRoot.innerHTML = `<style>${STYLES}</style><div class="loading">Home Maintenance…</div>`;
    try {
      const [config, registry, labels, presets] = await Promise.all([
        this._ws("get_config"), this._hass.callWS({ type: "config/entity_registry/list" }), this._hass.callWS({ type: "config/label_registry/list" }), this._ws("presets"),
      ]);
      this._ai = await this._ws("ai_status").catch(() => ({ available: false }));
      Object.assign(this, { _config: config || {}, _registry: Array.isArray(registry) ? registry : [], _labels: Array.isArray(labels) ? labels : [], _presets: Array.isArray(presets) ? presets : [] });
      await this._refresh();
    } catch (e) {
      console.error(e);
      this.shadowRoot.innerHTML = `<style>${STYLES}</style><div class="loading">${esc(this._t("error"))}<br><br><button class="btn" id="retry">${esc(this._t("retry"))}</button></div>`;
      this.shadowRoot.querySelector("#retry")?.addEventListener("click", () => this._load());
    }
  }
  async _refresh({ registry = false } = {}) {
    const calls = [this._ws("get_tasks"), this._ws("statistics")];
    if (registry) calls.push(this._hass.callWS({ type: "config/entity_registry/list" }));
    const [tasks, stats, reg] = await Promise.all(calls);
    this._tasks = Array.isArray(tasks) ? tasks : [];
    this._stats = stats || {};
    if (reg) this._registry = reg;
    this._render();
  }
  _ws(cmd, extra = {}) { return this._hass.callWS({ type: `home_maintenance/${cmd}`, ...extra }); }

  /* ---------- render ---------- */
  _render() {
    const title = this._config?.options?.sidebar_title || this._config?.data?.sidebar_title || "Home Maintenance";
    const scroll = this.shadowRoot.querySelector(".sheet-body")?.scrollTop;
    this.shadowRoot.innerHTML = `<style>${STYLES}</style>
      <header class="top">
        <ha-menu-button></ha-menu-button>
        <h1>${esc(title)}</h1>
        <button class="btn quiet" data-act="import" title="${esc(this._t("import"))}"><ha-icon icon="mdi:tray-arrow-up"></ha-icon><span class="txt">${esc(this._t("import"))}</span></button>
        <button class="btn quiet" data-act="export" title="${esc(this._t("export"))}"><ha-icon icon="mdi:tray-arrow-down"></ha-icon><span class="txt">${esc(this._t("export"))}</span></button>
        <button class="btn primary" data-act="new"><ha-icon icon="mdi:plus"></ha-icon><span class="txt">${esc(this._t("newTask"))}</span></button>
        <input type="file" id="import-file" accept="application/json" hidden>
      </header>
      <main class="page">
        ${this._nowSection()}
        ${this._summary()}
        <div class="listbar">
          <input class="search" id="search" type="search" placeholder="${esc(this._t("search"))}" value="${esc(this._search)}" aria-label="${esc(this._t("search"))}">
          <div class="seg" role="group">${[["all", "all"], ["overdue", "overdue"], ["soon", "dueSoon"], ["snoozed", "snoozed"]].map(([v, k]) => `<button data-filter="${v}" aria-pressed="${this._filter === v}">${esc(this._t(k))}</button>`).join("")}</div>
          <div class="seg" role="group">${[["timeline", "timeline"], ["labels", "labelsView"]].map(([v, k]) => `<button data-view="${v}" aria-pressed="${this._view === v}">${esc(this._t(k))}</button>`).join("")}</div>
        </div>
        <div id="list">${this._list()}</div>
      </main>
      ${this._overlay()}
      <div class="toast" role="status" aria-live="polite"></div>`;
    this._wire();
    if (scroll) { const b = this.shadowRoot.querySelector(".sheet-body"); if (b) b.scrollTop = scroll; }
  }

  _stepsHtml(t, compact = false) {
    const steps = Array.isArray(t.checklist) ? t.checklist : [];
    if (!steps.length) return "";
    const done = new Set(t.checklist_done || []);
    return `<ul class="steps${compact ? " compact" : ""}">${steps.map((s, i) => `<li><label class="step"><input type="checkbox" data-step="${i}" data-id="${esc(t.id)}" ${done.has(i) ? "checked" : ""} ${this._busy === t.id ? "disabled" : ""}><span class="tick">${TICK}</span><span>${esc(s)}</span></label></li>`).join("")}</ul>`;
  }

  _nowSection() {
    const next = this._queue()[0];
    let focus;
    if (next) {
      const s = this._status(next), p = priorityOf(next), busy = this._busy === next.id ? "disabled" : "";
      const facts = [
        s.kind === "overdue" ? `<span class="late">${esc(s.label)}</span>` : `<span>${esc(s.label)}</span>`,
        p !== "normal" ? `<span>${esc(this._t("priority"))}: ${esc(this._prio(p))}</span>` : "",
        next.duration_minutes ? `<span>${esc(this._t("minutes", { n: next.duration_minutes }))}</span>` : "",
        `<span>${esc(next.last_performed && (next.history || []).length ? this._t("lastDone", { date: this._date(next.last_performed) }) : this._t("neverDone"))}</span>`,
      ].join("");
      focus = `<section class="focus ${p}" aria-labelledby="now-title">
        <p class="eyebrow">${esc(this._t("now"))}</p>
        <h2 id="now-title">${esc(next.title)}</h2>
        <div class="facts">${facts}</div>
        ${next.description ? `<p class="note">${esc(next.description)}</p>` : ""}
        ${safeUrl(next.url) ? `<p class="note"><a class="link" href="${esc(safeUrl(next.url))}" target="_blank" rel="noopener noreferrer"><ha-icon icon="mdi:open-in-new"></ha-icon>${esc(this._t("openLink"))}</a></p>` : ""}
        ${this._stepsHtml(next)}
        <div class="do">
          <button class="btn good" data-act="complete" data-id="${esc(next.id)}" ${busy}><ha-icon icon="mdi:check"></ha-icon>${esc(this._t("done"))}</button>
          <button class="btn" data-act="later" data-id="${esc(next.id)}" ${busy}>${esc(this._t("later2h"))}</button>
          <button class="btn" data-act="skip" data-id="${esc(next.id)}" ${busy}>${esc(this._t("skip"))}</button>
          <button class="btn quiet" data-act="edit" data-id="${esc(next.id)}">${esc(this._t("edit"))}</button>
        </div>
      </section>`;
    } else {
      const upcoming = this._tasks.map((t) => [t, this._status(t)]).filter(([, s]) => s.due).sort((a, b) => a[1].due - b[1].due)[0];
      focus = `<section class="focus empty"><p class="eyebrow">${esc(this._t("now"))}</p><h2>${esc(this._t("nothingNow"))}</h2>
        <p class="note">${upcoming ? esc(this._t("nothingNowHint", { title: upcoming[0].title, when: upcoming[1].label.toLowerCase() })) : esc(this._t("allClear"))}</p></section>`;
    }
    return `<div class="now">${focus}${this._streakCard()}</div>`;
  }

  _streakCard() {
    const st = this._stats?.streak;
    if (!st) return "";
    const n = Number(st.current) || 0;
    const recent = Array.isArray(st.recent_weeks) ? st.recent_weeks.slice(-8) : [];
    const pads = Array.from({ length: 8 - recent.length }, () => `<i class="wk pad"></i>`).join("");
    const weeks = pads + recent.map((ok) => `<i class="wk ${ok ? "ok" : ""}"></i>`).join("") + `<i class="wk now ${st.current_week_ok ? "ok" : ""}" title="${esc(this._t(st.current_week_ok ? "thisWeekOk" : "thisWeekOpen"))}"></i>`;
    if (!st.tracked_tasks) return `<aside class="streak"><div class="big"><strong>–</strong></div><small>${esc(this._t("streakEmpty"))}</small></aside>`;
    return `<aside class="streak" aria-label="${esc(this._t("streakHint"))}">
      <div class="big"><strong>${n}</strong><span>${esc(this._t(n === 1 ? "streakUnit1" : "streakUnit"))}</span></div>
      <div class="weeks" role="img" aria-label="${esc(this._t(st.current_week_ok ? "thisWeekOk" : "thisWeekOpen"))}">${weeks}</div>
      <small>${esc(this._t(st.current_week_ok ? "thisWeekOk" : "thisWeekOpen"))}. ${esc(this._t("streakBest", { n: st.best || 0 }))}</small>
    </aside>`;
  }

  _summary() {
    const st = this._tasks.map((t) => this._status(t));
    return `<p class="summary">${esc(this._t("summary", { overdue: st.filter((s) => s.kind === "overdue").length, soon: st.filter((s) => s.kind === "today" || s.kind === "soon").length, completed: this._stats?.completed || 0 }))}</p>`;
  }

  _filtered() {
    const q = this._search.trim().toLowerCase();
    return this._tasks.filter((t) => {
      if (q) { const hay = `${t.title} ${t.description || ""} ${(t.checklist || []).join(" ")} ${this._labelsFor(t).map((l) => l.name).join(" ")}`.toLowerCase(); if (!hay.includes(q)) return false; }
      const k = this._status(t).kind;
      if (this._filter === "overdue") return k === "overdue";
      if (this._filter === "soon") return k === "today" || k === "soon";
      if (this._filter === "snoozed") return snoozedNow(t);
      return true;
    });
  }

  _groups(tasks) {
    if (this._view === "labels") {
      const map = new Map();
      for (const t of tasks) { const ls = this._labelsFor(t); const keys = ls.length ? ls.map((l) => l.name) : [this._t("unlabelled")]; for (const k of keys) { if (!map.has(k)) map.set(k, []); map.get(k).push(t); } }
      return [...map.entries()].sort((a, b) => a[0].localeCompare(b[0])).map(([k, v]) => ["label", k, v]);
    }
    const order = [["overdue", "overdue"], ["today", "dueToday"], ["soon", "dueSoon"], ["later", null], ["unknown", "unknown"]];
    const byKind = new Map(order.map(([k]) => [k, []]));
    for (const t of tasks) byKind.get(this._status(t).kind)?.push(t);
    for (const list of byKind.values()) list.sort((a, b) => (this._status(a).due ?? 0) - (this._status(b).due ?? 0));
    const laterLabel = this._lang() === "it" ? "Più avanti" : "Later";
    return order.filter(([k]) => byKind.get(k).length).map(([k, label]) => [k, label ? this._t(label) : laterLabel, byKind.get(k)]);
  }

  _list() {
    if (!this._tasks.length) return `<div class="rows"><div class="empty"><h3>${esc(this._t("noTasks"))}</h3><p>${esc(this._t("noTasksHint"))}</p><button class="btn primary" data-act="new">${esc(this._t("newTask"))}</button></div></div>`;
    const tasks = this._filtered();
    if (!tasks.length) return `<div class="rows"><div class="empty"><h3>${esc(this._t("noMatch"))}</h3></div></div>`;
    return this._groups(tasks).map(([kind, name, items]) => `<section class="group ${esc(kind)}"><h3>${esc(name)} <span class="n">${items.length}</span></h3><div class="rows">${items.map((t) => this._row(t)).join("")}</div></section>`).join("");
  }

  _row(t) {
    const s = this._status(t), p = priorityOf(t), busy = this._busy === t.id ? "disabled" : "";
    const steps = Array.isArray(t.checklist) ? t.checklist : [];
    const done = (t.checklist_done || []).length;
    const due = this._isDue(t);
    const statusCls = s.kind === "overdue" ? "late" : s.kind === "today" || s.kind === "soon" ? "soon" : "";
    const meta = [
      `<span class="${statusCls}">${esc(s.label)}</span>`,
      `<span>${esc(this._interval(t))}</span>`,
      steps.length ? `<span>${esc(this._t("stepsProgress", { done, total: steps.length }))}</span>` : "",
      t.duration_minutes ? `<span>${esc(this._t("minutes", { n: t.duration_minutes }))}</span>` : "",
    ].join("");
    const pills = [
      p === "high" ? `<span class="pill high">${esc(this._prio(p))}</span>` : "",
      snoozedNow(t) ? `<span class="pill">${esc(this._t("snoozedUntil"))}</span>` : "",
      offSeason(t) ? `<span class="pill">${esc(this._t("offSeason"))}</span>` : "",
      ...this._labelsFor(t).map((l) => `<span class="pill">${esc(l.name)}</span>`),
    ].filter(Boolean).join("");
    return `<article class="task ${p}">
      <div class="ico"><ha-icon icon="${esc(t.icon || "mdi:calendar-check")}"></ha-icon></div>
      <div>
        <div class="t-title">${esc(t.title)}</div>
        <div class="t-meta">${meta}</div>
        ${pills ? `<div class="labels">${pills}</div>` : ""}
        ${steps.length ? `<div class="bar" aria-hidden="true"><i style="width:${Math.round((done / steps.length) * 100)}%"></i></div>` : ""}
      </div>
      <div class="t-actions">
        <button class="btn${due ? " due" : ""}" data-act="complete" data-id="${esc(t.id)}" ${busy}><ha-icon icon="mdi:check"></ha-icon>${esc(this._t("done"))}</button>
        <div class="more">
          ${safeUrl(t.url) ? `<a class="btn icon quiet" href="${esc(safeUrl(t.url))}" target="_blank" rel="noopener noreferrer" title="${esc(this._t("openLink"))}" aria-label="${esc(this._t("openLink"))}"><ha-icon icon="mdi:open-in-new"></ha-icon></a>` : ""}
          <button class="btn icon quiet" data-act="history" data-id="${esc(t.id)}" title="${esc(this._t("history"))}" aria-label="${esc(this._t("history"))}"><ha-icon icon="mdi:history"></ha-icon></button>
          <button class="btn icon quiet" data-act="edit" data-id="${esc(t.id)}" title="${esc(this._t("edit"))}" aria-label="${esc(this._t("edit"))}"><ha-icon icon="mdi:pencil-outline"></ha-icon></button>
        </div>
      </div>
    </article>`;
  }

  /* ---------- overlays ---------- */
  _overlay() {
    if (this._sheet) return `<div class="scrim" data-act="close"></div>${this._sheetHtml()}`;
    if (this._dialog?.kind === "history") return `<div class="scrim" data-act="close"></div>${this._historyHtml(this._dialog.task)}`;
    if (this._dialog?.kind === "delete") return `<div class="scrim" data-act="close"></div>${this._deleteHtml(this._dialog.task)}`;
    return "";
  }

  _sheetHtml() {
    const { task, tab } = this._sheet, editing = !!task?.id;
    const t = task || {};
    const steps = Array.isArray(t.checklist) ? t.checklist : [];
    const tabs = [["basics", "tabBasics"], ["schedule", "tabSchedule"], ["checklist", "tabChecklist"], ["more", "tabMore"]];
    const selectedLabels = editing ? this._labelsFor(t).map((l) => l.label_id) : (t.labels || []);
    const months = new Set(t.active_months || []);
    const prio = priorityOf(t), mode = t.schedule_mode === "fixed" ? "fixed" : "interval";
    const radio = (name, value, current, title, hint, cls = "") => `<label class="opt ${cls}"><input type="radio" name="${name}" value="${value}" ${current === value ? "checked" : ""}><b>${esc(title)}</b>${hint ? `<span>${esc(hint)}</span>` : ""}</label>`;
    return `<form class="sheet" id="task-form" role="dialog" aria-modal="true" aria-labelledby="sheet-title" novalidate>
      <div class="sheet-head">
        <div class="ico"><ha-icon id="icon-preview" icon="${esc(t.icon || "mdi:calendar-check")}"></ha-icon></div>
        <h2 id="sheet-title">${esc(editing ? t.title : this._t("newTask"))}</h2>
        <button type="button" class="btn icon quiet" data-act="close" aria-label="${esc(this._t("close"))}"><ha-icon icon="mdi:close"></ha-icon></button>
      </div>
      <div class="tabs" role="tablist">${tabs.map(([id, k]) => `<button type="button" role="tab" data-tab="${id}" aria-selected="${tab === id}">${esc(this._t(k))}${id === "checklist" ? `<span class="count" id="steps-count">${steps.length || ""}</span>` : ""}</button>`).join("")}</div>
      <div class="sheet-body">
        <div role="tabpanel" data-panel="basics" ${tab === "basics" ? "" : "hidden"}>
          ${!editing && this._ai?.available ? `<div class="ai field">
            <label for="f-ai">${esc(this._t("aiTitle"))}</label>
            <div class="ai-row"><textarea id="f-ai" rows="2" maxlength="500" placeholder="${esc(this._t("aiPh"))}"></textarea>
            <button type="button" class="btn" data-act="ai-fill"><ha-icon icon="mdi:creation-outline"></ha-icon><span>${esc(this._t("aiFill"))}</span></button></div>
            <small id="ai-msg" role="status">${esc(this._t("aiHint"))}</small>
          </div>` : ""}
          ${!editing && this._presets.length ? `<div class="field"><span class="lbl">${esc(this._t("presets"))}</span><div class="presets">${this._presets.map((p, i) => `<button type="button" data-preset="${i}">${esc(p.title)}</button>`).join("")}</div></div>` : ""}
          <div class="field"><label for="f-title">${esc(this._t("title"))}</label><input id="f-title" name="title" maxlength="120" required value="${esc(t.title || "")}" placeholder="${esc(this._t("titlePh"))}" autocomplete="off"><span class="err" id="title-err" hidden>${esc(this._t("titleRequired"))}</span></div>
          <div class="field"><label for="f-icon">${esc(this._t("icon"))}</label><input id="f-icon" name="icon" value="${esc(t.icon || "mdi:calendar-check")}" placeholder="mdi:broom" autocomplete="off"></div>
          <div class="field"><label for="f-desc">${esc(this._t("description"))}</label><textarea id="f-desc" name="description">${esc(t.description || "")}</textarea></div>
          <div class="field"><label for="f-url">${esc(this._t("url"))}</label><input id="f-url" name="url" type="url" value="${esc(t.url || "")}" placeholder="https://"></div>
          <div class="field"><span class="lbl">${esc(this._t("labels"))}</span>${this._labels.length ? `<div class="chips">${this._labels.map((l) => `<label class="toggle"><input type="checkbox" name="labels" value="${esc(l.label_id)}" ${selectedLabels.includes(l.label_id) ? "checked" : ""}>${esc(l.name)}</label>`).join("")}</div>` : `<small>${esc(this._t("noLabels"))}</small>`}</div>
        </div>
        <div role="tabpanel" data-panel="schedule" ${tab === "schedule" ? "" : "hidden"}>
          <div class="row2">
            <div class="field"><label for="f-every">${esc(this._t("every"))}</label><div class="with-icon"><input id="f-every" name="interval_value" type="number" min="1" inputmode="numeric" required value="${esc(t.interval_value || 1)}" style="max-width:90px"><select name="interval_type" aria-label="${esc(this._t("every"))}">${INTERVALS.map((x) => `<option value="${x}" ${(t.interval_type || "weeks") === x ? "selected" : ""}>${esc(this._t(x))}</option>`).join("")}</select></div></div>
            <div class="field"><label for="f-last">${esc(this._t("lastPerformed"))}</label><input id="f-last" name="last_performed" type="date" value="${esc(t.last_performed ? String(t.last_performed).split("T")[0] : localInput())}"></div>
          </div>
          <div class="field"><span class="lbl">${esc(this._t("scheduleMode"))}</span><div class="choice cols2">${radio("schedule_mode", "interval", mode, this._t("modeInterval"), this._t("modeIntervalHint"))}${radio("schedule_mode", "fixed", mode, this._t("modeFixed"), this._t("modeFixedHint"))}</div></div>
          <div class="field"><span class="lbl">${esc(this._t("priority"))}</span><div class="choice cols3">${radio("priority", "high", prio, this._t("prioHigh"), "", "high")}${radio("priority", "normal", prio, this._t("prioNormal"), "")}${radio("priority", "low", prio, this._t("prioLow"), "")}</div></div>
          <div class="field"><label for="f-dur">${esc(this._t("duration"))}</label><input id="f-dur" name="duration_minutes" type="number" min="0" max="1440" inputmode="numeric" value="${esc(t.duration_minutes ?? "")}" style="max-width:140px"></div>
          <div class="field"><span class="lbl">${esc(this._t("activeMonths"))}</span><div class="months">${this._months().map((m, i) => `<label class="toggle"><input type="checkbox" name="active_months" value="${i + 1}" ${months.has(i + 1) ? "checked" : ""}>${esc(m)}</label>`).join("")}</div><small>${esc(this._t("activeMonthsHint"))}</small></div>
        </div>
        <div role="tabpanel" data-panel="checklist" ${tab === "checklist" ? "" : "hidden"}>
          <div class="field"><span class="lbl">${esc(this._t("steps"))}</span>
            <small id="steps-empty" ${steps.length ? "hidden" : ""}>${esc(this._t("noSteps"))}</small>
            <div class="step-edit" id="step-edit">${steps.map((s, i) => this._stepRow(s, i)).join("")}</div>
            <div class="row-btns"><button type="button" class="btn" data-act="add-step"><ha-icon icon="mdi:plus"></ha-icon>${esc(this._t("addStep"))}</button>${this._ai?.available ? `<button type="button" class="btn quiet" data-act="ai-steps"><ha-icon icon="mdi:creation-outline"></ha-icon><span>${esc(this._t("aiSteps"))}</span></button>` : ""}</div>
            <small id="ai-steps-msg" role="status"></small>
          </div>
          <label class="switch"><input type="checkbox" name="checklist_autocomplete" ${t.checklist_autocomplete === false ? "" : "checked"}><span>${esc(this._t("autocomplete"))}</span></label>
        </div>
        <div role="tabpanel" data-panel="more" ${tab === "more" ? "" : "hidden"}>
          <label class="switch field"><input type="checkbox" name="notify_enabled" ${t.notify_enabled ? "checked" : ""}><span>${esc(this._t("notify"))}</span></label>
          <div class="field"><label for="f-nd">${esc(this._t("notifyDays"))}</label><input id="f-nd" name="notify_before_days" type="number" min="0" max="365" value="${esc(t.notify_before_days ?? 0)}" style="max-width:140px"></div>
          <div class="field"><label for="f-tag">${esc(this._t("tag"))}</label><select id="f-tag" name="tag_id"><option value="">${esc(this._t("noTag"))}</option>${Object.entries(this._hass?.states || {}).filter(([id]) => id.startsWith("tag.")).map(([id, st]) => `<option value="${esc(id)}" ${id === t.tag_id ? "selected" : ""}>${esc(st.attributes?.friendly_name || id)}</option>`).join("")}</select></div>
          <div class="field"><label for="f-ent">${esc(this._t("smartEntity"))}</label><input id="f-ent" name="source_entity_id" list="hm-entities" value="${esc(t.source_entity_id || "")}" placeholder="binary_sensor.dishwasher" autocomplete="off"><datalist id="hm-entities">${Object.entries(this._hass?.states || {}).slice(0, 2000).map(([id, st]) => `<option value="${esc(id)}">${esc(st.attributes?.friendly_name || id)}</option>`).join("")}</datalist></div>
          <div class="field"><label for="f-state">${esc(this._t("smartState"))}</label><input id="f-state" name="source_state" value="${esc(t.source_state || "")}" placeholder="off" style="max-width:200px"></div>
        </div>
      </div>
      <div class="sheet-foot">
        ${editing ? `<button type="button" class="btn danger quiet" data-act="delete" data-id="${esc(t.id)}">${esc(this._t("delete"))}</button>` : ""}
        <span class="spacer"></span>
        <button type="button" class="btn" data-act="close">${esc(this._t("cancel"))}</button>
        <button type="submit" class="btn primary" ${this._busy === "form" ? "disabled" : ""}>${esc(editing ? this._t("save") : this._t("create"))}</button>
      </div>
    </form>`;
  }

  _stepRow(value, i) {
    return `<div class="step-row"><span class="num">${i + 1}</span><input class="input" name="checklist" value="${esc(value)}" maxlength="120" placeholder="${esc(this._t("stepPh", { n: i + 1 }))}" autocomplete="off"><button type="button" class="btn icon quiet" data-act="remove-step" aria-label="${esc(this._t("removeStep"))}"><ha-icon icon="mdi:close"></ha-icon></button></div>`;
  }

  _historyHtml(task) {
    const items = [...(task.history || []).map((d) => ["done", d]), ...(task.skipped || []).map((d) => ["skip", d])].sort((a, b) => String(b[1]).localeCompare(String(a[1])));
    return `<section class="dialog" role="dialog" aria-modal="true" aria-labelledby="dlg-title">
      <header><h2 id="dlg-title">${esc(task.title)}</h2><button class="btn icon quiet" data-act="close" aria-label="${esc(this._t("close"))}"><ha-icon icon="mdi:close"></ha-icon></button></header>
      <div class="body">${items.length ? `<ul class="timeline">${items.map(([k, d]) => `<li class="${k}"><span>${esc(this._t(k === "done" ? "historyDone" : "historySkipped"))}</span><span>${esc(this._date(d))}</span></li>`).join("")}</ul>` : `<p>${esc(this._t("historyEmpty"))}</p>`}</div>
    </section>`;
  }

  _deleteHtml(task) {
    return `<section class="dialog" role="alertdialog" aria-modal="true" aria-labelledby="dlg-title" aria-describedby="dlg-body">
      <header><h2 id="dlg-title">${esc(this._t("deleteQuestion", { title: task.title }))}</h2></header>
      <div class="body" id="dlg-body"><p>${esc(this._t("deleteCopy"))}</p></div>
      <footer><button class="btn" data-act="close" autofocus>${esc(this._t("cancel"))}</button><button class="btn primary" style="background:var(--bad);border-color:var(--bad)" data-act="confirm-delete" data-id="${esc(task.id)}">${esc(this._t("delete"))}</button></footer>
    </section>`;
  }

  /* ---------- events ---------- */
  _wireMenu() { const m = this.shadowRoot?.querySelector("ha-menu-button"); if (m && this._hass) { m.hass = this._hass; m.narrow = this._narrow; } }

  _wire() {
    const root = this.shadowRoot;
    this._wireMenu();
    root.querySelector("#search")?.addEventListener("input", (e) => { this._search = e.target.value; root.querySelector("#list").innerHTML = this._list(); });
    root.querySelectorAll("[data-filter]").forEach((b) => b.addEventListener("click", () => { this._filter = b.dataset.filter; this._render(); }));
    root.querySelectorAll("[data-view]").forEach((b) => b.addEventListener("click", () => { this._view = b.dataset.view; this._render(); }));
    root.querySelector("#import-file")?.addEventListener("change", (e) => this._importFile(e.target.files?.[0]));

    const form = root.querySelector("#task-form");
    if (form) {
      form.addEventListener("submit", (e) => { e.preventDefault(); this._submit(form); });
      form.querySelectorAll("[data-tab]").forEach((b) => b.addEventListener("click", () => this._showTab(b.dataset.tab)));
      form.querySelectorAll("[data-preset]").forEach((b) => b.addEventListener("click", () => this._applyPreset(form, Number(b.dataset.preset))));
      form.querySelector("#f-icon")?.addEventListener("input", (e) => root.querySelector("#icon-preview")?.setAttribute("icon", e.target.value || "mdi:calendar-check"));
      form.querySelector("#f-title")?.addEventListener("input", (e) => { root.querySelector("#title-err").hidden = true; if (!this._sheet.task?.id) root.querySelector("#sheet-title").textContent = e.target.value.trim() || this._t("newTask"); });
      form.querySelector("#step-edit")?.addEventListener("keydown", (e) => { if (e.key === "Enter" && e.target.name === "checklist") { e.preventDefault(); this._addStep(form, e.target.closest(".step-row")); } });
      requestAnimationFrame(() => this._sheet && (this._sheet.tab === "basics" ? form.querySelector("#f-ai") || form.querySelector("#f-title") : form.querySelector(`[data-panel="${this._sheet.tab}"] input:not([type=checkbox]):not([type=radio])`))?.focus());
    }
    root.querySelector(".dialog [autofocus], .dialog button")?.focus();
  }

  _showTab(tab) {
    if (!this._sheet) return;
    this._sheet.tab = tab;
    const root = this.shadowRoot;
    root.querySelectorAll("[data-tab]").forEach((b) => b.setAttribute("aria-selected", String(b.dataset.tab === tab)));
    root.querySelectorAll("[data-panel]").forEach((p) => { p.hidden = p.dataset.panel !== tab; });
    // Keep focus inside the sheet when the focused field was just hidden.
    if (!root.activeElement || root.activeElement.closest("[data-panel][hidden]")) root.querySelector(`[data-tab="${tab}"]`)?.focus({ focusVisible: false });
    root.querySelector(".sheet-body").scrollTop = 0;
  }

  _addStep(form, after = null) {
    const box = form.querySelector("#step-edit");
    const tmp = document.createElement("div");
    tmp.innerHTML = this._stepRow("", box.children.length);
    const row = tmp.firstElementChild;
    if (after?.nextSibling) box.insertBefore(row, after.nextSibling); else box.appendChild(row);
    this._renumberSteps(form);
    row.querySelector("input").focus();
  }

  _renumberSteps(form) {
    const rows = [...form.querySelectorAll("#step-edit .step-row")];
    rows.forEach((r, i) => { r.querySelector(".num").textContent = String(i + 1); r.querySelector("input").placeholder = this._t("stepPh", { n: i + 1 }); });
    form.querySelector("#steps-empty").hidden = rows.length > 0;
    form.querySelector("#steps-count").textContent = rows.length ? String(rows.length) : "";
  }

  _applyPreset(form, i) {
    const p = this._presets[i];
    if (!p) return;
    for (const [k, v] of Object.entries(p)) { const el = form.elements.namedItem(k); if (el && "value" in el) el.value = v; }
    this.shadowRoot.querySelector("#icon-preview")?.setAttribute("icon", p.icon || "mdi:calendar-check");
    this.shadowRoot.querySelector("#sheet-title").textContent = p.title;
    form.elements.namedItem("title")?.focus();
  }

  async _aiCall(button, msgEl, workingKey, fn) {
    const label = button.querySelector("span");
    const idle = label.textContent;
    button.disabled = true; label.textContent = this._t(workingKey);
    msgEl.classList.remove("err");
    try { return await fn(); }
    catch (e) { console.error(e); msgEl.textContent = this._t("aiError", { msg: e?.message || e?.code || "?" }); msgEl.classList.add("err"); return null; }
    finally { button.disabled = false; label.textContent = idle; }
  }

  async _aiFill(button) {
    const form = this.shadowRoot.querySelector("#task-form");
    const msg = this.shadowRoot.querySelector("#ai-msg");
    const text = form.querySelector("#f-ai").value.trim();
    if (!text) { msg.textContent = this._t("aiNeedText"); msg.classList.add("err"); form.querySelector("#f-ai").focus(); return; }
    const p = await this._aiCall(button, msg, "aiWorking", () => this._ws("ai_suggest_task", { description: text }));
    if (!p) return;
    const set = (name, value) => { const el = form.elements.namedItem(name); if (el && "value" in el && value !== undefined && value !== null) el.value = value; };
    set("title", p.title); set("icon", p.icon); set("description", p.description);
    set("interval_value", p.interval_value); set("interval_type", p.interval_type);
    set("duration_minutes", p.duration_minutes ?? "");
    form.querySelectorAll('input[name="priority"]').forEach((r) => { r.checked = r.value === p.priority; });
    form.querySelectorAll('input[name="active_months"]').forEach((c) => { c.checked = (p.active_months || []).includes(Number(c.value)); });
    this._setSteps(form, p.checklist || []);
    this.shadowRoot.querySelector("#icon-preview")?.setAttribute("icon", p.icon || "mdi:calendar-check");
    this.shadowRoot.querySelector("#sheet-title").textContent = p.title;
    this.shadowRoot.querySelector("#title-err").hidden = true;
    msg.textContent = this._t("aiDone");
  }

  async _aiSteps(button) {
    const form = this.shadowRoot.querySelector("#task-form");
    const msg = this.shadowRoot.querySelector("#ai-steps-msg");
    const title = String(form.elements.namedItem("title")?.value || "").trim();
    if (!title) { msg.textContent = this._t("aiNeedTitle"); msg.classList.add("err"); return; }
    const res = await this._aiCall(button, msg, "aiStepsWorking", () => this._ws("ai_suggest_steps", { title, description: String(form.elements.namedItem("description")?.value || "") }));
    if (!res) return;
    const current = [...form.querySelectorAll('#step-edit input[name="checklist"]')].map((i) => i.value.trim()).filter(Boolean);
    const known = new Set(current.map((x) => x.toLowerCase()));
    const fresh = (res.checklist || []).filter((x) => !known.has(String(x).toLowerCase()));
    this._setSteps(form, [...current, ...fresh]);
    msg.textContent = fresh.length ? this._t("aiStepsDone", { n: fresh.length }) : this._t("aiStepsNone");
  }

  _setSteps(form, steps) {
    const box = form.querySelector("#step-edit");
    box.innerHTML = steps.map((s, i) => this._stepRow(s, i)).join("");
    this._renumberSteps(form);
  }

  _payload(form) {
    const fd = new FormData(form);
    const num = (k, d = 0) => { const v = Number(fd.get(k)); return Number.isFinite(v) ? v : d; };
    return {
      title: String(fd.get("title") || "").trim(),
      interval_value: Math.max(1, num("interval_value", 1)),
      interval_type: String(fd.get("interval_type") || "weeks"),
      last_performed: String(fd.get("last_performed") || ""),
      icon: String(fd.get("icon") || "mdi:calendar-check").trim(),
      tag_id: String(fd.get("tag_id") || ""),
      labels: fd.getAll("labels").map(String),
      description: String(fd.get("description") || ""),
      url: String(fd.get("url") || ""),
      notify_enabled: fd.get("notify_enabled") !== null,
      notify_before_days: num("notify_before_days", 0),
      source_entity_id: String(fd.get("source_entity_id") || ""),
      source_state: String(fd.get("source_state") || ""),
      priority: String(fd.get("priority") || "normal"),
      duration_minutes: fd.get("duration_minutes") ? num("duration_minutes", 0) || null : null,
      schedule_mode: String(fd.get("schedule_mode") || "interval"),
      active_months: fd.getAll("active_months").map(Number),
      checklist: fd.getAll("checklist").map((s) => String(s).trim()).filter(Boolean),
      checklist_autocomplete: fd.get("checklist_autocomplete") !== null,
    };
  }

  async _submit(form) {
    const data = this._payload(form);
    if (!data.title) { this._showTab("basics"); this.shadowRoot.querySelector("#title-err").hidden = false; form.elements.namedItem("title")?.focus(); return; }
    const editing = this._sheet.task?.id;
    this._busy = "form";
    form.querySelector("[type=submit]").disabled = true;
    try {
      if (editing) await this._ws("update_task", { task_id: editing, updates: data });
      else await this._ws("add_task", data);
      this._sheet = null; this._busy = null;
      await this._refresh({ registry: true });
      this._toast(this._t(editing ? "saved" : "created"));
    } catch (e) {
      console.error(e); this._busy = null;
      form.querySelector("[type=submit]").disabled = false;
      this._toast(e?.message || this._t("error"));
    }
  }

  async _act(act, id, el) {
    const task = this._tasks.find((t) => t.id === id);
    switch (act) {
      case "new": this._sheet = { task: null, tab: "basics" }; this._render(); return;
      case "edit": if (task) { this._sheet = { task, tab: "basics" }; this._dialog = null; this._render(); } return;
      case "history": if (task) { this._dialog = { kind: "history", task }; this._render(); } return;
      case "delete": if (task) { this._sheet = null; this._dialog = { kind: "delete", task }; this._render(); } return;
      case "close": this._closeOverlay(); return;
      case "import": this.shadowRoot.querySelector("#import-file")?.click(); return;
      case "export": this._export(); return;
      case "add-step": this._addStep(this.shadowRoot.querySelector("#task-form")); return;
      case "remove-step": { const form = this.shadowRoot.querySelector("#task-form"); el.closest(".step-row")?.remove(); this._renumberSteps(form); return; }
      case "ai-fill": return this._aiFill(el);
      case "ai-steps": return this._aiSteps(el);
      case "complete": return this._run(id, "complete_task", {}, "completedToast");
      case "later": return this._run(id, "snooze_task", { hours: 2 }, "laterToast");
      case "tomorrow": return this._run(id, "snooze_task", { days: 1 }, "tomorrowToast");
      case "skip": return this._run(id, "skip_task", {}, "skippedToast");
      case "confirm-delete": this._dialog = null; return this._run(id, "remove_task", {}, "removed");
      default: return;
    }
  }

  _closeOverlay() {
    const wasEditing = this._sheet?.task?.id;
    this._sheet = null; this._dialog = null; this._render();
    if (wasEditing) this.shadowRoot.querySelector(`[data-act="edit"][data-id="${CSS.escape(wasEditing)}"]`)?.focus();
  }

  async _run(id, cmd, extra, msg) {
    this._busy = id; this._render();
    try { await this._ws(cmd, { task_id: id, ...extra }); this._busy = null; await this._refresh(); this._toast(this._t(msg)); }
    catch (e) { console.error(e); this._busy = null; this._render(); this._toast(this._t("error")); }
  }

  async _checkStep(id, index, checked) {
    try {
      const res = await this._ws("check_step", { task_id: id, index, checked });
      await this._refresh();
      if (res?.task_completed) this._toast(this._t("completedToast"));
    } catch (e) { console.error(e); this._toast(this._t("error")); await this._refresh(); }
  }

  async _export() {
    try {
      const data = await this._ws("export");
      const url = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], { type: "application/json" }));
      const a = document.createElement("a"); a.href = url; a.download = `home-maintenance-${localInput()}.json`; a.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    } catch (e) { console.error(e); this._toast(this._t("error")); }
  }

  async _importFile(file) {
    if (!file) return;
    try {
      const parsed = JSON.parse(await file.text());
      const tasks = Array.isArray(parsed) ? parsed : parsed.tasks;
      if (!Array.isArray(tasks)) throw new Error("Invalid export");
      await this._ws("import", { tasks });
      await this._refresh({ registry: true });
      this._toast(this._t("imported"));
    } catch (e) { console.error(e); this._toast(this._t("error")); }
  }

  _toast(text) {
    const el = this.shadowRoot?.querySelector(".toast");
    if (!el) return;
    el.textContent = text; el.classList.add("show");
    clearTimeout(this._toastTimer);
    this._toastTimer = setTimeout(() => el.classList.remove("show"), 2600);
  }
}

if (!customElements.get("home-maintenance-panel")) customElements.define("home-maintenance-panel", HomeMaintenancePanel);
