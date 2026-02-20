"""Config flow for Victoria Metrics Exporter integration."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlowWithConfigEntry,
)
from homeassistant.core import callback
from homeassistant.helpers import entity_registry as er
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

    _user_input: dict[str, Any] | None = None
    _connect_task: asyncio.Task[bool] | None = None
    _connect_error: str | None = None

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

        if self._connect_error is not None:
            errors["base"] = self._connect_error
            self._connect_error = None

        if user_input is not None:
            await self.async_set_unique_id(
                f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}"
            )
            self._abort_if_unique_id_configured()

            self._user_input = user_input
            return await self.async_step_connect()

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def _async_test_connection(self) -> bool:
        """Run the connection test in a background task."""
        if self._user_input is None:
            return False
        writer = VictoriaMetricsWriter(
            host=self._user_input[CONF_HOST],
            port=self._user_input[CONF_PORT],
            ssl=self._user_input.get(CONF_SSL, False),
            verify_ssl=self._user_input.get(CONF_VERIFY_SSL, True),
            token=self._user_input.get(CONF_TOKEN) or None,
        )
        try:
            return await writer.test_connection()
        finally:
            await writer.close()

    async def async_step_connect(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Test the connection with a progress spinner."""
        if self._connect_task is None:
            self._connect_task = self.hass.async_create_task(
                self._async_test_connection(),
                "Victoria Metrics connection test",
            )

        task = self._connect_task

        if not task.done():
            return self.async_show_progress(
                step_id="connect",
                progress_action="connecting",
                progress_task=task,
            )

        self._connect_task = None

        try:
            result = task.result()
        except Exception:
            _LOGGER.exception("Unexpected error during connection test")
            self._connect_error = "unknown"
            return self.async_show_progress_done(next_step_id="user")

        if not result:
            self._connect_error = "cannot_connect"
            return self.async_show_progress_done(next_step_id="user")

        return self.async_show_progress_done(next_step_id="finish")

    async def async_step_finish(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Create the config entry after successful connection."""
        if self._user_input is None:
            return self.async_abort(reason="unknown")
        title = f"Victoria Metrics ({self._user_input[CONF_HOST]}:{self._user_input[CONF_PORT]})"
        return self.async_create_entry(title=title, data=self._user_input)


class VictoriaMetricsOptionsFlowHandler(OptionsFlowWithConfigEntry):
    """Handle Victoria Metrics options."""

    _user_input: dict[str, Any]
    _save_task: asyncio.Task[bool] | None = None
    _save_error: str | None = None

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the export options."""
        if user_input is not None:
            self._user_input = user_input
            return await self.async_step_preview()

        # Exclude our own integration entities from the entity picker
        ent_reg = er.async_get(self.hass)
        vm_entity_ids = [
            entry.entity_id
            for entry in ent_reg.entities.get_entries_for_config_entry_id(
                self.config_entry.entry_id
            )
        ]

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
                ): EntitySelector(
                    EntitySelectorConfig(
                        multiple=True,
                        exclude_entities=vm_entity_ids,
                    )
                ),
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
            return await self.async_step_save()

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

    async def _async_validate_connection(self) -> bool:
        """Revalidate the Victoria Metrics connection before saving."""
        writer = VictoriaMetricsWriter(
            host=self.config_entry.data[CONF_HOST],
            port=self.config_entry.data[CONF_PORT],
            ssl=self.config_entry.data.get(CONF_SSL, False),
            verify_ssl=self.config_entry.data.get(CONF_VERIFY_SSL, True),
            token=self.config_entry.data.get(CONF_TOKEN) or None,
        )
        try:
            return await writer.test_connection()
        finally:
            await writer.close()

    async def async_step_save(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Validate connection and save options with a progress spinner."""
        if self._save_task is None:
            self._save_task = self.hass.async_create_task(
                self._async_validate_connection(),
                "Victoria Metrics connection revalidation",
            )

        task = self._save_task

        if not task.done():
            return self.async_show_progress(
                step_id="save",
                progress_action="saving",
                progress_task=task,
            )

        self._save_task = None

        try:
            result = task.result()
        except Exception:
            _LOGGER.exception("Unexpected error during connection revalidation")
            self._save_error = "save_failed"
            return self.async_show_progress_done(next_step_id="save_failed")

        if not result:
            self._save_error = "cannot_connect"
            return self.async_show_progress_done(next_step_id="save_failed")

        return self.async_show_progress_done(next_step_id="save_done")

    async def async_step_save_done(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Finalize saving the options entry."""
        return self.async_create_entry(data=self._user_input)

    async def async_step_save_failed(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle save failure — allow user to retry."""
        if user_input is not None:
            self._save_error = None
            return await self.async_step_init()

        return self.async_show_form(
            step_id="save_failed",
            data_schema=vol.Schema({}),
            errors={"base": self._save_error or "cannot_connect"},
        )
