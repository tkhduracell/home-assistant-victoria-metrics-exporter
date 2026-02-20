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
    max-height: 240px;
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
  .dropdown-item .entity-name {
    color: var(--primary-text-color);
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
  .toggle-wrapper {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .toggle {
    position: relative;
    width: 36px;
    height: 20px;
    flex-shrink: 0;
  }
  .toggle input {
    opacity: 0;
    width: 0;
    height: 0;
    position: absolute;
  }
  .toggle .slider {
    position: absolute;
    cursor: pointer;
    top: 0; left: 0; right: 0; bottom: 0;
    background: var(--label-badge-blue, #2196f3);
    border-radius: 20px;
    transition: background 0.2s;
  }
  .toggle input:checked + .slider {
    background: var(--label-badge-green, #4caf50);
  }
  .toggle .slider::before {
    content: "";
    position: absolute;
    width: 16px;
    height: 16px;
    left: 2px;
    bottom: 2px;
    background: white;
    border-radius: 50%;
    transition: transform 0.2s;
  }
  .toggle input:checked + .slider::before {
    transform: translateX(16px);
  }
  .toggle-label {
    font-size: 12px;
    font-weight: 500;
    text-transform: capitalize;
    min-width: 52px;
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
  .tags {
    font-family: var(--code-font-family, monospace);
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
      '<button class="settings-btn">' +
        '<svg viewBox="0 0 24 24"><path d="M12,15.5A3.5,3.5 0 0,1 8.5,12A3.5,3.5 0 0,1 12,8.5A3.5,3.5 0 0,1 15.5,12A3.5,3.5 0 0,1 12,15.5M19.43,12.97C19.47,12.65 19.5,12.33 19.5,12C19.5,11.67 19.47,11.34 19.43,11L21.54,9.37C21.73,9.22 21.78,8.95 21.66,8.73L19.66,5.27C19.54,5.05 19.27,4.96 19.05,5.05L16.56,6.05C16.04,5.66 15.5,5.32 14.87,5.07L14.5,2.42C14.46,2.18 14.25,2 14,2H10C9.75,2 9.54,2.18 9.5,2.42L9.13,5.07C8.5,5.32 7.96,5.66 7.44,6.05L4.95,5.05C4.73,4.96 4.46,5.05 4.34,5.27L2.34,8.73C2.21,8.95 2.27,9.22 2.46,9.37L4.57,11C4.53,11.34 4.5,11.67 4.5,12C4.5,12.33 4.53,12.65 4.57,12.97L2.46,14.63C2.27,14.78 2.21,15.05 2.34,15.27L4.34,18.73C4.46,18.95 4.73,19.04 4.95,18.95L7.44,17.95C7.96,18.34 8.5,18.68 9.13,18.93L9.5,21.58C9.54,21.82 9.75,22 10,22H14C14.25,22 14.46,21.82 14.5,21.58L14.87,18.93C15.5,18.68 16.04,18.34 16.56,17.95L19.05,18.95C19.27,19.04 19.54,18.95 19.66,18.73L21.66,15.27C21.78,15.05 21.73,14.78 21.54,14.63L19.43,12.97Z"/></svg>' +
        "Settings" +
      "</button>" +
      "</div>";
    this.shadowRoot.appendChild(header);

    header.querySelector(".view-config-btn").addEventListener("click", () => {
      this._showConfigOverlay();
    });
    header.querySelector(".settings-btn:not(.view-config-btn)").addEventListener("click", () => {
      this._navigateToSettings();
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
      if (this._searchQuery.length >= 2) {
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
      const realtime = item.realtime || false;
      const batchInterval = item.batch_interval || this._config.batch_interval || 300;
      const sourceState = states[entityId];
      const friendlyName = sourceState
        ? sourceState.attributes.friendly_name || entityId
        : entityId;

      // Check the sensor entity for custom tags
      const sensorId = "sensor.vm_export_" + entityId.replace(".", "_");
      const sensorState = states[sensorId];
      const customTags = sensorState
        ? sensorState.attributes.custom_tags || {}
        : {};

      rows.push({
        sourceEntity: entityId,
        friendlyName: friendlyName,
        metricName: metricName,
        realtime: realtime,
        batchInterval: batchInterval,
        customTags: Object.entries(customTags)
          .map(function (pair) { return pair[0] + "=" + pair[1]; })
          .join(", "),
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

    let tableRows = "";
    for (const r of rows) {
      const checkedAttr = r.realtime ? " checked" : "";
      const modeLabel = r.realtime ? "realtime" : "batch";

      let modeCell =
        '<div class="toggle-wrapper">' +
          '<label class="toggle">' +
            '<input type="checkbox"' + checkedAttr +
              ' data-entity="' + escapeHtml(r.sourceEntity) + '"' +
              ' class="realtime-toggle">' +
            '<span class="slider"></span>' +
          '</label>' +
          '<span class="toggle-label">' + modeLabel + '</span>';

      if (!r.realtime) {
        modeCell +=
          '<input type="number" class="batch-interval-input"' +
            ' value="' + r.batchInterval + '"' +
            ' min="10" max="3600" step="10"' +
            ' data-entity="' + escapeHtml(r.sourceEntity) + '">' +
          '<span class="batch-interval-suffix">s</span>';
      }
      modeCell += '</div>';

      const displayName = this._formatDisplayName(r.sourceEntity);
      tableRows +=
        "<tr>" +
        '<td class="entity-id">' + escapeHtml(r.sourceEntity) + "</td>" +
        "<td>" +
          '<a class="entity-link" data-entity="' + escapeHtml(r.sourceEntity) + '" href="#">' +
            escapeHtml(displayName) +
          "</a>" +
        "</td>" +
        '<td class="metric-name">' + escapeHtml(r.metricName) + "</td>" +
        "<td>" + modeCell + "</td>" +
        '<td class="tags">' + (r.customTags ? escapeHtml(r.customTags) : "\u2014") + "</td>" +
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
          "<th>Mode</th>" +
          "<th>Tags</th>" +
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

    // Realtime toggle handlers
    this._cardEl.querySelectorAll(".realtime-toggle").forEach(function (toggle) {
      toggle.addEventListener("change", function () {
        const entityId = toggle.getAttribute("data-entity");
        self._updateEntitySetting(entityId, { realtime: toggle.checked });
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

  _navigateToSettings() {
    window.history.pushState(null, "", "/config/integrations/integration/victoria_metrics");
    window.dispatchEvent(new CustomEvent("location-changed"));
  }

  _showConfigOverlay() {
    if (!this._config) return;

    const c = this._config;
    const entityCount = c.entities ? c.entities.length : 0;
    const realtimeCount = c.entities ? c.entities.filter(function (e) { return e.realtime; }).length : 0;
    const batchCount = entityCount - realtimeCount;

    let entitiesHtml = "";
    if (c.entities && c.entities.length > 0) {
      const sorted = c.entities.slice().sort(function (a, b) {
        return a.entity_id.localeCompare(b.entity_id);
      });
      entitiesHtml = '<table style="width:100%;font-size:13px;border-collapse:collapse;">' +
        "<thead><tr>" +
          '<th style="text-align:left;padding:4px 8px;border-bottom:1px solid var(--divider-color);">Entity</th>' +
          '<th style="text-align:left;padding:4px 8px;border-bottom:1px solid var(--divider-color);">Metric</th>' +
          '<th style="text-align:left;padding:4px 8px;border-bottom:1px solid var(--divider-color);">Mode</th>' +
          '<th style="text-align:right;padding:4px 8px;border-bottom:1px solid var(--divider-color);">Interval</th>' +
        "</tr></thead><tbody>";
      for (const e of sorted) {
        entitiesHtml +=
          "<tr>" +
          '<td style="padding:4px 8px;font-family:monospace;font-size:12px;">' + escapeHtml(e.entity_id) + "</td>" +
          '<td style="padding:4px 8px;font-family:monospace;font-size:12px;">' + escapeHtml(e.metric_name) + "</td>" +
          '<td style="padding:4px 8px;">' + (e.realtime ? "realtime" : "batch") + "</td>" +
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
          '<div class="config-label">Entities (' + entityCount + " total \u2014 " + realtimeCount + " realtime, " + batchCount + " batch)</div>" +
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
      if ("realtime" in settings) msg.realtime = settings.realtime;
      if ("batch_interval" in settings) msg.batch_interval = settings.batch_interval;

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

  _updateDropdown() {
    if (!this._hass || this._searchQuery.length < 2) {
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
      if (entityId.startsWith("sensor.vm_export_") || entityId.startsWith("switch.vm_realtime_")) continue;

      const state = states[entityId];
      const friendlyName = state.attributes.friendly_name || "";
      const searchText = entityId + " " + friendlyName.toLowerCase();

      if (searchText.indexOf(query) >= 0) {
        matches.push({ entityId: entityId, friendlyName: friendlyName });
      }
      if (matches.length >= 10) break;
    }

    if (matches.length === 0) {
      this._closeDropdown();
      return;
    }

    let html = "";
    for (const m of matches) {
      const displayName = this._formatDisplayName(m.entityId);
      html +=
        '<div class="dropdown-item" data-entity="' + escapeHtml(m.entityId) + '">' +
          '<span class="entity-name">' + escapeHtml(displayName) + "</span>" +
          '<span class="entity-detail">' + escapeHtml(m.entityId) + "</span>" +
        "</div>";
    }

    this._dropdown.innerHTML = html;
    this._dropdown.classList.add("open");

    const self = this;
    this._dropdown.querySelectorAll(".dropdown-item").forEach(function (item) {
      item.addEventListener("click", function () {
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

customElements.define("victoria-metrics-panel", VictoriaMetricsPanel);
