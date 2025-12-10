from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinators = hass.data[DOMAIN][entry.entry_id]["coordinators"]
    
    sensors = []
    for coordinator in coordinators:
        sensors.append(RedgtechSensor(coordinator))
    
    async_add_entities(sensors)


class RedgtechSensor(CoordinatorEntity, SensorEntity):

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._coordinator = coordinator
        self._attr_name = f"Estado {coordinator.board_name}"
        self._attr_unique_id = f"{DOMAIN}_{coordinator.board_name}_state"
        self._attr_has_entity_name = True

    @property
    def name(self):
        return self._attr_name

    @property
    def state(self):
        if self.coordinator.data:
            return self.coordinator.data.get("success")
        return None

    @property
    def extra_state_attributes(self):
        if not self.coordinator.data:
            return {}
        
        attributes = {}
        for key, value in self.coordinator.data.items():
            if key.startswith("AC") or key.startswith("Nm"):
                attributes[key] = value
        
        return attributes

    @property
    def available(self):
        return self.coordinator.last_update_success

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._coordinator.board_name)},
            "name": self._coordinator.board_name,
            "manufacturer": "Redgtech",
            "model": f"Placa {self._coordinator.num_channels} Canais",
        }
