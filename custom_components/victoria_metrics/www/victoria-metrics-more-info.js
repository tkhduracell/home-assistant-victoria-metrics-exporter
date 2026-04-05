/**
 * Victoria Metrics — More-Info dialog integration.
 *
 * Injects an "Export to Victoria Metrics" / "Remove from Victoria Metrics"
 * button into the native Home Assistant entity more-info dialog.
 *
 * Loaded globally via frontend.add_extra_js_url().
 */
(function () {
  "use strict";

  const BUTTON_ID = "vm-more-info-btn";
  const DOMAIN = "victoria_metrics";

  // ── Helpers ──────────────────────────────────────────────────────────

  function getHass() {
    const ha = document.querySelector("home-assistant");
    return ha && ha.hass;
  }

  function getConnection() {
    const hass = getHass();
    return hass && hass.connection;
  }

  /** Fetch tracked entity list from the integration. */
  async function getTrackedEntities() {
    const conn = getConnection();
    if (!conn) return null;
    try {
      const result = await conn.sendMessagePromise({
        type: "victoria_metrics/get_config",
      });
      return new Set((result.entities || []).map(function (e) { return e.entity_id; }));
    } catch (_err) {
      // Integration not loaded or no config entry
      return null;
    }
  }

  async function addEntity(entityId) {
    const conn = getConnection();
    if (!conn) return;
    return conn.sendMessagePromise({
      type: "victoria_metrics/add_entity",
      entity_id: entityId,
    });
  }

  async function removeEntity(entityId) {
    const conn = getConnection();
    if (!conn) return;
    return conn.sendMessagePromise({
      type: "victoria_metrics/remove_entity",
      entity_id: entityId,
    });
  }

  // ── SVG icon (mdi:chart-line) ───────────────────────────────────────

  const ICON_SVG =
    '<svg viewBox="0 0 24 24" style="width:18px;height:18px;fill:currentColor;">' +
    '<path d="M16,11.78L20.24,4.45L21.97,5.45L16.74,14.5L10.23,10.75L5.46,' +
    '19H22V21H2V3H4V17.54L9.5,8L16,11.78Z"/>' +
    "</svg>";

  // ── CSS ─────────────────────────────────────────────────────────────

  const STYLE_ID = "vm-more-info-style";

  function ensureStyles() {
    if (document.getElementById(STYLE_ID)) return;
    const style = document.createElement("style");
    style.id = STYLE_ID;
    style.textContent =
      "#" + BUTTON_ID + " {" +
      "  display: inline-flex; align-items: center; gap: 6px;" +
      "  padding: 6px 14px; margin: 8px 16px;" +
      "  border: none; border-radius: 8px; cursor: pointer;" +
      "  font-size: 13px; font-weight: 500;" +
      "  font-family: var(--paper-font-body1_-_font-family, Roboto, sans-serif);" +
      "  transition: opacity 0.15s;" +
      "}" +
      "#" + BUTTON_ID + ":hover { opacity: 0.85; }" +
      "#" + BUTTON_ID + ".vm-add {" +
      "  background: var(--primary-color); color: var(--text-primary-color, #fff);" +
      "}" +
      "#" + BUTTON_ID + ".vm-remove {" +
      "  background: var(--error-color, #db4437); color: var(--text-primary-color, #fff);" +
      "}" +
      "#" + BUTTON_ID + ".vm-loading {" +
      "  opacity: 0.6; pointer-events: none;" +
      "}" +
      "#" + BUTTON_ID + ".vm-hidden { display: none; }";
    document.head.appendChild(style);
  }

  // ── Button injection ────────────────────────────────────────────────

  /** Try to find the entity_id from the dialog element. */
  function getEntityIdFromDialog(dialog) {
    // Modern HA exposes entityId or a large property
    if (dialog.entityId) return dialog.entityId;

    // Try the dialog's internal state object
    if (dialog.stateObj && dialog.stateObj.entity_id) {
      return dialog.stateObj.entity_id;
    }

    // Traverse known shadow DOM paths for the entity_id
    var root = dialog.shadowRoot || dialog;
    // ha-more-info-dialog may wrap ha-dialog which wraps ha-more-info
    var moreInfo =
      root.querySelector("ha-more-info") ||
      root.querySelector("ha-more-info-info");
    if (moreInfo) {
      if (moreInfo.entityId) return moreInfo.entityId;
      if (moreInfo.stateObj && moreInfo.stateObj.entity_id) {
        return moreInfo.stateObj.entity_id;
      }
    }

    // Fallback: look for entity_id in heading text or attribute
    var header = root.querySelector("[data-entity-id]");
    if (header) return header.getAttribute("data-entity-id");

    // Look at the dialog's large property (Lit element)
    if (dialog._entityId) return dialog._entityId;
    if (dialog.large != null && dialog._params && dialog._params.entityId) {
      return dialog._params.entityId;
    }

    return null;
  }

  /** Find a suitable place to insert the button. */
  function findInsertionPoint(dialog) {
    var root = dialog.shadowRoot || dialog;

    // Try to find the content area of the dialog
    var content =
      root.querySelector(".content") ||
      root.querySelector("ha-dialog-header") ||
      root.querySelector("div[slot='content']");
    if (content) return { parent: content, position: "afterbegin" };

    // Fallback: insert directly into the dialog root
    return { parent: root, position: "afterbegin" };
  }

  function createButton(entityId, isTracked) {
    var btn = document.createElement("button");
    btn.id = BUTTON_ID;
    btn.className = isTracked ? "vm-remove" : "vm-add";
    btn.innerHTML =
      ICON_SVG +
      "<span>" +
      (isTracked ? "Remove from Victoria Metrics" : "Export to Victoria Metrics") +
      "</span>";

    btn.addEventListener("click", async function () {
      btn.classList.add("vm-loading");
      btn.querySelector("span").textContent = isTracked
        ? "Removing..."
        : "Adding...";
      try {
        if (isTracked) {
          await removeEntity(entityId);
        } else {
          await addEntity(entityId);
        }
        // Update button state optimistically
        var nowTracked = !isTracked;
        btn.className = nowTracked ? "vm-remove" : "vm-add";
        btn.innerHTML =
          ICON_SVG +
          "<span>" +
          (nowTracked
            ? "Remove from Victoria Metrics"
            : "Export to Victoria Metrics") +
          "</span>";
        // Rebind for the new state (replace the button)
        var newBtn = createButton(entityId, nowTracked);
        btn.replaceWith(newBtn);
      } catch (_err) {
        btn.classList.remove("vm-loading");
        btn.querySelector("span").textContent = "Error — try again";
      }
    });

    return btn;
  }

  async function injectButton(dialog) {
    // Remove any existing button first
    var existing = dialog.querySelector("#" + BUTTON_ID);
    if (!existing && dialog.shadowRoot) {
      existing = dialog.shadowRoot.querySelector("#" + BUTTON_ID);
    }
    if (existing) existing.remove();

    var entityId = getEntityIdFromDialog(dialog);
    if (!entityId) return;

    // Skip the integration's own entities
    if (entityId.indexOf(DOMAIN) !== -1) return;

    var tracked = await getTrackedEntities();
    // If integration is not configured at all, don't show button
    if (tracked === null) return;

    ensureStyles();

    var isTracked = tracked.has(entityId);
    var btn = createButton(entityId, isTracked);

    var point = findInsertionPoint(dialog);
    point.parent.insertAdjacentElement(
      point.position === "afterbegin" ? "afterbegin" : "beforeend",
      btn
    );
  }

  // ── Dialog observation ──────────────────────────────────────────────

  var _pendingCheck = null;

  function checkForDialog() {
    if (_pendingCheck) return;
    _pendingCheck = setTimeout(function () {
      _pendingCheck = null;
      _doCheck();
    }, 150);
  }

  function _doCheck() {
    var ha = document.querySelector("home-assistant");
    if (!ha || !ha.shadowRoot) return;

    var dialog =
      ha.shadowRoot.querySelector("ha-more-info-dialog") ||
      ha.shadowRoot.querySelector("ha-dialog[data-domain]");

    if (!dialog) {
      // Check inside nested shadow roots (some HA versions)
      var mainEl = ha.shadowRoot.querySelector("home-assistant-main");
      if (mainEl && mainEl.shadowRoot) {
        dialog = mainEl.shadowRoot.querySelector("ha-more-info-dialog");
      }
    }

    if (!dialog) return;

    // Wait a bit for the dialog to render its contents
    setTimeout(function () {
      injectButton(dialog);
    }, 200);
  }

  function startObserver() {
    var ha = document.querySelector("home-assistant");
    if (!ha) {
      // HA not ready yet, retry
      setTimeout(startObserver, 1000);
      return;
    }

    if (!ha.shadowRoot) {
      setTimeout(startObserver, 500);
      return;
    }

    // Observe the shadow root for dialog additions/changes
    var observer = new MutationObserver(function () {
      checkForDialog();
    });

    observer.observe(ha.shadowRoot, { childList: true, subtree: true });

    // Also observe home-assistant-main if it exists
    var mainEl = ha.shadowRoot.querySelector("home-assistant-main");
    if (mainEl && mainEl.shadowRoot) {
      observer.observe(mainEl.shadowRoot, { childList: true, subtree: true });
    }

    // Listen for the hass-more-info custom event as a secondary trigger
    window.addEventListener("hass-more-info", function () {
      setTimeout(checkForDialog, 300);
    });
  }

  // ── Init ────────────────────────────────────────────────────────────

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", startObserver);
  } else {
    startObserver();
  }
})();
