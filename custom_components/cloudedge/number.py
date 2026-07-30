"""
CloudEdge number platform.

Tuning knobs, none of which writes anything to the camera:

* PTZ step duration, per camera. The protocol fixes the motor speed, so the only
  thing that decides how far a button press moves the camera is how long the
  motor is held.
* Video stall timeout and reconnect cooldown, per account. The two waits that
  decide what fraction of the wall clock actually carries video.
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
    RECONNECT_COOLDOWN,
    RECONNECT_COOLDOWN_DEFAULT,
    RECONNECT_COOLDOWN_MAX,
    RECONNECT_COOLDOWN_MIN,
    VIDEO_STALL_TIMEOUT_DEFAULT,
    VIDEO_STALL_TIMEOUT_MAX,
    VIDEO_STALL_TIMEOUT_MIN,
    PTZ_DEFAULT_DURATION,
    PTZ_STEP_MAX,
    PTZ_STEP_MIN,
    PTZ_STEP_STEP,
    apply_video_stall_timeout,
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

    entities: list[NumberEntity] = [
        CloudEdgePtzStepNumber(coordinator, device_sn, device_data)
        for device_sn, device_data in coordinator.data.items()
    ]

    # One per account, not per camera: both are module-level settings shared by
    # every stream this account opens.
    entities.append(
        CloudEdgeVideoStallTimeoutNumber(coordinator, config_entry.entry_id)
    )
    entities.append(
        CloudEdgeReconnectCooldownNumber(coordinator, config_entry.entry_id)
    )

    async_add_entities(entities)


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


class CloudEdgeVideoStallTimeoutNumber(CoordinatorEntity, RestoreEntity, NumberEntity):
    """How long a stalled live window is given before the session is torn down.

    A live window ends without warning: the camera simply stops sending, and the
    only way to tell is that no frame has arrived for a while. Waiting longer
    than necessary to conclude that costs dead time on every single window, and
    dead time is the dominant term in how choppy the stream looks.

    The floor is above the library's KCP gap-skip delay on purpose: a lost
    segment blocks delivery for two seconds before the skip unblocks it, so a
    shorter timeout would tear down windows that were about to recover.
    """

    _attr_entity_category = EntityCategory.CONFIG
    _attr_native_min_value = VIDEO_STALL_TIMEOUT_MIN
    _attr_native_max_value = VIDEO_STALL_TIMEOUT_MAX
    _attr_native_step = 0.5
    _attr_native_unit_of_measurement = UnitOfTime.SECONDS
    _attr_mode = NumberMode.BOX
    _attr_icon = "mdi:timer-sand"
    _attr_name = "CloudEdge video stall timeout"

    def __init__(self, coordinator, entry_id: str) -> None:
        """Initialize the stall timeout knob."""
        super().__init__(coordinator)
        self._value = VIDEO_STALL_TIMEOUT_DEFAULT
        self._attr_unique_id = f"{entry_id}_video_stall_timeout"

    async def async_added_to_hass(self) -> None:
        """Restore the tuned value and apply it to the library."""
        await super().async_added_to_hass()

        last_state = await self.async_get_last_state()
        if last_state is not None:
            try:
                self._value = min(
                    VIDEO_STALL_TIMEOUT_MAX,
                    max(VIDEO_STALL_TIMEOUT_MIN, float(last_state.state)),
                )
            except (TypeError, ValueError):
                # unknown/unavailable after a restart: keep the default
                pass

        apply_video_stall_timeout(self._value)

    @property
    def native_value(self) -> float:
        """Return the current stall timeout in seconds."""
        return self._value

    async def async_set_native_value(self, value: float) -> None:
        """Store and apply a new stall timeout."""
        self._value = value
        apply_video_stall_timeout(value)
        _LOGGER.debug("Video stall timeout set to %ss", value)
        self.async_write_ha_state()


class CloudEdgeReconnectCooldownNumber(CoordinatorEntity, RestoreEntity, NumberEntity):
    """How long to wait before opening a fresh live window.

    The camera rate-limits back-to-back sessions: reconnect too soon and the
    next window produces no video at all, which costs more time than it saves.
    Eight seconds was measured as always-safe, but that is an upper bound rather
    than the real limit, and the real limit is what this knob is for.
    """

    _attr_entity_category = EntityCategory.CONFIG
    _attr_native_min_value = RECONNECT_COOLDOWN_MIN
    _attr_native_max_value = RECONNECT_COOLDOWN_MAX
    _attr_native_step = 0.5
    _attr_native_unit_of_measurement = UnitOfTime.SECONDS
    _attr_mode = NumberMode.BOX
    _attr_icon = "mdi:timer-refresh"
    _attr_name = "CloudEdge reconnect cooldown"

    def __init__(self, coordinator, entry_id: str) -> None:
        """Initialize the reconnect cooldown knob."""
        super().__init__(coordinator)
        self._value = RECONNECT_COOLDOWN_DEFAULT
        self._attr_unique_id = f"{entry_id}_reconnect_cooldown"

    async def async_added_to_hass(self) -> None:
        """Restore the tuned value and publish it for the stream bridge."""
        await super().async_added_to_hass()

        last_state = await self.async_get_last_state()
        if last_state is not None:
            try:
                self._value = min(
                    RECONNECT_COOLDOWN_MAX,
                    max(RECONNECT_COOLDOWN_MIN, float(last_state.state)),
                )
            except (TypeError, ValueError):
                pass

        RECONNECT_COOLDOWN["value"] = self._value

    @property
    def native_value(self) -> float:
        """Return the current cooldown in seconds."""
        return self._value

    async def async_set_native_value(self, value: float) -> None:
        """Store and publish a new cooldown."""
        self._value = value
        RECONNECT_COOLDOWN["value"] = value
        _LOGGER.debug("Reconnect cooldown set to %ss", value)
        self.async_write_ha_state()
