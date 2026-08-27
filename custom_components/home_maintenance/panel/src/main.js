const VERSION = "1.5.2";
const DAY_MS = 86_400_000;

const STRINGS = {
  en: {
    subtitle: "Keep recurring home jobs visible, current, and easy to finish.",
    total: "Total tasks", overdue: "Overdue", dueSoon: "Due this week", onTrack: "On track",
    search: "Search maintenance tasks…", all: "All", newTask: "New task", addTask: "Add task",
    taskTitle: "Task title", interval: "Interval", every: "Every", lastPerformed: "Last performed",
    icon: "Icon", tag: "NFC tag", labels: "Labels", optional: "More options", noTag: "No tag",
    days: "days", weeks: "weeks", months: "months", day: "day", week: "week", month: "month",
    complete: "Complete", edit: "Edit", delete: "Delete", save: "Save changes", cancel: "Cancel",
    editTask: "Edit task", noTasks: "No maintenance tasks yet", noTasksHint: "Add the first recurring job to start tracking your home.",
    noMatch: "No tasks match this filter", noMatchHint: "Try another search or status filter.",
    dueToday: "Due today", overdueBy: "Overdue by {days}d", dueIn: "Due in {days}d", dueDate: "Due {date}",
    unknownDue: "Due date unavailable", lastDone: "Last done {date}", never: "Never completed",
    loading: "Loading maintenance tasks…", loadError: "Could not load Home Maintenance data.", retry: "Retry",
    required: "Add a title and a valid interval.", added: "Task added", updated: "Task updated", removed: "Task removed",
    completed: "Task completed", actionError: "Something went wrong. Please try again.", confirmDelete: "Delete “{title}”? This cannot be undone.",
    results: "{count} tasks", status: "Status", later: "Later", version: "Version"
  },
  it: {
    subtitle: "Tieni sotto controllo le manutenzioni ricorrenti di casa, senza dimenticarne nessuna.",
    total: "Attività totali", overdue: "Scadute", dueSoon: "Entro 7 giorni", onTrack: "In regola",
    search: "Cerca attività di manutenzione…", all: "Tutte", newTask: "Nuova attività", addTask: "Aggiungi attività",
    taskTitle: "Titolo attività", interval: "Intervallo", every: "Ogni", lastPerformed: "Ultima esecuzione",
    icon: "Icona", tag: "Tag NFC", labels: "Etichette", optional: "Altre opzioni", noTag: "Nessun tag",
    days: "giorni", weeks: "settimane", months: "mesi", day: "giorno", week: "settimana", month: "mese",
    complete: "Completa", edit: "Modifica", delete: "Elimina", save: "Salva modifiche", cancel: "Annulla",
    editTask: "Modifica attività", noTasks: "Nessuna manutenzione ancora", noTasksHint: "Aggiungi la prima attività ricorrente per iniziare a tenere traccia della casa.",
    noMatch: "Nessuna attività corrisponde ai filtri", noMatchHint: "Prova una ricerca o un filtro diverso.",
    dueToday: "Scade oggi", overdueBy: "Scaduta da {days}g", dueIn: "Tra {days}g", dueDate: "Scade {date}",
    unknownDue: "Scadenza non disponibile", lastDone: "Ultima volta {date}", never: "Mai completata",
    loading: "Caricamento manutenzioni…", loadError: "Impossibile caricare i dati di Home Maintenance.", retry: "Riprova",
    required: "Inserisci un titolo e un intervallo valido.", added: "Attività aggiunta", updated: "Attività aggiornata", removed: "Attività eliminata",
    completed: "Attività completata", actionError: "Qualcosa è andato storto. Riprova.", confirmDelete: "Eliminare “{title}”? L'operazione non può essere annullata.",
    results: "{count} attività", status: "Stato", later: "Più avanti", version: "Versione"
  },
  de: {
    subtitle: "Wiederkehrende Hausarbeiten im Blick behalten und rechtzeitig erledigen.",
    total: "Aufgaben gesamt", overdue: "Überfällig", dueSoon: "Diese Woche fällig", onTrack: "Im Plan",
    search: "Wartungsaufgaben suchen…", all: "Alle", newTask: "Neue Aufgabe", addTask: "Aufgabe hinzufügen",
    taskTitle: "Aufgabentitel", interval: "Intervall", every: "Alle", lastPerformed: "Zuletzt erledigt",
    icon: "Symbol", tag: "NFC-Tag", labels: "Labels", optional: "Weitere Optionen", noTag: "Kein Tag",
    days: "Tage", weeks: "Wochen", months: "Monate", day: "Tag", week: "Woche", month: "Monat",
    complete: "Erledigen", edit: "Bearbeiten", delete: "Löschen", save: "Änderungen speichern", cancel: "Abbrechen",
    editTask: "Aufgabe bearbeiten", noTasks: "Noch keine Wartungsaufgaben", noTasksHint: "Füge die erste wiederkehrende Aufgabe hinzu.",
    noMatch: "Keine Aufgaben entsprechen dem Filter", noMatchHint: "Versuche eine andere Suche oder einen anderen Filter.",
    dueToday: "Heute fällig", overdueBy: "Seit {days} T. überfällig", dueIn: "In {days} T. fällig", dueDate: "Fällig {date}",
    unknownDue: "Fälligkeit unbekannt", lastDone: "Zuletzt {date}", never: "Nie erledigt",
    loading: "Wartungsaufgaben werden geladen…", loadError: "Home-Maintenance-Daten konnten nicht geladen werden.", retry: "Erneut versuchen",
    required: "Titel und gültiges Intervall angeben.", added: "Aufgabe hinzugefügt", updated: "Aufgabe aktualisiert", removed: "Aufgabe gelöscht",
    completed: "Aufgabe erledigt", actionError: "Etwas ist schiefgelaufen. Bitte erneut versuchen.", confirmDelete: "„{title}“ löschen? Dies kann nicht rückgängig gemacht werden.",
    results: "{count} Aufgaben", status: "Status", later: "Später", version: "Version"
  }
};

const CSS = `
  :host {
    display: block;
    min-height: 100vh;
    color: var(--primary-text-color, #e8eaed);
    background: var(--lovelace-background, var(--primary-background-color, #0f1115));
    font-family: var(--paper-font-body1_-_font-family, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif);
    --hm-surface: var(--card-background-color, #181b20);
    --hm-surface-2: color-mix(in srgb, var(--card-background-color, #181b20) 88%, var(--primary-text-color, #fff) 12%);
    --hm-border: color-mix(in srgb, var(--divider-color, #ffffff1f) 72%, transparent);
    --hm-muted: var(--secondary-text-color, #9aa0a6);
    --hm-accent: var(--primary-color, #03a9f4);
    --hm-danger: var(--error-color, #db4437);
    --hm-success: var(--success-color, #43a047);
    box-sizing: border-box;
  }
  *, *::before, *::after { box-sizing: border-box; }
  button, input, select { font: inherit; }
  button { color: inherit; }
  .app-header {
    position: sticky; top: 0; z-index: 20;
    min-height: var(--header-height, 56px);
    display: flex; align-items: center; gap: 14px;
    padding: 0 20px;
    background: color-mix(in srgb, var(--app-header-background-color, var(--hm-surface)) 92%, transparent);
    color: var(--app-header-text-color, var(--primary-text-color));
    border-bottom: 1px solid var(--hm-border);
    backdrop-filter: blur(16px);
  }
  .title-block { min-width: 0; flex: 1; }
  .title { font-size: 18px; line-height: 1.2; font-weight: 650; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .header-version { color: var(--hm-muted); font-size: 12px; font-weight: 600; }
  .header-action {
    border: 0; border-radius: 10px; padding: 9px 13px; cursor: pointer;
    background: var(--hm-accent); color: var(--text-primary-color, #fff); font-weight: 650;
  }
  .page { max-width: 1480px; margin: 0 auto; padding: 28px 24px 48px; }
  .hero { display: flex; align-items: flex-end; justify-content: space-between; gap: 20px; margin-bottom: 22px; }
  .hero h1 { margin: 0 0 6px; font-size: clamp(26px, 3vw, 38px); line-height: 1.08; letter-spacing: -0.035em; }
  .hero p { margin: 0; max-width: 720px; color: var(--hm-muted); font-size: 15px; line-height: 1.5; }
  .stats { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; margin-bottom: 18px; }
  .stat {
    padding: 16px 17px; border-radius: 16px; background: var(--hm-surface); border: 1px solid var(--hm-border);
    min-height: 92px; display: flex; flex-direction: column; justify-content: space-between;
  }
  .stat-label { color: var(--hm-muted); font-size: 12px; font-weight: 650; text-transform: uppercase; letter-spacing: .045em; }
  .stat-value { font-size: 29px; line-height: 1; font-weight: 720; letter-spacing: -.03em; }
  .stat.overdue .stat-value { color: var(--hm-danger); }
  .layout { display: grid; grid-template-columns: minmax(0, 1fr) minmax(320px, 390px); gap: 18px; align-items: start; }
  .panel { background: var(--hm-surface); border: 1px solid var(--hm-border); border-radius: 18px; overflow: hidden; }
  .panel-head { padding: 16px; border-bottom: 1px solid var(--hm-border); display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
  .search-wrap { position: relative; flex: 1 1 260px; }
  .search-wrap::before { content: "⌕"; position: absolute; left: 12px; top: 50%; transform: translateY(-53%); color: var(--hm-muted); font-size: 19px; pointer-events: none; }
  .search { width: 100%; height: 40px; padding: 0 12px 0 36px; border: 1px solid var(--hm-border); border-radius: 11px; outline: none; color: var(--primary-text-color); background: var(--primary-background-color, #101216); }
  .search:focus, .field input:focus, .field select:focus { border-color: var(--hm-accent); box-shadow: 0 0 0 2px color-mix(in srgb, var(--hm-accent) 22%, transparent); }
  .filters { display: flex; gap: 6px; overflow-x: auto; }
  .filter { border: 1px solid var(--hm-border); background: transparent; border-radius: 999px; padding: 7px 11px; color: var(--hm-muted); cursor: pointer; white-space: nowrap; font-size: 13px; font-weight: 620; }
  .filter.active { color: var(--primary-text-color); background: var(--hm-surface-2); border-color: color-mix(in srgb, var(--hm-accent) 40%, var(--hm-border)); }
  .list-meta { padding: 11px 16px; color: var(--hm-muted); font-size: 12px; border-bottom: 1px solid var(--hm-border); }
  .task-list { display: flex; flex-direction: column; }
  .task { display: grid; grid-template-columns: 46px minmax(0, 1fr) auto; gap: 13px; align-items: center; padding: 15px 16px; border-bottom: 1px solid var(--hm-border); transition: background .16s ease; }
  .task:last-child { border-bottom: 0; }
  .task:hover { background: color-mix(in srgb, var(--hm-surface-2) 55%, transparent); }
  .task-icon { width: 42px; height: 42px; border-radius: 13px; display: grid; place-items: center; background: var(--hm-surface-2); color: var(--hm-accent); }
  .task-icon ha-icon { --mdc-icon-size: 21px; }
  .task-main { min-width: 0; }
  .task-top { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
  .task-title { font-size: 15px; font-weight: 680; min-width: 0; overflow: hidden; text-overflow: ellipsis; }
  .badge { display: inline-flex; align-items: center; min-height: 22px; padding: 3px 8px; border-radius: 999px; font-size: 11px; font-weight: 700; line-height: 1.2; background: var(--hm-surface-2); color: var(--hm-muted); }
  .badge.overdue { color: var(--hm-danger); background: color-mix(in srgb, var(--hm-danger) 13%, transparent); }
  .badge.today, .badge.soon { color: var(--warning-color, #f9ab00); background: color-mix(in srgb, var(--warning-color, #f9ab00) 13%, transparent); }
  .task-meta { margin-top: 5px; color: var(--hm-muted); font-size: 12.5px; line-height: 1.45; display: flex; gap: 7px; flex-wrap: wrap; }
  .labels { margin-top: 7px; display: flex; gap: 5px; flex-wrap: wrap; }
  .label-chip { font-size: 10.5px; padding: 2px 7px; border-radius: 6px; background: var(--hm-surface-2); color: var(--hm-muted); }
  .task-actions { display: flex; gap: 6px; align-items: center; }
  .action { height: 34px; border: 1px solid var(--hm-border); background: transparent; border-radius: 9px; padding: 0 10px; cursor: pointer; font-size: 12px; font-weight: 650; }
  .action:hover { background: var(--hm-surface-2); }
  .action.primary { border-color: color-mix(in srgb, var(--hm-success) 35%, var(--hm-border)); color: var(--hm-success); }
  .action.danger { color: var(--hm-danger); }
  .action:disabled { opacity: .48; cursor: wait; }
  .empty { padding: 64px 28px; text-align: center; }
  .empty-icon { width: 54px; height: 54px; margin: 0 auto 14px; border-radius: 17px; display: grid; place-items: center; background: var(--hm-surface-2); font-size: 24px; }
  .empty h3 { margin: 0 0 6px; font-size: 17px; }
  .empty p { margin: 0 auto; max-width: 430px; color: var(--hm-muted); font-size: 13px; line-height: 1.5; }
  .form-panel { position: sticky; top: calc(var(--header-height, 56px) + 18px); }
  .form-title { padding: 18px 18px 4px; font-size: 18px; font-weight: 700; }
  .form-copy { padding: 0 18px 14px; color: var(--hm-muted); font-size: 12.5px; line-height: 1.45; }
  form { padding: 0 18px 18px; }
  .field { margin-bottom: 13px; }
  .field-row { display: grid; grid-template-columns: 1fr 1.25fr; gap: 10px; }
  .field label, .field-label { display: block; margin-bottom: 6px; color: var(--hm-muted); font-size: 11.5px; font-weight: 650; }
  .field input, .field select { width: 100%; height: 42px; padding: 0 11px; border: 1px solid var(--hm-border); border-radius: 10px; outline: none; color: var(--primary-text-color); background: var(--primary-background-color, #101216); }
  details { border-top: 1px solid var(--hm-border); border-bottom: 1px solid var(--hm-border); margin: 4px 0 14px; padding: 0; }
  summary { padding: 12px 0; cursor: pointer; color: var(--hm-muted); font-size: 12.5px; font-weight: 650; }
  .details-body { padding-bottom: 4px; }
  .label-options { display: flex; flex-wrap: wrap; gap: 7px; max-height: 124px; overflow: auto; padding: 2px 1px 5px; }
  .label-option { display: inline-flex; align-items: center; gap: 5px; border: 1px solid var(--hm-border); border-radius: 8px; padding: 6px 8px; font-size: 11.5px; color: var(--hm-muted); cursor: pointer; }
  .label-option input { width: auto; height: auto; margin: 0; }
  .submit { width: 100%; min-height: 43px; border: 0; border-radius: 11px; background: var(--hm-accent); color: var(--text-primary-color, #fff); cursor: pointer; font-weight: 700; }
  .submit:disabled { opacity: .55; cursor: wait; }
  .loading { min-height: 320px; display: grid; place-items: center; color: var(--hm-muted); }
  .error-box { margin: 36px auto; max-width: 560px; padding: 22px; border-radius: 16px; border: 1px solid color-mix(in srgb, var(--hm-danger) 40%, var(--hm-border)); background: var(--hm-surface); text-align: center; }
  .error-box p { color: var(--hm-muted); }
  .secondary { border: 1px solid var(--hm-border); background: var(--hm-surface-2); border-radius: 9px; padding: 8px 12px; cursor: pointer; }
  .modal-backdrop { position: fixed; inset: 0; z-index: 60; background: rgba(0,0,0,.58); display: grid; place-items: center; padding: 18px; }
  .modal { width: min(580px, 100%); max-height: min(760px, calc(100vh - 36px)); overflow: auto; background: var(--hm-surface); border: 1px solid var(--hm-border); border-radius: 18px; box-shadow: 0 24px 70px rgba(0,0,0,.35); }
  .modal-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 17px 18px; border-bottom: 1px solid var(--hm-border); }
  .modal-title { font-size: 17px; font-weight: 700; }
  .modal-close { border: 0; background: transparent; color: var(--hm-muted); font-size: 22px; cursor: pointer; }
  .modal form { padding-top: 17px; }
  .modal-actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 16px; }
  .modal-actions .submit { width: auto; padding: 0 18px; }
  .toast { position: fixed; z-index: 100; right: 22px; bottom: 22px; max-width: min(380px, calc(100vw - 32px)); padding: 11px 14px; border-radius: 11px; background: #262a31; color: #fff; box-shadow: 0 12px 35px rgba(0,0,0,.28); opacity: 0; transform: translateY(8px); pointer-events: none; transition: .18s ease; font-size: 13px; }
  .toast.show { opacity: 1; transform: translateY(0); }
  .toast.error { background: color-mix(in srgb, var(--hm-danger) 80%, #222); }
  @media (max-width: 980px) {
    .stats { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .layout { grid-template-columns: 1fr; }
    .form-panel { position: static; order: -1; }
  }
  @media (max-width: 640px) {
    .app-header { padding: 0 12px; }
    .header-version { display: none; }
    .page { padding: 20px 12px 32px; }
    .hero { align-items: flex-start; }
    .hero .header-action { display: none; }
    .stats { gap: 8px; }
    .stat { min-height: 80px; padding: 13px; border-radius: 14px; }
    .stat-value { font-size: 25px; }
    .panel { border-radius: 15px; }
    .panel-head { padding: 12px; }
    .task { grid-template-columns: 40px minmax(0, 1fr); padding: 14px 12px; }
    .task-icon { width: 38px; height: 38px; border-radius: 11px; }
    .task-actions { grid-column: 1 / -1; padding-left: 53px; }
    .action { flex: 1; }
    .field-row { grid-template-columns: 1fr; gap: 0; }
    .toast { left: 16px; right: 16px; bottom: 16px; }
  }
`;

function esc(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;"
  })[char]);
}

function localDateInput(date = new Date()) {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

function parseLocalDate(value) {
  if (!value) return null;
  const match = String(value).split("T")[0].match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (!match) return null;
  const date = new Date(Number(match[1]), Number(match[2]) - 1, Number(match[3]));
  if (date.getFullYear() !== Number(match[1]) || date.getMonth() !== Number(match[2]) - 1 || date.getDate() !== Number(match[3])) return null;
  date.setHours(0, 0, 0, 0);
  return date;
}

function dateToIso(value) {
  const date = parseLocalDate(value) || new Date();
  date.setHours(0, 0, 0, 0);
  return date.toISOString();
}

function addMonthsClamped(date, months) {
  const day = date.getDate();
  const target = new Date(date.getFullYear(), date.getMonth() + months, 1);
  const lastDay = new Date(target.getFullYear(), target.getMonth() + 1, 0).getDate();
  target.setDate(Math.min(day, lastDay));
  target.setHours(0, 0, 0, 0);
  return target;
}

function calculateDue(task) {
  const last = parseLocalDate(task.last_performed);
  const value = Number(task.interval_value);
  if (!last || !Number.isFinite(value) || value < 1) return null;
  if (task.interval_type === "days") return new Date(last.getFullYear(), last.getMonth(), last.getDate() + value);
  if (task.interval_type === "weeks") return new Date(last.getFullYear(), last.getMonth(), last.getDate() + value * 7);
  if (task.interval_type === "months") return addMonthsClamped(last, value);
  return null;
}

function dayNumber(date) {
  return Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()) / DAY_MS;
}

class HomeMaintenancePanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._hass = null;
    this._narrow = false;
    this._tasks = [];
    this._config = null;
    this._registry = [];
    this._labels = [];
    this._loading = true;
    this._loadError = false;
    this._search = "";
    this._filter = "all";
    this._editingId = null;
    this._busyId = null;
    this._toastTimer = null;

    this.shadowRoot.addEventListener("click", (event) => this._onClick(event));
    this.shadowRoot.addEventListener("input", (event) => this._onInput(event));
    this.shadowRoot.addEventListener("submit", (event) => this._onSubmit(event));
  }

  set hass(value) {
    const first = !this._hass;
    this._hass = value;
    if (this.isConnected && first) this._loadData();
    this._wireHassElements();
  }
  get hass() { return this._hass; }

  set narrow(value) {
    const changed = this._narrow !== Boolean(value);
    this._narrow = Boolean(value);
    if (changed && this.isConnected) this._render();
  }
  get narrow() { return this._narrow; }

  connectedCallback() {
    this._render();
    if (this._hass) this._loadData();
  }

  _lang() {
    const raw = this._hass?.language || navigator.language || "en";
    const lang = String(raw).toLowerCase().split("-")[0];
    return STRINGS[lang] ? lang : "en";
  }

  _t(key, vars = {}) {
    let text = STRINGS[this._lang()]?.[key] ?? STRINGS.en[key] ?? key;
    for (const [name, value] of Object.entries(vars)) text = text.replaceAll(`{${name}}`, String(value));
    return text;
  }

  _formatDate(date) {
    if (!date) return "—";
    try { return new Intl.DateTimeFormat(this._hass?.locale?.language || this._hass?.language || undefined, { dateStyle: "medium" }).format(date); }
    catch { return localDateInput(date); }
  }

  _status(task) {
    const due = calculateDue(task);
    if (!due) return { kind: "unknown", diff: null, due: null, label: this._t("unknownDue") };
    const today = new Date(); today.setHours(0, 0, 0, 0);
    const diff = dayNumber(due) - dayNumber(today);
    if (diff < 0) return { kind: "overdue", diff, due, label: this._t("overdueBy", { days: Math.abs(diff) }) };
    if (diff === 0) return { kind: "today", diff, due, label: this._t("dueToday") };
    if (diff <= 7) return { kind: "soon", diff, due, label: this._t("dueIn", { days: diff }) };
    return { kind: "later", diff, due, label: this._t("dueDate", { date: this._formatDate(due) }) };
  }

  _taskLabels(task) {
    const entity = this._registry.find((item) => item.unique_id === task.id);
    const ids = Array.isArray(entity?.labels) ? entity.labels : [];
    return ids.map((id) => this._labels.find((label) => label.label_id === id)).filter(Boolean);
  }

  _tagOptions() {
    if (!this._hass?.states) return [];
    return Object.entries(this._hass.states)
      .filter(([entityId]) => entityId.startsWith("tag."))
      .map(([entityId, state]) => ({ id: entityId, name: state.attributes?.friendly_name || entityId.replace("tag.", "") }))
      .sort((a, b) => a.name.localeCompare(b.name));
  }

  async _loadData() {
    if (!this._hass) return;
    this._loading = true;
    this._loadError = false;
    this._render();
    try {
      const [tasks, config, registry, labels] = await Promise.all([
        this._hass.callWS({ type: "home_maintenance/get_tasks" }),
        this._hass.callWS({ type: "home_maintenance/get_config" }),
        this._hass.callWS({ type: "config/entity_registry/list" }),
        this._hass.callWS({ type: "config/label_registry/list" }),
      ]);
      this._tasks = Array.isArray(tasks) ? tasks : [];
      this._config = config || null;
      this._registry = Array.isArray(registry) ? registry : [];
      this._labels = Array.isArray(labels) ? labels : [];
    } catch (error) {
      console.error("Home Maintenance: failed to load panel data", error);
      this._loadError = true;
    } finally {
      this._loading = false;
      this._render();
    }
  }

  _stats() {
    const statuses = this._tasks.map((task) => this._status(task));
    return {
      total: this._tasks.length,
      overdue: statuses.filter((s) => s.kind === "overdue").length,
      soon: statuses.filter((s) => s.kind === "today" || s.kind === "soon").length,
      track: statuses.filter((s) => s.kind === "later").length,
    };
  }

  _filteredTasks() {
    const query = this._search.trim().toLocaleLowerCase();
    return [...this._tasks]
      .filter((task) => {
        if (query && !String(task.title || "").toLocaleLowerCase().includes(query)) return false;
        const status = this._status(task);
        if (this._filter === "overdue" && status.kind !== "overdue") return false;
        if (this._filter === "soon" && !["today", "soon"].includes(status.kind)) return false;
        if (this._filter === "later" && status.kind !== "later") return false;
        return true;
      })
      .sort((a, b) => {
        const ad = calculateDue(a); const bd = calculateDue(b);
        if (!ad && !bd) return String(a.title).localeCompare(String(b.title));
        if (!ad) return 1; if (!bd) return -1;
        return ad.getTime() - bd.getTime();
      });
  }

  _intervalLabel(task) {
    const value = Number(task.interval_value);
    const singularKey = task.interval_type === "days" ? "day" : task.interval_type === "weeks" ? "week" : "month";
    const pluralKey = task.interval_type === "days" ? "days" : task.interval_type === "weeks" ? "weeks" : "months";
    return `${this._t("every")} ${value} ${this._t(value === 1 ? singularKey : pluralKey)}`;
  }

  _labelOptions(selected = []) {
    if (!this._labels.length) return `<span class="field-label">—</span>`;
    const selectedSet = new Set(selected);
    return `<div class="label-options">${this._labels.map((label) => `
      <label class="label-option"><input type="checkbox" name="labels" value="${esc(label.label_id)}" ${selectedSet.has(label.label_id) ? "checked" : ""}>${esc(label.name)}</label>
    `).join("")}</div>`;
  }

  _tagSelect(selected = "") {
    const options = this._tagOptions();
    return `<select name="tag_id"><option value="">${esc(this._t("noTag"))}</option>${options.map((tag) => `<option value="${esc(tag.id)}" ${tag.id === selected ? "selected" : ""}>${esc(tag.name)}</option>`).join("")}</select>`;
  }

  _taskMarkup(task) {
    const status = this._status(task);
    const last = parseLocalDate(task.last_performed);
    const labels = this._taskLabels(task);
    const busy = this._busyId === task.id;
    return `<article class="task">
      <div class="task-icon"><ha-icon icon="${esc(task.icon || "mdi:calendar-check")}"></ha-icon></div>
      <div class="task-main">
        <div class="task-top"><div class="task-title">${esc(task.title)}</div><span class="badge ${esc(status.kind)}">${esc(status.label)}</span></div>
        <div class="task-meta"><span>${esc(this._intervalLabel(task))}</span><span>•</span><span>${esc(last ? this._t("lastDone", { date: this._formatDate(last) }) : this._t("never"))}</span></div>
        ${labels.length ? `<div class="labels">${labels.map((label) => `<span class="label-chip">${esc(label.name)}</span>`).join("")}</div>` : ""}
      </div>
      <div class="task-actions">
        <button class="action primary" type="button" data-action="complete" data-id="${esc(task.id)}" ${busy ? "disabled" : ""}>✓ ${esc(this._t("complete"))}</button>
        <button class="action" type="button" data-action="edit" data-id="${esc(task.id)}" ${busy ? "disabled" : ""}>${esc(this._t("edit"))}</button>
        <button class="action danger" type="button" data-action="delete" data-id="${esc(task.id)}" ${busy ? "disabled" : ""}>${esc(this._t("delete"))}</button>
      </div>
    </article>`;
  }

  _tasksMarkup() {
    const tasks = this._filteredTasks();
    if (!this._tasks.length) return `<div class="empty"><div class="empty-icon">⌂</div><h3>${esc(this._t("noTasks"))}</h3><p>${esc(this._t("noTasksHint"))}</p></div>`;
    if (!tasks.length) return `<div class="empty"><div class="empty-icon">⌕</div><h3>${esc(this._t("noMatch"))}</h3><p>${esc(this._t("noMatchHint"))}</p></div>`;
    return `<div class="task-list">${tasks.map((task) => this._taskMarkup(task)).join("")}</div>`;
  }

  _addFormMarkup() {
    return `<aside class="panel form-panel" id="new-task-card">
      <div class="form-title">${esc(this._t("newTask"))}</div>
      <div class="form-copy">${esc(this._t("subtitle"))}</div>
      <form id="add-form">
        <div class="field"><label for="add-title">${esc(this._t("taskTitle"))}</label><input id="add-title" name="title" required maxlength="120" autocomplete="off"></div>
        <div class="field-row">
          <div class="field"><label for="add-interval">${esc(this._t("interval"))}</label><input id="add-interval" name="interval_value" type="number" min="1" step="1" value="1" required></div>
          <div class="field"><label for="add-type">${esc(this._t("every"))}</label><select id="add-type" name="interval_type"><option value="days">${esc(this._t("days"))}</option><option value="weeks">${esc(this._t("weeks"))}</option><option value="months">${esc(this._t("months"))}</option></select></div>
        </div>
        <details><summary>${esc(this._t("optional"))}</summary><div class="details-body">
          <div class="field"><label>${esc(this._t("lastPerformed"))}</label><input name="last_performed" type="date" value="${localDateInput()}"></div>
          <div class="field"><label>${esc(this._t("icon"))}</label><input name="icon" value="mdi:calendar-check" placeholder="mdi:hammer-wrench"></div>
          <div class="field"><label>${esc(this._t("tag"))}</label>${this._tagSelect()}</div>
          <div class="field"><span class="field-label">${esc(this._t("labels"))}</span>${this._labelOptions()}</div>
        </div></details>
        <button class="submit" type="submit">${esc(this._t("addTask"))}</button>
      </form>
    </aside>`;
  }

  _editMarkup() {
    if (!this._editingId) return "";
    const task = this._tasks.find((item) => item.id === this._editingId);
    if (!task) return "";
    const labels = this._taskLabels(task).map((label) => label.label_id);
    return `<div class="modal-backdrop" data-action="close-edit-backdrop">
      <section class="modal" role="dialog" aria-modal="true" aria-label="${esc(this._t("editTask"))}" data-modal>
        <div class="modal-head"><div class="modal-title">${esc(this._t("editTask"))}</div><button class="modal-close" type="button" aria-label="${esc(this._t("cancel"))}" data-action="close-edit">×</button></div>
        <form id="edit-form" data-id="${esc(task.id)}">
          <div class="field"><label>${esc(this._t("taskTitle"))}</label><input name="title" required maxlength="120" value="${esc(task.title)}"></div>
          <div class="field-row">
            <div class="field"><label>${esc(this._t("interval"))}</label><input name="interval_value" type="number" min="1" step="1" required value="${esc(task.interval_value)}"></div>
            <div class="field"><label>${esc(this._t("every"))}</label><select name="interval_type"><option value="days" ${task.interval_type === "days" ? "selected" : ""}>${esc(this._t("days"))}</option><option value="weeks" ${task.interval_type === "weeks" ? "selected" : ""}>${esc(this._t("weeks"))}</option><option value="months" ${task.interval_type === "months" ? "selected" : ""}>${esc(this._t("months"))}</option></select></div>
          </div>
          <div class="field"><label>${esc(this._t("lastPerformed"))}</label><input name="last_performed" type="date" value="${esc(String(task.last_performed || "").split("T")[0])}"></div>
          <div class="field"><label>${esc(this._t("icon"))}</label><input name="icon" value="${esc(task.icon || "mdi:calendar-check")}"></div>
          <div class="field"><label>${esc(this._t("tag"))}</label>${this._tagSelect(task.tag_id || "")}</div>
          <div class="field"><span class="field-label">${esc(this._t("labels"))}</span>${this._labelOptions(labels)}</div>
          <div class="modal-actions"><button class="secondary" type="button" data-action="close-edit">${esc(this._t("cancel"))}</button><button class="submit" type="submit">${esc(this._t("save"))}</button></div>
        </form>
      </section>
    </div>`;
  }

  _render() {
    if (!this.shadowRoot) return;
    const title = this._config?.options?.sidebar_title || this._config?.data?.sidebar_title || "Home Maintenance";
    if (this._loading) {
      this.shadowRoot.innerHTML = `<style>${CSS}</style><header class="app-header"><ha-menu-button></ha-menu-button><div class="title-block"><div class="title">${esc(title)}</div></div></header><div class="loading">${esc(this._t("loading"))}</div><div class="toast" role="status"></div>`;
      this._wireHassElements(); return;
    }
    if (this._loadError) {
      this.shadowRoot.innerHTML = `<style>${CSS}</style><header class="app-header"><ha-menu-button></ha-menu-button><div class="title-block"><div class="title">${esc(title)}</div></div></header><div class="error-box"><h2>${esc(this._t("loadError"))}</h2><p>${esc(this._t("actionError"))}</p><button class="secondary" data-action="retry">${esc(this._t("retry"))}</button></div><div class="toast" role="status"></div>`;
      this._wireHassElements(); return;
    }
    const stats = this._stats();
    this.shadowRoot.innerHTML = `<style>${CSS}</style>
      <header class="app-header"><ha-menu-button></ha-menu-button><div class="title-block"><div class="title">${esc(title)}</div></div><div class="header-version">v${VERSION}</div><button class="header-action" type="button" data-action="scroll-new">+ ${esc(this._t("newTask"))}</button></header>
      <main class="page">
        <section class="hero"><div><h1>${esc(title)}</h1><p>${esc(this._t("subtitle"))}</p></div></section>
        <section class="stats">
          <div class="stat"><span class="stat-label">${esc(this._t("total"))}</span><span class="stat-value">${stats.total}</span></div>
          <div class="stat overdue"><span class="stat-label">${esc(this._t("overdue"))}</span><span class="stat-value">${stats.overdue}</span></div>
          <div class="stat"><span class="stat-label">${esc(this._t("dueSoon"))}</span><span class="stat-value">${stats.soon}</span></div>
          <div class="stat"><span class="stat-label">${esc(this._t("onTrack"))}</span><span class="stat-value">${stats.track}</span></div>
        </section>
        <section class="layout">
          <section class="panel">
            <div class="panel-head"><div class="search-wrap"><input class="search" id="task-search" value="${esc(this._search)}" placeholder="${esc(this._t("search"))}" aria-label="${esc(this._t("search"))}"></div>
              <div class="filters"><button class="filter ${this._filter === "all" ? "active" : ""}" data-filter="all">${esc(this._t("all"))}</button><button class="filter ${this._filter === "overdue" ? "active" : ""}" data-filter="overdue">${esc(this._t("overdue"))}</button><button class="filter ${this._filter === "soon" ? "active" : ""}" data-filter="soon">${esc(this._t("dueSoon"))}</button><button class="filter ${this._filter === "later" ? "active" : ""}" data-filter="later">${esc(this._t("later"))}</button></div>
            </div>
            <div class="list-meta" id="result-count">${esc(this._t("results", { count: this._filteredTasks().length }))}</div>
            <div id="task-list-host">${this._tasksMarkup()}</div>
          </section>
          ${this._addFormMarkup()}
        </section>
      </main>
      ${this._editMarkup()}
      <div class="toast" role="status" aria-live="polite"></div>`;
    this._wireHassElements();
  }

  _wireHassElements() {
    const menu = this.shadowRoot?.querySelector("ha-menu-button");
    if (menu && this._hass) { menu.hass = this._hass; menu.narrow = this._narrow; }
  }

  _renderTasksOnly() {
    const host = this.shadowRoot?.querySelector("#task-list-host");
    const count = this.shadowRoot?.querySelector("#result-count");
    if (host) host.innerHTML = this._tasksMarkup();
    if (count) count.textContent = this._t("results", { count: this._filteredTasks().length });
    this.shadowRoot?.querySelectorAll("[data-filter]").forEach((button) => button.classList.toggle("active", button.dataset.filter === this._filter));
  }

  _onInput(event) {
    const target = event.target;
    if (target?.id === "task-search") {
      this._search = target.value || "";
      this._renderTasksOnly();
    }
  }

  async _onClick(event) {
    const button = event.target?.closest?.("[data-action], [data-filter]");
    if (!button) return;
    if (button.dataset.filter) { this._filter = button.dataset.filter; this._renderTasksOnly(); return; }
    const action = button.dataset.action;
    if (action === "scroll-new") { this.shadowRoot.querySelector("#new-task-card")?.scrollIntoView({ behavior: "smooth", block: "start" }); this.shadowRoot.querySelector("#add-title")?.focus(); return; }
    if (action === "retry") { this._loadData(); return; }
    if (action === "close-edit") { this._editingId = null; this._render(); return; }
    if (action === "close-edit-backdrop" && event.target === button) { this._editingId = null; this._render(); return; }
    const id = button.dataset.id;
    if (!id || this._busyId) return;
    if (action === "edit") { this._editingId = id; this._render(); return; }
    if (action === "complete") await this._completeTask(id);
    if (action === "delete") await this._deleteTask(id);
  }

  async _onSubmit(event) {
    const form = event.target;
    if (!(form instanceof HTMLFormElement)) return;
    event.preventDefault();
    if (!form.reportValidity()) return;
    if (form.id === "add-form") await this._addTask(form);
    if (form.id === "edit-form") await this._saveEdit(form);
  }

  _payloadFromForm(form) {
    const data = new FormData(form);
    const title = String(data.get("title") || "").trim();
    const intervalValue = Number(data.get("interval_value"));
    const intervalType = String(data.get("interval_type") || "days");
    if (!title || !Number.isInteger(intervalValue) || intervalValue < 1 || !["days", "weeks", "months"].includes(intervalType)) return null;
    return {
      title,
      interval_value: intervalValue,
      interval_type: intervalType,
      last_performed: dateToIso(String(data.get("last_performed") || localDateInput())),
      icon: String(data.get("icon") || "mdi:calendar-check").trim() || "mdi:calendar-check",
      tag_id: String(data.get("tag_id") || "").trim() || null,
      labels: data.getAll("labels").map((value) => String(value)),
    };
  }

  async _addTask(form) {
    const payload = this._payloadFromForm(form);
    if (!payload) { this._showToast(this._t("required"), true); return; }
    const submit = form.querySelector("button[type=submit]"); if (submit) submit.disabled = true;
    try {
      const addPayload = { ...payload }; if (!addPayload.tag_id) delete addPayload.tag_id;
      await this._hass.callWS({ type: "home_maintenance/add_task", ...addPayload });
      await this._loadData();
      this._showToast(this._t("added"));
    } catch (error) {
      console.error("Home Maintenance: failed to add task", error); this._showToast(this._t("actionError"), true); if (submit) submit.disabled = false;
    }
  }

  async _saveEdit(form) {
    const payload = this._payloadFromForm(form);
    const id = form.dataset.id;
    if (!payload || !id) { this._showToast(this._t("required"), true); return; }
    const submit = form.querySelector("button[type=submit]"); if (submit) submit.disabled = true;
    try {
      await this._hass.callWS({ type: "home_maintenance/update_task", task_id: id, updates: payload });
      this._editingId = null;
      await this._loadData();
      this._showToast(this._t("updated"));
    } catch (error) {
      console.error("Home Maintenance: failed to update task", error); this._showToast(this._t("actionError"), true); if (submit) submit.disabled = false;
    }
  }

  async _completeTask(id) {
    this._busyId = id; this._renderTasksOnly();
    try {
      await this._hass.callWS({ type: "home_maintenance/complete_task", task_id: id });
      await this._loadData();
      this._showToast(this._t("completed"));
    } catch (error) {
      console.error("Home Maintenance: failed to complete task", error); this._busyId = null; this._renderTasksOnly(); this._showToast(this._t("actionError"), true);
    } finally { this._busyId = null; }
  }

  async _deleteTask(id) {
    const task = this._tasks.find((item) => item.id === id);
    if (!task || !window.confirm(this._t("confirmDelete", { title: task.title }))) return;
    this._busyId = id; this._renderTasksOnly();
    try {
      await this._hass.callWS({ type: "home_maintenance/remove_task", task_id: id });
      await this._loadData();
      this._showToast(this._t("removed"));
    } catch (error) {
      console.error("Home Maintenance: failed to delete task", error); this._busyId = null; this._renderTasksOnly(); this._showToast(this._t("actionError"), true);
    } finally { this._busyId = null; }
  }

  _showToast(message, isError = false) {
    const toast = this.shadowRoot?.querySelector(".toast");
    if (!toast) return;
    toast.textContent = message;
    toast.classList.toggle("error", isError);
    toast.classList.add("show");
    if (this._toastTimer) window.clearTimeout(this._toastTimer);
    this._toastTimer = window.setTimeout(() => toast.classList.remove("show"), 2600);
  }
}

if (!customElements.get("home-maintenance-panel")) {
  customElements.define("home-maintenance-panel", HomeMaintenancePanel);
}
