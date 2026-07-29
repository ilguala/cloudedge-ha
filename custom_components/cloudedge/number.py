"""
CloudEdge number platform.

Exposes how far one PTZ button press moves a camera. The protocol fixes the
motor speed, so the only thing that decides the distance is how long the motor
is held — which makes this a per-camera step-size knob rather than a device
setting: nothing is written to the camera when it changes.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, TYPE_CHECKING

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    PTZ_DEFAULT_DURATION,
    PTZ_STEP_MAX,
    PTZ_STEP_MIN,
    PTZ_STEP_STEP,
)

if TYPE_CHECKING:
    from . import CloudEdgeCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up CloudEdge number entities from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    if not coordinator.data:
        _LOGGER.warning("No devices found for number setup")
        return

    async_add_entities(
        CloudEdgePtzStepNumber(coordinator, device_sn, device_data)
        for device_sn, device_data in coordinator.data.items()
    )


class CloudEdgePtzStepNumber(CoordinatorEntity, RestoreEntity, NumberEntity):
    """How long one PTZ button press keeps the motor running."""

    _attr_entity_category = EntityCategory.CONFIG
    _attr_native_min_value = PTZ_STEP_MIN
    _attr_native_max_value = PTZ_STEP_MAX
    _attr_native_step = PTZ_STEP_STEP
    _attr_native_unit_of_measurement = UnitOfTime.SECONDS
    _attr_mode = NumberMode.BOX
    _attr_icon = "mdi:arrow-left-right"

    def __init__(
        self,
        coordinator,
        device_sn: str,
        device_data: Dict[str, Any],
    ) -> None:
        """Initialize the PTZ step duration knob."""
        super().__init__(coordinator)
        self._device_sn = device_sn
        self._device_data = device_data
        self._device_name = device_data.get("name", "Unknown Device")
        self._value = PTZ_DEFAULT_DURATION

        self._attr_name = f"{self._device_name} PTZ step duration"
        self._attr_unique_id = f"{device_sn}_ptz_step_duration"

    async def async_added_to_hass(self) -> None:
        """Restore the tuned value and publish it for the buttons to read."""
        await super().async_added_to_hass()

        last_state = await self.async_get_last_state()
        if last_state is not None:
            try:
                self._value = min(
                    PTZ_STEP_MAX, max(PTZ_STEP_MIN, float(last_state.state))
                )
            except (TypeError, ValueError):
                # unknown/unavailable after a restart: keep the default
                pass

        self.coordinator.ptz_step_duration[self._device_sn] = self._value

    @property
    def native_value(self) -> float:
        """Return the current step duration in seconds."""
        return self._value

    async def async_set_native_value(self, value: float) -> None:
        """Store the new step duration."""
        self._value = value
        self.coordinator.ptz_step_duration[self._device_sn] = value
        self.async_write_ha_state()

    @property
    def device_info(self) -> Dict[str, Any]:
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._device_sn)},
            "name": self._device_name,
            "manufacturer": "CloudEdge",
            "model": self._device_data.get("type", "SmartEye Camera"),
            "serial_number": self._device_sn,
        }
