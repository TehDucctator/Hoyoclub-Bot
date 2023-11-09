import discord

class ConfirmButtonView(discord.ui.View):
    def __init__(self, author, timeout: float = 180):
        self.author = author
        super().__init__(timeout=timeout)

    confirmed : bool = None

    async def disable_all_items(self):
        for item in self.children:
            item.disabled = True

    async def on_timeout(self) -> None:
        await self.disable_all_items()
        await self.message.edit(content="Timed out", view=self)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.grey)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.author.id:
            self.confirmed = False
            await self.disable_all_items()
            await interaction.response.edit_message(content="Canceled", view=self)
            self.stop()

    @discord.ui.button(label="End", style=discord.ButtonStyle.red)
    async def end(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.author.id:
            self.confirmed = True
            await self.disable_all_items()
            await interaction.response.edit_message(content=self.message.content + "\n**Confirmed**", view=self)
            self.stop()