import os, random
import discord
from discord.ext import tasks, commands

intents = discord.Intents.default()
intents.message_content = True

class MyBot(commands.Bot):
    async def setup_hook(self):
        cog_files = ['autoresponder.responder']

        for cog_file in cog_files:
            await client.load_extension(cog_file)
            print(f"{cog_file} loaded")

client = MyBot(command_prefix="ht!", intents=intents)

status = ["with coffins", "with Qiqi", "with fire, shh", "with ghosts", "with Boo Tao"] # statuses to go through

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    change_status.start() # start loop to change status

@tasks.loop(minutes=10, count=len(status)) # changes status every 10 minutes
async def change_status():
    await client.change_presence(activity=discord.Game(status[change_status.current_loop]))

@change_status.after_loop
async def restart_status(): # restart change_status
    change_status.restart()


if __name__ == "__main__":
    client.run(os.getenv('TOKEN'))