import discord
from discord import Activity, ActivityType  # Add this line for activity
from discord.ext import commands

intents = discord.Intents.all()
intents.typing = False
intents.presences = False
intents.messages = True  # Enable the message intent


async def send_message(message, user_message, is_private):
    pass


def run_discord_bot():
    TOKEN = ""
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f"{client.user} is running")
        activity = Activity(name="Information", type=ActivityType.streaming)
        await client.change_presence(activity=activity)

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return  # Don't respond to ourselves

        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)
        print(f"{username} said: {user_message} in {channel}")


    client.run(TOKEN)

run_discord_bot()
