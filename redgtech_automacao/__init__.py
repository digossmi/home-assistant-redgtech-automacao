from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import RedgtechCoordinator

PLATFORMS = ["sensor", "switch"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})
    
    coordinators = []
    for board in entry.data["boards"]:
        coordinator = RedgtechCoordinator(hass, board)
        await coordinator.async_config_entry_first_refresh()
        coordinators.append(coordinator)
    
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinators": coordinators,
        "boards": entry.data["boards"]
    }
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        coordinators = hass.data[DOMAIN][entry.entry_id]["coordinators"]
        for coordinator in coordinators:
            await coordinator.async_shutdown()
        
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok
