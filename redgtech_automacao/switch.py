import asyncio
import logging
import time

from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinators = hass.data[DOMAIN][entry.entry_id]["coordinators"]
    
    switches = []
    for coordinator in coordinators:
        num_channels = coordinator.num_channels
        for switch_id in range(1, num_channels + 1):
            switches.append(
                RedgtechSwitch(
                    coordinator=coordinator,
                    switch_id=switch_id,
                )
            )
    
    async_add_entities(switches)


class RedgtechSwitch(CoordinatorEntity, SwitchEntity):

    def __init__(self, coordinator, switch_id: int):
        super().__init__(coordinator)
        self._coordinator = coordinator
        self._switch_id = switch_id
        self._attr_unique_id = f"{DOMAIN}_{coordinator.board_name}_switch_{switch_id}"
        self._attr_has_entity_name = True
        self._last_command_time = 0
        self._optimistic_state = None
        self._optimistic_until = 0

    @property
    def name(self):
        if self.coordinator.data:
            friendly_name_key = f"Nm_{self._switch_id}"
            friendly_name = self.coordinator.data.get(friendly_name_key)
            if friendly_name and friendly_name.strip():
                return friendly_name
        
        return f"Canal {self._switch_id}"

    @property
    def is_on(self):
        now = time.time()
        if self._optimistic_state is not None and now < self._optimistic_until:
            return self._optimistic_state
        
        if self._optimistic_state is not None and now >= self._optimistic_until:
            self._optimistic_state = None
        
        if not self.coordinator.data:
            return False
        
        state_key = f"AC{self._switch_id}"
        state = self.coordinator.data.get(state_key)
        return state == "1"

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

    def _handle_coordinator_update(self) -> None:
        now = time.time()
        if self._optimistic_state is not None and now < self._optimistic_until:
            _LOGGER.debug(
                f"Ignorando update do coordinator para {self.name} (modo otimista ativo)"
            )
            return
        
        super()._handle_coordinator_update()

    async def async_turn_on(self, **kwargs):
        now = time.time()
        
        if now - self._last_command_time < 1.0:
            _LOGGER.debug(f"Comando duplicado ignorado para {self.name}")
            return
        
        self._last_command_time = now
        self._optimistic_state = True
        self._optimistic_until = now + 5.0
        self.async_write_ha_state()
        
        _LOGGER.info(f"Ligando {self.name} (modo otimista por 5s)")
        
        success = await self._coordinator.send_command(self._switch_id, "l")
        
        if not success:
            self._optimistic_state = None
            self._optimistic_until = 0
            self.async_write_ha_state()
            _LOGGER.warning(f"Falha ao ligar {self.name}")

    async def async_turn_off(self, **kwargs):
        now = time.time()
        
        if now - self._last_command_time < 1.0:
            _LOGGER.debug(f"Comando duplicado ignorado para {self.name}")
            return
        
        self._last_command_time = now
        self._optimistic_state = False
        self._optimistic_until = now + 5.0
        self.async_write_ha_state()
        
        _LOGGER.info(f"Desligando {self.name} (modo otimista por 5s)")
        
        success = await self._coordinator.send_command(self._switch_id, "d")
        
        if not success:
            self._optimistic_state = None
            self._optimistic_until = 0
            self.async_write_ha_state()
            _LOGGER.warning(f"Falha ao desligar {self.name}")
