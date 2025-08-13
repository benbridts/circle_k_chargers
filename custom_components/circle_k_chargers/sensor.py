from __future__ import annotations

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .lib import get_chargers
from .models import PUBLIC_OPERATOR_IDS


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the sensor platform."""
    add_entities([BestAvailableChargerSensor(hass)])


class BestAvailableChargerSensor(SensorEntity):
    _attr_name = "Best Available Charger"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, hass: HomeAssistant):
        self.latitude = hass.config.latitude
        self.longitude = hass.config.longitude

    def update(self) -> None:
        locale = "BE_nl"
        distance = 500
        excluded_evses = set()
        for charger in get_chargers(
            locale,
            self.latitude,
            self.longitude,
            distance,
            operators=PUBLIC_OPERATOR_IDS,
            excluded_evses=excluded_evses,
        ):
            if charger.num_available >= 1:
                self._attr_native_value = charger.name
                self._attr_extra_state_attributes = charger.to_dict()
                # do not look at other chargers
                return
