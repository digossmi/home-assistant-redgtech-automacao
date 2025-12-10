import voluptuous as vol
import aiohttp

from homeassistant import config_entries

from .const import (
    DOMAIN,
    CONF_NUM_BOARDS,
    CONF_BOARD_IP,
    CONF_BOARD_IP_SECONDARY,
    CONF_BOARD_NAME,
    CONF_NUM_CHANNELS
)


class RedgtechAutomacaoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    
    VERSION = 1
    
    def __init__(self):
        self.num_boards = 1
        self.boards_config = []
        self.current_board = 0
    
    async def async_step_user(self, user_input=None):
        errors = {}
        
        if user_input is not None:
            self.num_boards = user_input[CONF_NUM_BOARDS]
            self.boards_config = []
            self.current_board = 0
            return await self.async_step_board_config()
        
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_NUM_BOARDS, default=1): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=10)
                )
            }),
            errors=errors,
            description_placeholders={
                "step": "Configuração Inicial - Redgtech Automação"
            }
        )
    
    async def async_step_board_config(self, user_input=None):
        errors = {}
        
        if user_input is not None:
            try:
                timeout = aiohttp.ClientTimeout(total=5)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get(
                        f"http://{user_input[CONF_BOARD_IP]}/L"
                    ) as response:
                        if response.status != 200:
                            errors["base"] = "cannot_connect"
            except:
                errors["base"] = "cannot_connect"
            
            if not errors:
                self.boards_config.append(user_input)
                self.current_board += 1
                
                if self.current_board >= self.num_boards:
                    return self.async_create_entry(
                        title=f"Redgtech Automação ({self.num_boards} placa{'s' if self.num_boards > 1 else ''})",
                        data={
                            CONF_NUM_BOARDS: self.num_boards,
                            "boards": self.boards_config
                        }
                    )
                return await self.async_step_board_config()
        
        return self.async_show_form(
            step_id="board_config",
            data_schema=vol.Schema({
                vol.Required(CONF_BOARD_NAME, default=f"Placa {self.current_board + 1}"): str,
                vol.Required(CONF_BOARD_IP): str,
                vol.Optional(CONF_BOARD_IP_SECONDARY, default=""): str,
                vol.Required(CONF_NUM_CHANNELS, default=16): vol.In([8, 16, 32]),
            }),
            errors=errors,
            description_placeholders={
                "board_number": str(self.current_board + 1),
                "total_boards": str(self.num_boards)
            }
        )
