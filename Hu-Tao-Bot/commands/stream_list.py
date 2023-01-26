import discord
from discord.ext import commands

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
    async def End(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.author.id:
            self.confirmed = True
            await self.disable_all_items()
            await interaction.response.edit_message(content="Confirmed", view=self)
            self.stop()


class StreamList(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queues = []

    class Queue():
        def __init__(self, channel, q=[]) -> None:
            self.channel = channel
            self.q = q
            self.current = 0

        def next(self) -> bool:
            self.q[self.current][1] = True
            self.current += 1
            try:
                self.q[self.current]
                return True
            except IndexError:
                self.current -= 1
                return False



    def find_stream_list(self, ctx):
        for i, q in enumerate(self.queues):
            if ctx.channel.id == q.channel:
                return i
        return None

    @commands.hybrid_group(name="stream", fallback="show")
    async def stream(self, ctx):
        embed = discord.Embed(title=f"List of Streamers (current pos: {self.queues[self.find_stream_list(ctx)].current})")
        index = self.find_stream_list(ctx)
        if index == None:
            await ctx.send("Could not find a list in this channel")
        else:
            streamers = ""
            for i, streamer in enumerate(self.queues[index].q):
                streamers += f"{i+1}. {streamer[0].mention}, status: {'streamed' if streamer[1] else 'waiting'}\n"

            embed.add_field(name="", value=streamers)
            await ctx.send(embed=embed)

    @stream.command(name="create")
    @commands.has_role("Executives")
    async def create_stream(self, ctx):
        if ctx.channel.id in [q.channel for q in self.queues]:
            await ctx.send("There is already a stream going on")
        else:
            new = self.Queue(channel=ctx.channel.id)
            self.queues.append(new)
            await ctx.send("stream created")

    @stream.command(name="end")
    @commands.has_role("Executives")
    async def end_stream(self, ctx):
        index = None
        for i, id in enumerate([q.channel for q in self.queues]):
            if ctx.channel.id == id:
                index = i
                break
        else:
            await ctx.send("There is no stream list for this channel")

        if index != None:
            confirmation_buttons = ConfirmButtonView(author=ctx.author, timeout=10)
            message = await ctx.send("Are you sure you want to end the stream list?", view=confirmation_buttons)
            confirmation_buttons.message = message
            await confirmation_buttons.wait()
            await confirmation_buttons.disable_all_items()

            if confirmation_buttons.confirmed == True:
                self.queues.pop(index)
                await ctx.send("Stream list ended")


    @stream.command(name="join")
    async def join(self, ctx):
        index = self.find_stream_list(ctx)
        if index == None:
            await ctx.send("Could not find a list in this channel")
        else:
            if not ctx.author in self.queues[index].q:
                self.queues[index].q.append([ctx.author, False])
                await ctx.send("You have successfully joined")
            else:
                await ctx.send("You have already joined")

    @stream.command(name="leave")
    async def leave(self, ctx):
        index = self.find_stream_list(ctx)
        if index == None:
            await ctx.send("Could not find a list in this channel")
        else:
            for i, s in enumerate(self.queues[index].q):
                if ctx.author == s[0]:
                    if s[1] == False:
                        self.queues[index].q.pop(i)
                        await ctx.send("You have successfully left")
                    else:
                        await ctx.send("You have already streamed, unfortunately I cannot let you leave to let execs keep track of streamers")
                    
                    break
            else:
                await ctx.send("You are not on the list")

    @stream.command(name="next")
    @commands.has_role("Executives")
    async def next(self, ctx):
        index = self.find_stream_list(ctx)
        if index == None:
            await ctx.send("Could not find a list in this channel")
        else:
            if self.queues[index].next():
                l = self.queues[index]
                await ctx.send(f"{l.q[l.current][0].mention} is up next!")
            else:
                await ctx.send("No one is next")

    @stream.command(name="add")
    @commands.has_role("Executives")
    async def add(self, ctx, user):
        index = self.find_stream_list(ctx)
        if index == None:
            await ctx.send("Could not find a list in this channel")
        else:
            self.queues[index].q.append([await ctx.bot.fetch_user(int(user[2:len(user)-1])), False])
            await ctx.send(f"{user} added")

    @stream.command(name="remove")
    @commands.has_role("Executives")
    async def remove(self, ctx, position):
        index = self.find_stream_list(ctx)
        if index == None:
            await ctx.send("Could not find a list in this channel")
        else:
            await ctx.send(f"Removing position {position}: {self.queues[index].q[int(position)-1][0].mention}")
            self.queues[index].q.pop(int(position)-1)
            if self.queues[index].current > int(position)-1:
                self.queues[index].current -= 1

    @end_stream.error
    @create_stream.error
    @next.error
    @add.error
    @remove.error
    async def not_exec_error(self, ctx, error):
        print(error)
        await ctx.send("Only execs can do this")


async def setup(client):
    await client.add_cog(StreamList(client))