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
    gap: 12px;
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
  .metric-name {
    font-family: var(--code-font-family, monospace);
    font-size: 13px;
    color: var(--primary-color);
  }
  .mode-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 500;
    text-transform: capitalize;
  }
  .mode-realtime {
    background: var(--label-badge-green, #4caf50);
    color: white;
  }
  .mode-batch {
    background: var(--label-badge-blue, #2196f3);
    color: white;
  }
  .tags {
    font-family: var(--code-font-family, monospace);
    font-size: 12px;
    color: var(--secondary-text-color);
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
  }

  set hass(hass) {
    this._hass = hass;
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

    this._countEl = document.createElement("div");
    this._countEl.className = "count";
    this.shadowRoot.appendChild(this._countEl);

    this._cardEl = document.createElement("div");
    this._cardEl.className = "card";
    this.shadowRoot.appendChild(this._cardEl);
  }

  _getExportData() {
    if (!this._hass) return [];

    const states = this._hass.states;
    const rows = [];

    for (const entityId of Object.keys(states)) {
      if (!entityId.startsWith("sensor.vm_export_")) continue;

      const sensor = states[entityId];
      const attrs = sensor.attributes;
      const sourceEntity = attrs.source_entity || "";
      const metricName = attrs.metric_name || sensor.state || "";
      const mode = attrs.mode || "batch";
      const customTags = attrs.custom_tags || {};

      const sourceState = states[sourceEntity];
      const friendlyName = sourceState
        ? sourceState.attributes.friendly_name || sourceEntity
        : sourceEntity;

      rows.push({
        sourceEntity,
        friendlyName,
        metricName,
        mode,
        customTags: Object.entries(customTags)
          .map(([k, v]) => k + "=" + v)
          .join(", "),
      });
    }

    rows.sort((a, b) => a.sourceEntity.localeCompare(b.sourceEntity));
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
      this._cardEl.innerHTML = `
        <div class="empty-state">
          <p>No entities are configured for export.</p>
          <p>Go to <b>Settings &gt; Devices &amp; Services &gt; Victoria Metrics &gt; Configure</b> to select entities.</p>
        </div>`;
      return;
    }

    this._countEl.textContent =
      rows.length + " entit" + (rows.length === 1 ? "y" : "ies") + " exported";

    let tableRows = "";
    for (const r of rows) {
      const modeClass = r.mode === "realtime" ? "mode-realtime" : "mode-batch";
      tableRows +=
        "<tr>" +
        '<td class="entity-id">' + escapeHtml(r.sourceEntity) + "</td>" +
        "<td>" + escapeHtml(r.friendlyName) + "</td>" +
        '<td class="metric-name">' + escapeHtml(r.metricName) + "</td>" +
        "<td>" +
          '<span class="mode-badge ' + modeClass + '">' +
            escapeHtml(r.mode) +
          "</span>" +
        "</td>" +
        '<td class="tags">' + (r.customTags ? escapeHtml(r.customTags) : "\u2014") + "</td>" +
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
        "</tr></thead>" +
        "<tbody>" + tableRows + "</tbody>" +
      "</table>";
  }
}

customElements.define("victoria-metrics-panel", VictoriaMetricsPanel);
