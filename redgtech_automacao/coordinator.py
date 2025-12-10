from datetime import timedelta
import aiohttp
import asyncio
import logging

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_BOARD_IP, CONF_BOARD_IP_SECONDARY, CONF_BOARD_NAME, CONF_NUM_CHANNELS

_LOGGER = logging.getLogger(__name__)


class RedgtechCoordinator(DataUpdateCoordinator):
    
    def __init__(self, hass: HomeAssistant, board_config: dict):
        self.board_config = board_config
        self.board_ip = board_config[CONF_BOARD_IP]
        self.board_ip_secondary = board_config.get(CONF_BOARD_IP_SECONDARY, "")
        self.board_name = board_config[CONF_BOARD_NAME]
        self.num_channels = board_config.get(CONF_NUM_CHANNELS, 16)
        self._session = None
        self._request_lock = asyncio.Lock()
        self._current_ip = self.board_ip
        self._failed_primary_count = 0
        
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{self.board_name}",
            update_interval=timedelta(seconds=60),
        )
    
    async def _get_session(self):
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=5)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session
    
    async def _try_ip(self, ip: str) -> dict:
        session = await self._get_session()
        async with session.get(f"http://{ip}/L") as response:
            if response.status != 200:
                raise UpdateFailed(f"HTTP {response.status}")
            return await response.json(content_type=None)
    
    async def _send_restart_command(self, ip: str) -> bool:
        try:
            session = await self._get_session()
            async with session.get(f"http://{ip}/L?restart") as response:
                success = response.status == 200
                if success:
                    _LOGGER.warning(
                        f"Comando RESTART enviado para {self.board_name} via {ip}"
                    )
                return success
        except Exception as err:
            _LOGGER.error(f"Erro ao enviar restart: {err}")
            return False
    
    async def _async_update_data(self):
        async with self._request_lock:
            try:
                data = await self._try_ip(self.board_ip)
                
                if self._current_ip != self.board_ip:
                    _LOGGER.info(
                        f"{self.board_name} voltou para IP primário {self.board_ip}"
                    )
                self._current_ip = self.board_ip
                self._failed_primary_count = 0
                return data
                
            except Exception as primary_err:
                self._failed_primary_count += 1
                _LOGGER.warning(
                    f"Falha no IP primário {self.board_ip} ({self._failed_primary_count}x): {primary_err}"
                )
                
                if self.board_ip_secondary:
                    try:
                        data = await self._try_ip(self.board_ip_secondary)
                        
                        if self._current_ip != self.board_ip_secondary:
                            _LOGGER.warning(
                                f"⚠️ {self.board_name} está no IP secundário (WiFi) {self.board_ip_secondary}"
                            )
                        
                        self._current_ip = self.board_ip_secondary
                        
                        if self._failed_primary_count >= 2:
                            _LOGGER.warning(
                                f"🔄 Auto-recovery: enviando restart para {self.board_name} "
                                f"voltar ao IP primário (cabo)"
                            )
                            await self._send_restart_command(self.board_ip_secondary)
                            self._failed_primary_count = 0
                            await asyncio.sleep(5)
                        
                        return data
                        
                    except Exception as secondary_err:
                        _LOGGER.error(
                            f"Falha em ambos IPs para {self.board_name}: "
                            f"Primário: {primary_err}, Secundário: {secondary_err}"
                        )
                        raise UpdateFailed(
                            f"Placa inacessível em {self.board_ip} e {self.board_ip_secondary}"
                        )
                else:
                    raise UpdateFailed(f"Erro ao conectar em {self.board_ip}: {primary_err}")
    
    async def send_command(self, switch_id: int, state: str) -> bool:
        async with self._request_lock:
            command_url = f"http://{self._current_ip}/L?{switch_id}{state}"
            try:
                session = await self._get_session()
                async with session.get(command_url) as response:
                    success = response.status == 200
                    if success:
                        _LOGGER.info(
                            f"Comando enviado via {self._current_ip}: "
                            f"Canal {switch_id} -> {state} ({self.board_name})"
                        )
                    else:
                        _LOGGER.warning(
                            f"Falha no comando via {self._current_ip}: "
                            f"Status {response.status}"
                        )
                    return success
            except Exception as err:
                _LOGGER.error(f"Erro ao enviar comando via {self._current_ip}: {err}")
                return False
    
    async def async_shutdown(self):
        if self._session and not self._session.closed:
            await self._session.close()
