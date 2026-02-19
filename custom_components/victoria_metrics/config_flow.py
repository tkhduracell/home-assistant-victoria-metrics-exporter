"""Config flow for Victoria Metrics Exporter integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlowWithConfigEntry,
)
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    EntitySelector,
    EntitySelectorConfig,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    TextSelector,
    TextSelectorConfig,
)
import voluptuous as vol

from .const import (
    CONF_BATCH_INTERVAL,
    CONF_EXPORT_ENTITIES,
    CONF_HOST,
    CONF_METRIC_PREFIX,
    CONF_PORT,
    CONF_SSL,
    CONF_TOKEN,
    CONF_VERIFY_SSL,
    DEFAULT_BATCH_INTERVAL,
    DEFAULT_METRIC_PREFIX,
    DEFAULT_PORT,
    DOMAIN,
    build_metric_name,
)
from .writer import VictoriaMetricsWriter

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
        vol.Optional(CONF_SSL, default=False): bool,
        vol.Optional(CONF_VERIFY_SSL, default=True): bool,
        vol.Optional(CONF_TOKEN, default=""): str,
    }
)


class VictoriaMetricsConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Victoria Metrics Exporter."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> VictoriaMetricsOptionsFlowHandler:
        """Create the options flow."""
        return VictoriaMetricsOptionsFlowHandler(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step — connection settings."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Prevent duplicate entries for the same host
            await self.async_set_unique_id(
                f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}"
            )
            self._abort_if_unique_id_configured()

            # Test the connection
            writer = VictoriaMetricsWriter(
                host=user_input[CONF_HOST],
                port=user_input[CONF_PORT],
                ssl=user_input.get(CONF_SSL, False),
                verify_ssl=user_input.get(CONF_VERIFY_SSL, True),
                token=user_input.get(CONF_TOKEN) or None,
            )

            try:
                if await writer.test_connection():
                    await writer.close()
                    title = f"Victoria Metrics ({user_input[CONF_HOST]}:{user_input[CONF_PORT]})"
                    return self.async_create_entry(title=title, data=user_input)
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected error during connection test")
                errors["base"] = "unknown"
            finally:
                await writer.close()

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )


class VictoriaMetricsOptionsFlowHandler(OptionsFlowWithConfigEntry):
    """Handle Victoria Metrics options."""

    _user_input: dict[str, Any]

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the export options."""
        if user_input is not None:
            self._user_input = user_input
            return await self.async_step_preview()

        options_schema = vol.Schema(
            {
                vol.Optional(
                    CONF_METRIC_PREFIX,
                    default=DEFAULT_METRIC_PREFIX,
                ): TextSelector(TextSelectorConfig()),
                vol.Optional(
                    CONF_BATCH_INTERVAL,
                    default=DEFAULT_BATCH_INTERVAL,
                ): NumberSelector(
                    NumberSelectorConfig(
                        min=10,
                        max=3600,
                        step=1,
                        mode=NumberSelectorMode.BOX,
                        unit_of_measurement="seconds",
                    )
                ),
                vol.Optional(
                    CONF_EXPORT_ENTITIES,
                    default=[],
                ): EntitySelector(EntitySelectorConfig(multiple=True)),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(
                options_schema, self.options
            ),
        )

    async def async_step_preview(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Show metric name preview before confirming."""
        if user_input is not None:
            return self.async_create_entry(data=self._user_input)

        prefix = self._user_input.get(CONF_METRIC_PREFIX, DEFAULT_METRIC_PREFIX)
        entities: list[str] = self._user_input.get(CONF_EXPORT_ENTITIES, [])

        if not entities:
            preview_text = "No entities selected."
        else:
            max_preview = 20
            lines: list[str] = []
            for entity_id in entities[:max_preview]:
                metric = build_metric_name(prefix, entity_id)
                lines.append(f"  {entity_id} \u2192 {metric}")
            preview_text = "\n".join(lines)
            if len(entities) > max_preview:
                preview_text += f"\n  ... and {len(entities) - max_preview} more"

        return self.async_show_form(
            step_id="preview",
            data_schema=vol.Schema({}),
            description_placeholders={
                "entity_count": str(len(entities)),
                "metric_preview": preview_text,
            },
        )
