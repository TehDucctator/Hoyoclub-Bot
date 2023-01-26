from discord.ext import commands

import autoresponder.responses as responses

class Autoresponder(commands.Cog):
    def __init__(self):
        pass

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot: # prevents reading bot messages
            return

        if message.channel.name == "announcements": # prevents responding in announcements
            return

        text = message.content.lower() # gets lowered message content
        response = responses.get_response(text) # get response to text
        if response: # send response if text is a trigger
            await message.channel.send(response) 

async def setup(client):
    await client.add_cog(Autoresponder())