import discord
from discord.ext import commands

from datetime import datetime, timedelta, timezone

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
            self.time += datetime.now(tz=timezone.utc) - self.last_update
            self.last_update = datetime.now(tz=timezone.utc)

    def on_leave(self):
        self.update_time()
        self.active = False
    
    def on_join(self):
        self.active = True
        self.recent_join_time = datetime.now(tz=timezone.utc)

class Event():
    def __init__(self, voice_channel) -> None:
        self.voice_channel = voice_channel
        self.attendees = set()
        self.start_time = datetime.now()

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
    
    def get_channel_id(self, ctx, channel_id : str = None) -> int:
        """identifies desired vc"""
        if channel_id == None:
            if ctx.author.voice == None: # author not in vc
                raise AttributeError
            
            channel_id = ctx.author.voice.channel.id
        else:
            if channel_id[0:1] != "<#" and channel_id[-1] != ">": # vc not mentioned properly
                raise ValueError
            
            channel_id = int(channel_id[2:len(channel_id)-1]) # get only id

        return channel_id

    @commands.hybrid_group(name="attendance", fallback="show")
    async def tracker(self, ctx, channel_id : str = None):
        """display attendees"""
        try:
            event = self.get_event_from_id(channel := self.get_channel_id(ctx, channel_id))
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
    
    @tracker.command(name="start")
    @commands.has_role("Executives")
    async def event_create(self, ctx, channel_id : str = None) -> None:
        """Adds vc exec is in to tracking"""
        # identifies desired vc
        try:
            channel_id = self.get_channel_id(ctx, channel_id=channel_id)
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
            event.add_attendee(Attendee(voice.guild.get_member(id), datetime.now(tz=timezone.utc)))

    @tracker.command(name="end")
    @commands.has_role("Executives")
    async def event_end(self, ctx, channel_id : str = None) -> None:
        """end vc event exec is in"""
        # identifies desired vc
        try:
            channel_id = self.get_channel_id(ctx, channel_id=channel_id)
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
            
        # iterates through events and finds and removes the one with matching voice channel
        self.events.remove([event for event in self.events if event.voice_channel == channel_id][0])
        await ctx.send(f"Attendance tracker ended for <#{channel_id}>!")

    # TODO: remove user command
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Updates status of attendees"""
        # update attendee object upon joining or leaving the channel
        if not before.channel is after.channel: 
            # joined channel
            if after.channel != None and after.channel.id in [event.voice_channel for event in self.events]:
                event = self.get_event_from_id(after.channel.id)
                
                try: # check for existing attendee object
                    attendee = event.get_attendee_from_member(member)

                    if not attendee.active:
                        attendee.on_join()

                except IndexError: # create new attendee object if new
                    event.add_attendee(Attendee(member, datetime.now(tz=timezone.utc)))
            
            # left channel
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
        if "Executives" in str(error):
            await ctx.send("Only execs can do this")
        else:
            await ctx.send("An error occured :/")

async def setup(client):
    await client.add_cog(AttendanceTracker(client))