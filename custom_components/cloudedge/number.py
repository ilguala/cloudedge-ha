"""
CloudEdge number platform.

Two tuning knobs, neither of which writes anything to the camera:

* PTZ step duration, per camera. The protocol fixes the motor speed, so the only
  thing that decides how far a button press moves the camera is how long the
  motor is held.
* KCP receive window, per account. How large a burst a camera may have in flight
  before waiting for acknowledgements — the setting that decides whether frames
  arrive whole, and how many of them arrive.
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
    KCP_RECEIVE_WINDOW,
    STREAM_QUALITY,
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

    entities: list[NumberEntity] = [
        CloudEdgePtzStepNumber(coordinator, device_sn, device_data)
        for device_sn, device_data in coordinator.data.items()
    ]

    # One per account, not per camera: the KCP window is a module-level setting
    # in the library, shared by every stream.
    entities.append(CloudEdgeKcpWindowNumber(coordinator, config_entry.entry_id))
    entities.append(CloudEdgeStreamQualityNumber(coordinator, config_entry.entry_id))

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


class CloudEdgeKcpWindowNumber(CoordinatorEntity, RestoreEntity, NumberEntity):
    """KCP receive window advertised to the cameras.

    This is the size of the burst a camera is allowed to have in flight before
    waiting for acknowledgements. Too large and it floods this side, the socket
    drops the surplus and frames arrive mangled; too small and it throttles the
    camera down to a couple of frames per second. The right value depends on the
    path (LAN vs the vendor's relay) and on how fast the host keeps up, so it is
    exposed rather than hardcoded.

    Takes effect on the next stream session, not on the one already running.
    """

    _attr_entity_category = EntityCategory.CONFIG
    _attr_native_min_value = 32
    _attr_native_max_value = 4096
    _attr_native_step = 32
    _attr_mode = NumberMode.BOX
    _attr_icon = "mdi:tune-variant"
    _attr_name = "CloudEdge KCP receive window"

    def __init__(self, coordinator, entry_id: str) -> None:
        """Initialize the KCP window knob."""
        super().__init__(coordinator)
        self._value = float(KCP_RECEIVE_WINDOW)
        self._attr_unique_id = f"{entry_id}_kcp_receive_window"

    async def async_added_to_hass(self) -> None:
        """Restore the tuned value and apply it to the library."""
        await super().async_added_to_hass()

        last_state = await self.async_get_last_state()
        if last_state is not None:
            try:
                self._value = min(4096.0, max(32.0, float(last_state.state)))
            except (TypeError, ValueError):
                pass

        self._apply(self._value)

    def _apply(self, value: float) -> None:
        """Write the window into the library, if it still lives there."""
        try:
            from cloudedge.p2p import kcp_tunnel
        except ImportError:
            _LOGGER.error("Cannot apply KCP window: library not importable")
            return

        if not hasattr(kcp_tunnel, "KCP_WND"):
            _LOGGER.error(
                "Cannot apply KCP window: KCP_WND is gone from "
                "cloudedge.p2p.kcp_tunnel"
            )
            return

        kcp_tunnel.KCP_WND = int(value)
        _LOGGER.debug("KCP receive window set to %s", int(value))

    @property
    def native_value(self) -> float:
        """Return the current window size in segments."""
        return self._value

    async def async_set_native_value(self, value: float) -> None:
        """Store and apply a new window size."""
        self._value = value
        self._apply(value)
        self.async_write_ha_state()


class CloudEdgeStreamQualityNumber(CoordinatorEntity, RestoreEntity, NumberEntity):
    """Quality requested in the VVP start-live packet.

    The library never sets this byte, so every session asks the camera for
    quality 0 and gets roughly 10 kbps, where the vendor app pulls about 1 Mbps
    from the same camera. The meaning of the values is not documented anywhere:
    they have to be tried, which is why this is a knob and not a constant.

    Takes effect on the next stream session.
    """

    _attr_entity_category = EntityCategory.CONFIG
    _attr_native_min_value = 0
    _attr_native_max_value = 3
    _attr_native_step = 1
    _attr_mode = NumberMode.BOX
    _attr_icon = "mdi:video-high-definition"
    _attr_name = "CloudEdge stream quality"

    def __init__(self, coordinator, entry_id: str) -> None:
        """Initialize the stream quality knob."""
        super().__init__(coordinator)
        self._value = float(STREAM_QUALITY["value"])
        self._attr_unique_id = f"{entry_id}_stream_quality"

    async def async_added_to_hass(self) -> None:
        """Restore the chosen value and apply it."""
        await super().async_added_to_hass()

        last_state = await self.async_get_last_state()
        if last_state is not None:
            try:
                self._value = min(3.0, max(0.0, float(last_state.state)))
            except (TypeError, ValueError):
                pass

        STREAM_QUALITY["value"] = int(self._value)

    @property
    def native_value(self) -> float:
        """Return the quality value currently requested."""
        return self._value

    async def async_set_native_value(self, value: float) -> None:
        """Store and apply a new quality value."""
        self._value = value
        STREAM_QUALITY["value"] = int(value)
        _LOGGER.debug("VVP start-live quality set to %s", int(value))
        self.async_write_ha_state()
