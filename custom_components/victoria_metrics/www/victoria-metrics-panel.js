const STYLES = `
  :host {
    display: block;
    padding: 16px 24px;
    background: var(--primary-background-color);
    color: var(--primary-text-color);
    font-family: var(--paper-font-body1_-_font-family, Roboto, sans-serif);
    min-height: 100vh;
    box-sizing: border-box;
  }
  .header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 24px;
    gap: 8px;
  }
  .header > div {
    display: flex;
    gap: 8px;
  }
  h1 {
    font-size: 24px;
    font-weight: 400;
    color: var(--primary-text-color);
    margin: 0;
  }
  .card {
    background: var(--ha-card-background, var(--card-background-color));
    border-radius: var(--ha-card-border-radius, 12px);
    box-shadow: var(--ha-card-box-shadow, 0 2px 2px rgba(0, 0, 0, 0.1));
    padding: 0;
    overflow-x: auto;
  }
  .add-section {
    background: var(--ha-card-background, var(--card-background-color));
    border-radius: var(--ha-card-border-radius, 12px);
    box-shadow: var(--ha-card-box-shadow, 0 2px 2px rgba(0, 0, 0, 0.1));
    padding: 16px;
    margin-bottom: 16px;
    position: relative;
  }
  .add-section label {
    display: block;
    font-size: 12px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--secondary-text-color);
    margin-bottom: 8px;
  }
  .search-wrapper {
    position: relative;
  }
  .search-input {
    width: 100%;
    padding: 10px 12px;
    border: 1px solid var(--divider-color);
    border-radius: 8px;
    background: var(--primary-background-color);
    color: var(--primary-text-color);
    font-size: 14px;
    box-sizing: border-box;
    outline: none;
  }
  .search-input:focus {
    border-color: var(--primary-color);
  }
  .search-input::placeholder {
    color: var(--secondary-text-color);
  }
  .dropdown {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: var(--ha-card-background, var(--card-background-color));
    border: 1px solid var(--divider-color);
    border-radius: 8px;
    margin-top: 4px;
    max-height: 480px;
    overflow-y: auto;
    z-index: 10;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    display: none;
  }
  .dropdown.open {
    display: block;
  }
  .dropdown-item {
    padding: 10px 12px;
    cursor: pointer;
    font-size: 14px;
    display: flex;
    flex-direction: column;
    gap: 2px;
    border-bottom: 1px solid var(--divider-color);
  }
  .dropdown-item:last-child {
    border-bottom: none;
  }
  .dropdown-item:hover {
    background: var(--table-row-alternative-background-color,
                    rgba(var(--rgb-primary-text-color, 0, 0, 0), 0.04));
  }
  .dropdown-item-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 8px;
  }
  .dropdown-item .entity-name {
    color: var(--primary-text-color);
  }
  .dropdown-item .entity-value {
    font-size: 12px;
    color: var(--secondary-text-color);
    white-space: nowrap;
    flex-shrink: 0;
  }
  .dropdown-item .entity-detail {
    font-size: 12px;
    color: var(--secondary-text-color);
    font-family: var(--code-font-family, monospace);
  }
  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
  }
  th {
    text-align: left;
    padding: 14px 16px;
    border-bottom: 2px solid var(--divider-color);
    color: var(--secondary-text-color);
    font-weight: 500;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    white-space: nowrap;
  }
  td {
    padding: 12px 16px;
    border-bottom: 1px solid var(--divider-color);
    color: var(--primary-text-color);
    vertical-align: middle;
  }
  tr:last-child td {
    border-bottom: none;
  }
  tbody tr:hover {
    background: var(--table-row-alternative-background-color,
                    rgba(var(--rgb-primary-text-color, 0, 0, 0), 0.04));
  }
  .entity-id {
    font-family: var(--code-font-family, monospace);
    font-size: 13px;
  }
  .entity-link {
    color: var(--primary-text-color);
    cursor: pointer;
    text-decoration: none;
  }
  .entity-link:hover {
    color: var(--primary-color);
    text-decoration: underline;
  }
  .metric-name {
    font-family: var(--code-font-family, monospace);
    font-size: 13px;
    color: var(--primary-color);
  }
  .metric-name-wrapper {
    display: flex;
    align-items: center;
    gap: 4px;
  }
  .metric-name-text {
    font-family: var(--code-font-family, monospace);
    font-size: 13px;
    color: var(--primary-color);
  }
  .metric-name-text.is-override {
    color: var(--accent-color, #ff9800);
  }
  .metric-name-edit-btn {
    background: none;
    border: none;
    cursor: pointer;
    padding: 2px;
    opacity: 0.4;
    color: var(--primary-text-color);
    line-height: 1;
    flex-shrink: 0;
  }
  .metric-name-edit-btn:hover {
    opacity: 0.8;
  }
  .metric-name-edit-btn svg {
    width: 14px;
    height: 14px;
    fill: currentColor;
  }
  .metric-name-input {
    width: 100%;
    padding: 4px 6px;
    border: 1px solid var(--primary-color);
    border-radius: 4px;
    background: var(--primary-background-color);
    color: var(--primary-text-color);
    font-size: 13px;
    font-family: var(--code-font-family, monospace);
    outline: none;
  }
  .interval-wrapper {
    display: flex;
    align-items: center;
    gap: 4px;
  }
  .batch-interval-input {
    width: 64px;
    padding: 4px 6px;
    border: 1px solid var(--divider-color);
    border-radius: 4px;
    background: var(--primary-background-color);
    color: var(--primary-text-color);
    font-size: 12px;
    font-family: var(--code-font-family, monospace);
    text-align: right;
  }
  .batch-interval-input:focus {
    border-color: var(--primary-color);
    outline: none;
  }
  .batch-interval-suffix {
    font-size: 12px;
    color: var(--secondary-text-color);
  }
  .remove-btn {
    background: none;
    border: none;
    color: var(--error-color, #db4437);
    cursor: pointer;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 13px;
    opacity: 0.7;
  }
  .remove-btn:hover {
    opacity: 1;
    background: rgba(var(--rgb-error-color, 219, 68, 55), 0.1);
  }
  .empty-state {
    text-align: center;
    padding: 48px 16px;
    color: var(--secondary-text-color);
  }
  .empty-state p {
    margin: 8px 0;
    line-height: 1.6;
  }
  .count {
    font-size: 14px;
    color: var(--secondary-text-color);
    margin-bottom: 12px;
  }
  .settings-btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: none;
    border: 1px solid var(--divider-color);
    color: var(--primary-text-color);
    cursor: pointer;
    padding: 6px 12px;
    border-radius: 8px;
    font-size: 13px;
    font-family: inherit;
    transition: background 0.15s;
  }
  .settings-btn:hover {
    background: var(--table-row-alternative-background-color,
                    rgba(var(--rgb-primary-text-color, 0, 0, 0), 0.04));
  }
  .settings-btn svg {
    width: 16px;
    height: 16px;
    fill: currentColor;
  }
  .saving {
    opacity: 0.6;
    pointer-events: none;
  }
  .config-overlay {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    z-index: 100;
    align-items: center;
    justify-content: center;
  }
  .config-overlay.open {
    display: flex;
  }
  .config-dialog {
    background: var(--ha-card-background, var(--card-background-color));
    border-radius: var(--ha-card-border-radius, 12px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
    padding: 24px;
    max-width: 640px;
    width: 90%;
    max-height: 80vh;
    overflow-y: auto;
    color: var(--primary-text-color);
  }
  .config-dialog h2 {
    margin: 0 0 16px;
    font-size: 18px;
    font-weight: 500;
  }
  .config-dialog .config-section {
    margin-bottom: 16px;
  }
  .config-dialog .config-label {
    font-size: 12px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--secondary-text-color);
    margin-bottom: 4px;
  }
  .config-dialog .config-value {
    font-size: 14px;
    padding: 8px 12px;
    background: var(--primary-background-color);
    border-radius: 6px;
    font-family: monospace;
    word-break: break-all;
  }
  .config-dialog .close-btn {
    display: block;
    margin: 16px 0 0 auto;
    background: none;
    border: 1px solid var(--divider-color);
    color: var(--primary-text-color);
    cursor: pointer;
    padding: 6px 16px;
    border-radius: 8px;
    font-size: 13px;
    font-family: inherit;
  }
  .config-dialog .close-btn:hover {
    background: var(--table-row-alternative-background-color,
                    rgba(var(--rgb-primary-text-color, 0, 0, 0), 0.04));
  }
  .audit-section {
    margin-top: 24px;
  }
  .audit-header {
    font-size: 16px;
    font-weight: 500;
    color: var(--primary-text-color);
    margin: 0 0 12px;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .audit-count {
    font-size: 12px;
    color: var(--secondary-text-color);
    font-weight: 400;
  }
  .audit-card {
    background: var(--ha-card-background, var(--card-background-color));
    border-radius: var(--ha-card-border-radius, 12px);
    box-shadow: var(--ha-card-box-shadow, 0 2px 2px rgba(0, 0, 0, 0.1));
    max-height: 400px;
    overflow-y: auto;
    padding: 0;
  }
  .audit-entry {
    display: flex;
    align-items: baseline;
    gap: 12px;
    padding: 8px 16px;
    border-bottom: 1px solid var(--divider-color);
    font-size: 13px;
  }
  .audit-entry:last-child {
    border-bottom: none;
  }
  .audit-time {
    font-size: 11px;
    color: var(--secondary-text-color);
    white-space: nowrap;
    flex-shrink: 0;
    min-width: 64px;
  }
  .audit-metric {
    font-family: var(--code-font-family, monospace);
    color: var(--primary-color);
    flex-shrink: 0;
  }
  .audit-arrow {
    color: var(--secondary-text-color);
    flex-shrink: 0;
  }
  .audit-value {
    font-family: var(--code-font-family, monospace);
    color: var(--primary-text-color);
  }
  .audit-mode {
    font-size: 11px;
    color: var(--secondary-text-color);
    margin-left: auto;
    flex-shrink: 0;
  }
  .audit-empty {
    text-align: center;
    padding: 24px 16px;
    color: var(--secondary-text-color);
    font-size: 13px;
  }
`;

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

class VictoriaMetricsPanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._hass = null;
    this._narrow = false;
    this._route = null;
    this._panel = null;
    this._lastDataJson = "";
    this._initialized = false;
    this._config = null;
    this._configEntities = [];
    this._saving = false;
    this._searchQuery = "";
    this._configLoadPending = false;
    this._auditEntries = [];
    this._auditTimer = null;
  }

  set hass(hass) {
    this._hass = hass;
    this._scheduleConfigLoad();
    this._updateIfChanged();
  }

  set panel(panel) {
    this._panel = panel;
  }

  set narrow(narrow) {
    this._narrow = narrow;
  }

  set route(route) {
    this._route = route;
  }

  connectedCallback() {
    if (!this._initialized) {
      this._initLayout();
      this._initialized = true;
    }
    this._updateIfChanged();
    this._loadAuditLog();
    this._auditTimer = setInterval(() => { this._loadAuditLog(); }, 10000);
  }

  disconnectedCallback() {
    if (this._auditTimer) {
      clearInterval(this._auditTimer);
      this._auditTimer = null;
    }
  }

  _initLayout() {
    const style = document.createElement("style");
    style.textContent = STYLES;
    this.shadowRoot.appendChild(style);

    const header = document.createElement("div");
    header.className = "header";
    header.innerHTML =
      "<h1>Victoria Metrics Exports</h1>" +
      "<div>" +
      '<button class="settings-btn view-config-btn">' +
        '<svg viewBox="0 0 24 24"><path d="M17,7H22V17H17V19A1,1 0 0,0 18,20H20V22H17.5C16.95,22 16,21.55 16,21C16,21.55 15.05,22 14.5,22H12V20H14A1,1 0 0,0 15,19V5A1,1 0 0,0 14,4H12V2H14.5C15.05,2 16,2.45 16,3C16,2.45 16.95,2 17.5,2H20V4H18A1,1 0 0,0 17,5V7M19,9H17V15H19V9M3,7H13V9H5V19H13V17H3V7M5,11H13V13H5V11Z"/></svg>' +
        "View Config" +
      "</button>" +
      "</div>";
    this.shadowRoot.appendChild(header);

    header.querySelector(".view-config-btn").addEventListener("click", () => {
      this._showConfigOverlay();
    });

    // Config overlay
    this._configOverlay = document.createElement("div");
    this._configOverlay.className = "config-overlay";
    this._configOverlay.addEventListener("click", (e) => {
      if (e.target === this._configOverlay) this._configOverlay.classList.remove("open");
    });
    this.shadowRoot.appendChild(this._configOverlay);

    // Entity search/add section
    this._addSection = document.createElement("div");
    this._addSection.className = "add-section";
    this._addSection.innerHTML =
      "<label>Add Entity to Export</label>" +
      '<div class="search-wrapper">' +
        '<input type="text" class="search-input" placeholder="Search entities to add...">' +
        '<div class="dropdown"></div>' +
      "</div>";
    this.shadowRoot.appendChild(this._addSection);

    this._searchInput = this._addSection.querySelector(".search-input");
    this._dropdown = this._addSection.querySelector(".dropdown");

    this._searchInput.addEventListener("input", () => {
      this._searchQuery = this._searchInput.value;
      this._updateDropdown();
    });
    this._searchInput.addEventListener("focus", () => {
      if (this._searchQuery.length >= 3) {
        this._updateDropdown();
      }
    });
    // Close dropdown on outside click
    this.shadowRoot.addEventListener("click", (e) => {
      if (!this._addSection.contains(e.target)) {
        this._closeDropdown();
      }
    });

    this._countEl = document.createElement("div");
    this._countEl.className = "count";
    this.shadowRoot.appendChild(this._countEl);

    this._cardEl = document.createElement("div");
    this._cardEl.className = "card";
    this.shadowRoot.appendChild(this._cardEl);

    // Audit log section
    this._auditSection = document.createElement("div");
    this._auditSection.className = "audit-section";
    this._auditSection.innerHTML =
      '<div class="audit-header">Export Log <span class="audit-count"></span></div>';
    this._auditCard = document.createElement("div");
    this._auditCard.className = "audit-card";
    this._auditSection.appendChild(this._auditCard);
    this.shadowRoot.appendChild(this._auditSection);
  }

  _scheduleConfigLoad() {
    if (this._configLoadPending) return;
    this._configLoadPending = true;
    var self = this;
    Promise.resolve().then(function () {
      self._configLoadPending = false;
      self._loadConfig();
    });
  }

  async _loadConfig() {
    if (!this._hass) return;
    try {
      var result = await this._hass.connection.sendMessagePromise({
        type: "victoria_metrics/get_config",
      });
      var newEntities = result.entities.map(function (e) { return e.entity_id; });
      var changed = JSON.stringify(newEntities) !== JSON.stringify(this._configEntities);
      this._config = result;
      this._configEntities = newEntities;
      if (changed) {
        this._updateIfChanged();
      }
    } catch (_err) {
      // Config entry may not exist yet
    }
  }

  _getExportData() {
    if (!this._hass || !this._config) return [];

    const states = this._hass.states;
    const rows = [];

    for (const item of this._config.entities) {
      const entityId = item.entity_id;
      const metricName = item.metric_name;
      const batchInterval = item.batch_interval || this._config.batch_interval || 300;
      const sourceState = states[entityId];
      const friendlyName = sourceState
        ? sourceState.attributes.friendly_name || entityId
        : entityId;

      rows.push({
        sourceEntity: entityId,
        friendlyName: friendlyName,
        metricName: metricName,
        metricNameOverride: item.metric_name_override || "",
        batchInterval: batchInterval,
      });
    }

    rows.sort(function (a, b) { return a.friendlyName.localeCompare(b.friendlyName); });
    return rows;
  }

  _updateIfChanged() {
    if (!this._initialized || !this._hass) return;

    const rows = this._getExportData();
    const dataJson = JSON.stringify(rows);

    if (dataJson === this._lastDataJson) return;
    this._lastDataJson = dataJson;

    this._renderData(rows);
  }

  _renderData(rows) {
    if (rows.length === 0) {
      this._countEl.textContent = "";
      this._cardEl.innerHTML =
        '<div class="empty-state">' +
          "<p>No entities are configured for export.</p>" +
          "<p>Use the search box above to add entities.</p>" +
        "</div>";
      return;
    }

    this._countEl.textContent =
      rows.length + " entit" + (rows.length === 1 ? "y" : "ies") + " exported";

    const metricPrefix = this._config ? (this._config.metric_prefix || "") : "";
    let tableRows = "";
    for (const r of rows) {
      const objId = r.sourceEntity.split(".", 2).pop();
      const autoMetricName = metricPrefix ? metricPrefix + "_" + objId : objId;
      const intervalCell =
        '<div class="interval-wrapper">' +
          '<input type="number" class="batch-interval-input"' +
            ' value="' + r.batchInterval + '"' +
            ' min="10" max="3600" step="10"' +
            ' data-entity="' + escapeHtml(r.sourceEntity) + '">' +
          '<span class="batch-interval-suffix">s</span>' +
        '</div>';

      const displayName = this._formatDisplayName(r.sourceEntity);
      tableRows +=
        "<tr>" +
        '<td class="entity-id">' + escapeHtml(r.sourceEntity) + "</td>" +
        "<td>" +
          '<a class="entity-link" data-entity="' + escapeHtml(r.sourceEntity) + '" href="#">' +
            escapeHtml(displayName) +
          "</a>" +
        "</td>" +
        '<td class="metric-name">' +
          '<div class="metric-name-wrapper">' +
            '<span class="metric-name-text' + (r.metricNameOverride ? ' is-override' : '') + '">' +
              escapeHtml(r.metricName) +
            '</span>' +
            '<button class="metric-name-edit-btn"' +
              ' data-entity="' + escapeHtml(r.sourceEntity) + '"' +
              ' data-current-override="' + escapeHtml(r.metricNameOverride) + '"' +
              ' data-auto-name="' + escapeHtml(autoMetricName) + '"' +
              ' title="' + (r.metricNameOverride ? 'Edit custom metric name' : 'Set custom metric name') + '">' +
              '<svg viewBox="0 0 24 24"><path d="M20.71,7.04C21.1,6.65 21.1,6 20.71,5.63L18.37,3.29C18,2.9 17.35,2.9 16.96,3.29L15.12,5.12L18.87,8.87M3,17.25V21H6.75L17.81,9.93L14.06,6.18L3,17.25Z"/></svg>' +
            '</button>' +
          '</div>' +
        "</td>" +
        "<td>" + intervalCell + "</td>" +
        "<td>" +
          '<button class="remove-btn" data-entity="' + escapeHtml(r.sourceEntity) + '">' +
            "Remove" +
          "</button>" +
        "</td>" +
        "</tr>";
    }

    this._cardEl.innerHTML =
      "<table>" +
        "<thead><tr>" +
          "<th>Entity</th>" +
          "<th>Friendly Name</th>" +
          "<th>Metric Name</th>" +
          "<th>Min Interval</th>" +
          "<th></th>" +
        "</tr></thead>" +
        "<tbody>" + tableRows + "</tbody>" +
      "</table>";

    // Attach event handlers
    const self = this;

    // Remove button handlers
    this._cardEl.querySelectorAll(".remove-btn").forEach(function (btn) {
      btn.addEventListener("click", function () {
        const entityId = btn.getAttribute("data-entity");
        self._removeEntity(entityId);
      });
    });

    // Batch interval handlers
    this._cardEl.querySelectorAll(".batch-interval-input").forEach(function (input) {
      var timer = null;
      input.addEventListener("change", function () {
        const entityId = input.getAttribute("data-entity");
        const val = parseInt(input.value, 10);
        if (val >= 10 && val <= 3600) {
          clearTimeout(timer);
          timer = setTimeout(function () {
            self._updateEntitySetting(entityId, { batch_interval: val });
          }, 500);
        }
      });
    });

    // Metric name edit button handlers
    this._cardEl.querySelectorAll(".metric-name-edit-btn").forEach(function (btn) {
      btn.addEventListener("click", function () {
        const entityId = btn.getAttribute("data-entity");
        const currentOverride = btn.getAttribute("data-current-override");
        const autoName = btn.getAttribute("data-auto-name");
        const wrapper = btn.closest(".metric-name-wrapper");
        self._startMetricNameEdit(wrapper, entityId, currentOverride, autoName);
      });
    });

    // Friendly name click handlers for more-info dialog
    this._cardEl.querySelectorAll(".entity-link").forEach(function (link) {
      link.addEventListener("click", function (e) {
        e.preventDefault();
        const entityId = link.getAttribute("data-entity");
        self._openMoreInfo(entityId);
      });
    });
  }

  _openMoreInfo(entityId) {
    const event = new CustomEvent("hass-more-info", {
      bubbles: true,
      composed: true,
      detail: { entityId: entityId },
    });
    this.dispatchEvent(event);
  }

  _showConfigOverlay() {
    if (!this._config) return;

    const c = this._config;
    const entityCount = c.entities ? c.entities.length : 0;

    let entitiesHtml = "";
    if (c.entities && c.entities.length > 0) {
      const sorted = c.entities.slice().sort(function (a, b) {
        return a.entity_id.localeCompare(b.entity_id);
      });
      entitiesHtml = '<table style="width:100%;font-size:13px;border-collapse:collapse;">' +
        "<thead><tr>" +
          '<th style="text-align:left;padding:4px 8px;border-bottom:1px solid var(--divider-color);">Entity</th>' +
          '<th style="text-align:left;padding:4px 8px;border-bottom:1px solid var(--divider-color);">Metric</th>' +
          '<th style="text-align:right;padding:4px 8px;border-bottom:1px solid var(--divider-color);">Min Interval</th>' +
        "</tr></thead><tbody>";
      for (const e of sorted) {
        entitiesHtml +=
          "<tr>" +
          '<td style="padding:4px 8px;font-family:monospace;font-size:12px;">' + escapeHtml(e.entity_id) + "</td>" +
          '<td style="padding:4px 8px;font-family:monospace;font-size:12px;">' + escapeHtml(e.metric_name) + "</td>" +
          '<td style="padding:4px 8px;text-align:right;">' + e.batch_interval + "s</td>" +
          "</tr>";
      }
      entitiesHtml += "</tbody></table>";
    } else {
      entitiesHtml = '<span style="color:var(--secondary-text-color);">No entities configured</span>';
    }

    this._configOverlay.innerHTML =
      '<div class="config-dialog">' +
        "<h2>Export Configuration</h2>" +
        '<div class="config-section">' +
          '<div class="config-label">Metric Prefix</div>' +
          '<div class="config-value">' + escapeHtml(c.metric_prefix || "(none)") + "</div>" +
        "</div>" +
        '<div class="config-section">' +
          '<div class="config-label">Default Batch Interval</div>' +
          '<div class="config-value">' + c.batch_interval + " seconds</div>" +
        "</div>" +
        '<div class="config-section">' +
          '<div class="config-label">Entities (' + entityCount + " total)</div>" +
          '<div class="config-value" style="padding:4px;overflow-x:auto;">' + entitiesHtml + "</div>" +
        "</div>" +
        '<button class="close-btn">Close</button>' +
      "</div>";

    this._configOverlay.classList.add("open");
    this._configOverlay.querySelector(".close-btn").addEventListener("click", () => {
      this._configOverlay.classList.remove("open");
    });
  }

  async _updateEntitySetting(entityId, settings) {
    if (!this._hass) return;
    try {
      const msg = {
        type: "victoria_metrics/update_entity_settings",
        entity_id: entityId,
      };
      if ("batch_interval" in settings) msg.batch_interval = settings.batch_interval;
      if ("metric_name" in settings) msg.metric_name = settings.metric_name;

      await this._hass.connection.sendMessagePromise(msg);

      // Refresh config to get updated state
      await this._loadConfig();
      // Force re-render after settings change
      this._lastDataJson = "";
      this._updateIfChanged();
    } catch (_err) {
      // Revert UI on error by reloading config
      this._lastDataJson = "";
      await this._loadConfig();
      this._updateIfChanged();
    }
  }

  _startMetricNameEdit(wrapper, entityId, currentOverride, autoName) {
    const input = document.createElement("input");
    input.type = "text";
    input.className = "metric-name-input";
    input.value = currentOverride || autoName || entityId;
    input.placeholder = autoName || entityId;

    wrapper.innerHTML = "";
    wrapper.appendChild(input);
    input.focus();
    input.select();

    const self = this;
    let saved = false;

    const originalValue = currentOverride || "";
    function save() {
      if (saved) return;
      saved = true;
      let newValue = input.value.trim();
      // Treat auto-generated name as "no override"
      if (newValue === autoName) newValue = "";
      // Skip save if nothing changed
      if (newValue === originalValue) {
        self._lastDataJson = "";
        self._updateIfChanged();
        return;
      }
      self._updateEntitySetting(entityId, { metric_name: newValue });
    }

    input.addEventListener("blur", save);
    input.addEventListener("keydown", function (e) {
      if (e.key === "Enter") {
        e.preventDefault();
        input.blur();
      } else if (e.key === "Escape") {
        saved = true;
        self._lastDataJson = "";
        self._updateIfChanged();
      }
    });
  }

  _formatDisplayName(entityId) {
    if (!this._hass) return entityId;

    const state = this._hass.states[entityId];
    const friendlyName = state ? (state.attributes.friendly_name || "") : "";
    if (!friendlyName) return entityId;

    const entities = this._hass.entities;
    const devices = this._hass.devices;
    const entityEntry = entities ? entities[entityId] : null;
    if (!entityEntry || !entityEntry.device_id) return friendlyName;

    const device = devices ? devices[entityEntry.device_id] : null;
    if (!device || !device.name) return friendlyName;

    const deviceName = device.name_by_user || device.name;

    // Split entity-specific name from device name
    var entityPart = "";
    if (friendlyName.startsWith(deviceName + " ")) {
      entityPart = friendlyName.substring(deviceName.length + 1);
    } else if (friendlyName === deviceName) {
      entityPart = "";
    } else {
      return friendlyName;
    }

    // Try to split manufacturer+model prefix from device name
    var devicePart = deviceName;
    var prefixPart = "";

    if (device.manufacturer && device.model) {
      var fullPrefix = device.manufacturer + " " + device.model;
      if (deviceName.startsWith(fullPrefix + " ") && deviceName !== fullPrefix) {
        prefixPart = fullPrefix;
        devicePart = deviceName.substring(fullPrefix.length + 1);
      } else if (deviceName.startsWith(device.model + " ") && deviceName !== device.model) {
        prefixPart = device.model;
        devicePart = deviceName.substring(device.model.length + 1);
      }
    } else if (device.model && deviceName.startsWith(device.model + " ") && deviceName !== device.model) {
      prefixPart = device.model;
      devicePart = deviceName.substring(device.model.length + 1);
    }

    var parts = [];
    if (prefixPart) parts.push(prefixPart);
    parts.push(devicePart);
    if (entityPart) parts.push(entityPart);

    return parts.join(" / ");
  }

  async _loadAuditLog() {
    if (!this._hass) return;
    try {
      var result = await this._hass.connection.sendMessagePromise({
        type: "victoria_metrics/get_audit_log",
        limit: 50,
      });
      this._auditEntries = result.entries || [];
      this._renderAuditLog();
    } catch (_err) {
      // Audit log is non-critical
    }
  }

  _renderAuditLog() {
    if (!this._auditCard) return;
    var entries = this._auditEntries;

    var countEl = this._auditSection.querySelector(".audit-count");
    if (countEl) {
      countEl.textContent = entries.length > 0
        ? "(" + entries.length + " recent)"
        : "";
    }

    if (entries.length === 0) {
      this._auditCard.innerHTML =
        '<div class="audit-empty">No export events recorded yet.</div>';
      return;
    }

    var html = "";
    for (var i = 0; i < entries.length; i++) {
      var e = entries[i];
      var d = new Date(e.timestamp * 1000);
      var timeStr = d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
      var valueStr = e.value === null ? "skipped" : String(e.value);
      var linesInfo = e.lines_count > 1 ? " (" + e.lines_count + " lines)" : "";

      html +=
        '<div class="audit-entry">' +
          '<span class="audit-time">' + escapeHtml(timeStr) + '</span>' +
          '<span class="audit-metric">' + escapeHtml(e.metric_name) + '</span>' +
          '<span class="audit-arrow">\u2192</span>' +
          '<span class="audit-value">' + escapeHtml(valueStr) + escapeHtml(linesInfo) + '</span>' +
          '<span class="audit-mode">' + escapeHtml(e.mode) + '</span>' +
        '</div>';
    }

    this._auditCard.innerHTML = html;
  }

  _updateDropdown() {
    if (!this._hass || this._searchQuery.length < 3) {
      this._closeDropdown();
      return;
    }

    const query = this._searchQuery.toLowerCase();
    const states = this._hass.states;
    const matches = [];

    for (const entityId of Object.keys(states)) {
      // Skip entities already exported
      if (this._configEntities.indexOf(entityId) >= 0) continue;
      // Skip VM integration's own entities
      if (entityId.startsWith("sensor.vm_export_")) continue;

      const state = states[entityId];
      const friendlyName = state.attributes.friendly_name || "";
      const searchText = entityId + " " + friendlyName.toLowerCase();

      if (searchText.indexOf(query) >= 0) {
        matches.push({
          entityId: entityId,
          friendlyName: friendlyName,
          stateValue: state.state,
          unit: state.attributes.unit_of_measurement || "",
        });
      }
      if (matches.length >= 100) break;
    }

    if (matches.length === 0) {
      this._closeDropdown();
      return;
    }

    let html = "";
    for (const m of matches) {
      const displayName = this._formatDisplayName(m.entityId);
      const valueText = m.stateValue + (m.unit ? " " + m.unit : "");
      html +=
        '<div class="dropdown-item" data-entity="' + escapeHtml(m.entityId) + '">' +
          '<div class="dropdown-item-header">' +
            '<span class="entity-name">' + escapeHtml(displayName) + "</span>" +
            '<span class="entity-value">' + escapeHtml(valueText) + "</span>" +
          "</div>" +
          '<span class="entity-detail">' + escapeHtml(m.entityId) + "</span>" +
        "</div>";
    }

    this._dropdown.innerHTML = html;
    this._dropdown.classList.add("open");

    const self = this;
    this._dropdown.querySelectorAll(".dropdown-item").forEach(function (item) {
      item.addEventListener("click", function (e) {
        e.stopPropagation();
        e.preventDefault();
        const entityId = item.getAttribute("data-entity");
        self._addEntity(entityId);
      });
    });
  }

  _closeDropdown() {
    if (this._dropdown) {
      this._dropdown.classList.remove("open");
    }
  }

  async _addEntity(entityId) {
    if (this._saving || this._configEntities.indexOf(entityId) >= 0) return;
    const newEntities = this._configEntities.concat([entityId]);
    await this._saveEntities(newEntities);
    this._searchInput.value = "";
    this._searchQuery = "";
    this._closeDropdown();
  }

  async _removeEntity(entityId) {
    if (this._saving) return;
    const newEntities = this._configEntities.filter(function (e) { return e !== entityId; });
    await this._saveEntities(newEntities);
  }

  async _saveEntities(entities) {
    if (!this._hass) return;
    this._saving = true;
    this._cardEl.classList.add("saving");

    try {
      await this._hass.connection.sendMessagePromise({
        type: "victoria_metrics/save_entities",
        entities: entities,
      });
      // Optimistically update local state while reload completes
      this._configEntities = entities;
      // Wait for the integration reload to complete, then refresh config
      await new Promise(function (resolve) { setTimeout(resolve, 2000); });
      await this._loadConfig();
    } catch (_err) {
      // Refresh config from backend on error
      await this._loadConfig();
    } finally {
      this._saving = false;
      this._cardEl.classList.remove("saving");
    }
  }
}

if (!customElements.get("victoria-metrics-panel")) {
  customElements.define("victoria-metrics-panel", VictoriaMetricsPanel);
}
