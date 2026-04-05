"""Panel registration for Victoria Metrics Exporter."""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path

from homeassistant.components import panel_custom
from homeassistant.components.frontend import async_remove_panel
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PANEL_COMPONENT_NAME, PANEL_ICON, PANEL_TITLE, PANEL_URL

_LOGGER = logging.getLogger(__name__)

_PANEL_DIR = Path(__file__).parent / "www"
_PANEL_FRONTEND_PATH = str(_PANEL_DIR)


async def async_register_panel(hass: HomeAssistant) -> None:
    """Register the Victoria Metrics sidebar panel."""
    # Compute content hash for cache busting
    js_path = _PANEL_DIR / f"{PANEL_COMPONENT_NAME}.js"
    file_hash = hashlib.sha256(js_path.read_bytes()).hexdigest()[:8]

    await hass.http.async_register_static_paths(
        [StaticPathConfig(PANEL_URL, _PANEL_FRONTEND_PATH, cache_headers=False)]
    )

    await panel_custom.async_register_panel(
        hass,
        webcomponent_name=PANEL_COMPONENT_NAME,
        frontend_url_path=DOMAIN,
        sidebar_title=PANEL_TITLE,
        sidebar_icon=PANEL_ICON,
        module_url=f"{PANEL_URL}/{PANEL_COMPONENT_NAME}.js?h={file_hash}",
        embed_iframe=False,
        require_admin=False,
        config={},
    )
    _LOGGER.debug("Registered Victoria Metrics sidebar panel")


def async_register_more_info_js(hass: HomeAssistant) -> None:
    """Register the more-info button JS as a globally loaded extra module."""
    from homeassistant.components.frontend import add_extra_js_url  # noqa: PLC0415

    js_path = _PANEL_DIR / "victoria-metrics-more-info.js"
    file_hash = hashlib.sha256(js_path.read_bytes()).hexdigest()[:8]

    # The static path PANEL_URL -> www/ is already registered by async_register_panel,
    # so the JS file is accessible at /victoria_metrics_panel/victoria-metrics-more-info.js
    add_extra_js_url(hass, f"{PANEL_URL}/victoria-metrics-more-info.js?h={file_hash}")
    _LOGGER.debug("Registered Victoria Metrics more-info JS module")


def async_unregister_panel(hass: HomeAssistant) -> None:
    """Remove the Victoria Metrics sidebar panel."""
    async_remove_panel(hass, DOMAIN)
    _LOGGER.debug("Removed Victoria Metrics sidebar panel")
