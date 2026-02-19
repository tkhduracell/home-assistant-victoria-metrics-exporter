"""Panel registration for Victoria Metrics Exporter."""

from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.components import panel_custom
from homeassistant.components.frontend import async_remove_panel
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PANEL_COMPONENT_NAME, PANEL_ICON, PANEL_TITLE, PANEL_URL

_LOGGER = logging.getLogger(__name__)

_PANEL_FRONTEND_PATH = str(Path(__file__).parent / "www")


async def async_register_panel(hass: HomeAssistant) -> None:
    """Register the Victoria Metrics sidebar panel."""
    await hass.http.async_register_static_paths(
        [StaticPathConfig(PANEL_URL, _PANEL_FRONTEND_PATH, cache_headers=False)]
    )

    await panel_custom.async_register_panel(
        hass,
        webcomponent_name=PANEL_COMPONENT_NAME,
        frontend_url_path=DOMAIN,
        sidebar_title=PANEL_TITLE,
        sidebar_icon=PANEL_ICON,
        module_url=f"{PANEL_URL}/{PANEL_COMPONENT_NAME}.js",
        embed_iframe=False,
        require_admin=False,
        config={},
    )
    _LOGGER.debug("Registered Victoria Metrics sidebar panel")


def async_unregister_panel(hass: HomeAssistant) -> None:
    """Remove the Victoria Metrics sidebar panel."""
    async_remove_panel(hass, DOMAIN)
    _LOGGER.debug("Removed Victoria Metrics sidebar panel")
