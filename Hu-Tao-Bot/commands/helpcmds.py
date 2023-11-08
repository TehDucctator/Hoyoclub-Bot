import discord
from discord.ext import commands

class HelpCmds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="help")
    async def help(self, ctx):
        embed = discord.Embed(title="Commands", description="List of commands and what they do")
        embed.add_field(name="help", value="This command! Shows all commands")

        cmd_list = ["join - Join the list of streamers in the current channel",
                    "leave - Leave the list of streamers in the current channel",
                    "show - (or just \"stream\") Shows the list of streamers in the current channel"]

        embed.add_field(name="stream...", value=" - stream " + "\n- stream ".join(cmd_list), inline=False)
        
        exec_stream_list = ["next - Moves onto the next streamer in the list",
                     "create - Creates an empty list of streamers for the current channel (one per channel)",
                     "end - Ends the list of streamers for the current channel",
                     "add - Add a member to the list of streamers",
                     "remove - Remove a member from the list of streamers"]

        embed.add_field(name="stream...", value=" - stream " + "\n- stream ".join(exec_stream_list), inline=False)

        exec_attendance = ["show - shows list of attendees, past and present, in specified or current vc of caller, with their total time",
                           "create - (Exec only) creates attendance tracker for specified or current vc of caller"
                           "end - (Exec only) ends attendance tracker for specified or current vc of caller"]
        
        embed.add_field(name="attendance...", value=" - attendance " + "\n- attendance ".join(exec_attendance), inline=False)

        await ctx.send(embed=embed)
    
async def setup(client):
    await client.add_cog(HelpCmds(client))