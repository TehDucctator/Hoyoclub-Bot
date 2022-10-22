import os, random
import discord
from discord.ext import tasks
import responses

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

status = iter(["with coffins", "with Qiqi", "with fire, shh"]) # statuses to go through
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    change_status.start() # start loop to change status

@tasks.loop(minutes=10) # changes status every 10 minutes
async def change_status():
    await client.change_presence(activity=discord.Game(next(status)))

@client.event
async def on_message(message):
    if message.author == client.user: # prevents reading its own messages
        return

    text = message.content.lower() # gets lowered message content
    if text.startswith(responses.gm_messages): # checks for good mornings
        await message.channel.send(random.choice(responses.gm_responses)) # responds with a gm

client.run(os.getenv('TOKEN'))