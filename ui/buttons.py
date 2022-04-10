from discord import ButtonStyle, Interaction, ui
from discord.ui import View, Button

from log import log


class Confirm(View):
    def __init__(self,
                 conf_msg: str = "Confirming...",
                 canc_msg: str = "Cancelling...",
                 timeout: float = 180.0
                 ) -> None:
        super().__init__(timeout=timeout)
        self.conf_msg = conf_msg
        self.canc_msg = canc_msg
        self.value = None

    @ui.button(label='Confirm', style=ButtonStyle.green)
    async def confirm(self, interaction: Interaction, button: Button):
        await interaction.response.edit_message(content=self.conf_msg, view=None)
        self.value = True
        self.stop()

    @ui.button(label='Cancel', style=ButtonStyle.grey)
    async def cancel(self, interaction: Interaction, button: Button):
        await interaction.response.edit_message(content=self.canc_msg, view=None)
        self.value = False
        self.stop()

    async def on_timeout(self) -> None:
        log.debug("Timeout")

