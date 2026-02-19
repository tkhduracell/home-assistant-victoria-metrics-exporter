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
  .saving {
    opacity: 0.6;
    pointer-events: none;
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
    header.innerHTML = "<h1>Victoria Metrics Exports</h1>";
    this.shadowRoot.appendChild(header);

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

    rows.sort(function (a, b) { return a.sourceEntity.localeCompare(b.sourceEntity); });
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

      tableRows +=
        "<tr>" +
        '<td class="entity-id">' + escapeHtml(r.sourceEntity) + "</td>" +
        "<td>" +
          '<a class="entity-link" data-entity="' + escapeHtml(r.sourceEntity) + '" href="#">' +
            escapeHtml(r.friendlyName) +
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
      html +=
        '<div class="dropdown-item" data-entity="' + escapeHtml(m.entityId) + '">' +
          '<span class="entity-name">' + escapeHtml(m.friendlyName || m.entityId) + "</span>" +
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
