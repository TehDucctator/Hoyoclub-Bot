import random
import discord
from discord.ext import commands

import autoresponder.responses as responses

class Autoresponder(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot: # prevents reading bot messages
            return

        if message.channel.name == "announcements": # prevents responding in announcements
            return

        text = message.content.lower() # gets lowered message content
        if text.startswith(responses.gm_messages): # checks for good mornings
            await message.channel.send(random.choice(responses.gm_responses)) # responds with a gm

        if text.startswith(responses.gn_messages): # checks for good nights
            await message.channel.send(random.choice(responses.gn_responses)) # responds with a gn

async def setup(client):
    await client.add_cog(Autoresponder(client))