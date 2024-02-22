import discord
from discord.ext import commands

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from utils.buttons import ConfirmButtonView

class Attendee():
    def __init__(self, member, join_time : datetime) -> None:
        self.member = member
        self.time = timedelta()
        self.original_join_time = join_time
        self.recent_join_time = join_time

        self.active = True
        self.last_update : datetime = join_time

    def update_time(self):
        if self.active:
            self.time += datetime.now(tz=ZoneInfo("America/New_York")) - self.last_update
        
        self.last_update = datetime.now(tz=ZoneInfo("America/New_York"))

    def on_leave(self):
        self.update_time()
        self.active = False
    
    def on_join(self):
        self.active = True
        self.last_update = datetime.now(tz=ZoneInfo("America/New_York"))

class Event():
    def __init__(self, voice_channel) -> None:
        self.voice_channel = voice_channel
        self.attendees = set()
        self.start_time = datetime.now(tz=ZoneInfo("America/New_York"))

    def add_attendee(self, attendee) -> None:
        self.attendees.add(attendee)

    def update_times(self):
        for attendee in self.attendees:
            attendee.update_time()

    def get_attendee_from_member(self, member):
        return [attendee for attendee in self.attendees if attendee.member == member][0]

class AttendanceTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.events = set()

    def get_event_from_id(self, channel_id : int):
        """iterates through events and finds the one with matching voice channel"""
        return [event for event in self.events if event.voice_channel == channel_id][0]
    
    def get_channel_id(self, ctx, channel_mention : str = None) -> int:
        """identifies desired vc"""
        if channel_mention == None:
            if ctx.author.voice == None: # author not in vc
                raise AttributeError
            
            channel_id = ctx.author.voice.channel.id
        else:
            if channel_mention[0:1] != "<#" and channel_mention[-1] != ">": # vc not mentioned properly
                raise ValueError
            
            channel_id = int(channel_mention[2:len(channel_mention)-1]) # get only id

        return channel_id

    @commands.hybrid_group(name="attendance", fallback="show")
    async def tracker(self, ctx, channel_mention : str = None):
        """Display present and past attendees of current or specified **tracked** vc"""
        try:
            event = self.get_event_from_id(channel := self.get_channel_id(ctx, channel_mention))
        except AttributeError:
            await ctx.send(f"{ctx.author.mention} Please join or mention a vc!")
            return
        except ValueError:
            await ctx.send(f"{ctx.author.mention} Please mention the vc by doing `<#CHANNEL ID>`!")
            return
        except IndexError:
            await ctx.send(f"{ctx.author.mention} No attendance tracker could be found for <#{channel}>!")
            return
        
        event.update_times()
        embed = discord.Embed(title=f"Attendees (<#{channel}>):", 
                              description=f"Start time: {event.start_time.strftime('%m/%d, %I:%M%p')}", 
                              color=discord.Color.random())
        attendees = ""
        inactive = ""

        for attendee in event.attendees:
            if attendee.active:
                attendees += f"<@{attendee.member.id}> (Total: {str(attendee.time).split('.')[0]})\n"
            else:
                inactive += f"<@{attendee.member.id}> (Total: {str(attendee.time).split('.')[0]})\n"

        embed.add_field(name="In VC", value=attendees, inline=False)
        embed.add_field(name="Left VC", value=inactive, inline=False)
        
        footer = "Total time may be inaccurate. Please compare with previous attendance messages and their timestamps if needed"
        embed.set_footer(text=footer)
        
        await ctx.send(embed=embed)

    @tracker.command(name="snapshot")
    async def vc_snapshot(self, ctx, channel_mention : str = None):
        """Display current members in specified or current vc"""
        try:
            channel_id = self.get_channel_id(ctx, channel_mention)
        except AttributeError:
            await ctx.send(f"{ctx.author.mention} Please join or mention a vc!")
            return
        except ValueError:
            await ctx.send(f"{ctx.author.mention} Please mention the vc by doing `<#CHANNEL ID>`!")
            return
        
        embed = discord.Embed(title=f"Attendees (<#{channel_id}>):", 
                              description=f"Time: {datetime.now(tz=ZoneInfo('America/New_York')).strftime('%m/%d, %I:%M%p')}", 
                              color=discord.Color.random())
        attendees = ""

        # Mentions members already connected to vc
        voice = self.bot.get_channel(channel_id)
        for user_id in voice.voice_states.keys():
            attendees += f"<@{user_id}>\n"

        embed.add_field(name="In VC", value=attendees, inline=False)

        await ctx.send(embed=embed)
    
    @tracker.command(name="start")
    @commands.has_role("Fatui")
    async def event_create(self, ctx, channel_mention : str = None) -> None:
        """Adds current or specified vc for tracking"""
        # identifies desired vc
        try:
            channel_id = self.get_channel_id(ctx, channel_mention=channel_mention)
        except AttributeError:
            await ctx.send(f"{ctx.author.mention} Please join or mention a vc to track!")
            return
        except ValueError:
            await ctx.send(f"{ctx.author.mention} Please mention the vc to track by doing `<#CHANNEL ID>`!")
            return

        # check for already tracked, add if not
        if channel_id in set([event.voice_channel for event in self.events]):
            await ctx.send(f"{ctx.author.mention} Attendance is already being tracked for <#{channel_id}>")
            return
            
        event = Event(voice_channel=int(channel_id))
        self.events.add(event)
        await ctx.send(f"Attendance tracker started for <#{channel_id}>!")
        
        # adds members already connected to vc
        voice = self.bot.get_channel(channel_id)
        for id in voice.voice_states.keys():
            event.add_attendee(Attendee(voice.guild.get_member(id), datetime.now(tz=ZoneInfo("America/New_York"))))

    @tracker.command(name="end")
    @commands.has_role("Fatui")
    async def event_end(self, ctx, channel_mention : str = None) -> None:
        """Ends tracking for specified or current vc"""
        # identifies desired vc
        try:
            channel_id = self.get_channel_id(ctx, channel_mention=channel_mention)
        except AttributeError:
            await ctx.send(f"{ctx.author.mention} Please join or mention a vc to stop tracking!")
            return
        except ValueError:
            await ctx.send(f"{ctx.author.mention} Please mention the vc to stop tracking by doing `<#CHANNEL ID>`!")
            return

        # check if vc is tracked
        if not channel_id in set([event.voice_channel for event in self.events]):
            await ctx.send(f"{ctx.author.mention} There is no event being tracked in <#{channel_id}>!")
            return
            
        # confirm end tracker
        confirmation_buttons = ConfirmButtonView(author=ctx.author, timeout=10)
        message = await ctx.send(f"Are you sure you want to end the attendance tracker for <#{channel_id}>?", view=confirmation_buttons)
        confirmation_buttons.message = message
        await confirmation_buttons.wait()
        await confirmation_buttons.disable_all_items()

        if confirmation_buttons.confirmed == True:
            # sends final attendance + iterates through events to find and remove the one with matching voice channel
            await ctx.invoke(self.bot.get_command("attendance"), channel_mention=f"<#{channel_id}>")
            self.events.remove(self.get_event_from_id(channel_id=channel_id))
            await ctx.send(f"Attendance tracker ended for <#{channel_id}>!")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Updates status of attendees"""
        # update attendee object upon joining or leaving the channel
        if not before.channel is after.channel: 
            # joined channel with tracking
            if after.channel != None and after.channel.id in [event.voice_channel for event in self.events]:
                event = self.get_event_from_id(after.channel.id)
                
                try: # check for existing attendee object
                    attendee = event.get_attendee_from_member(member)

                    if not attendee.active:
                        attendee.on_join()

                except IndexError: # create new attendee object if new
                    event.add_attendee(Attendee(member, datetime.now(tz=ZoneInfo("America/New_York"))))
            
            # left channel with tracking
            elif before.channel != None and before.channel.id in [event.voice_channel for event in self.events]:
                event = self.get_event_from_id(before.channel.id)
                
                try: # find existing attendee object
                    attendee = event.get_attendee_from_member(member)

                    if attendee.active:
                        attendee.on_leave()

                except IndexError:
                    pass
            
    @event_create.error
    @event_end.error
    async def exec_cmd_error(self, ctx, error):
        print(error)
        if "Fatui" in str(error):
            await ctx.send("Only execs can do this")
        else:
            await ctx.send("An error occured :/")

async def setup(client):
    await client.add_cog(AttendanceTracker(client))