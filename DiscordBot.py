import discord
from discord import Activity, ActivityType
from discord.ext import commands
import io
import base64
import os

from FileManager import FileManager

intents = discord.Intents.all()
intents.typing = False
intents.presences = False
intents.messages = True
intents.message_content = True

def run_discord_bot():
    TOKEN = ""
    bot = discord.Client(intents=intents)

    @bot.event
    async def on_ready():
        print(f"{bot.user} is running")
        activity = Activity(name="Information", type=ActivityType.watching)
        await bot.change_presence(activity=activity)

    @bot.event
    async def on_message(message:discord.Message):
        if message.author == bot.user:
            return  # Don't respond to ourselves

        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)
        print(f"{username} said: {user_message} in {channel} attachments {message.attachments}")
        await message.channel.send(f"Im here!")

        file_name = "34mb.exe"
        file = open(file_name, "rb")
        file_data = file.read()
        file.close()
        # Check if the message is "send" or "get"
        if user_message.lower() == "send":

            FM = FileManager()
            data_list = FM.split_file_data(file_data)
            for i, chunk in enumerate(data_list):

                file_data = discord.File(chunk, filename=f"TempFile{i}.txt")
                await message.channel.send(file=file_data)
            await message.channel.send("File Sending complete.")

        elif user_message.lower() == "get":
            #assemble file
            await message.channel.send("File assembly complete.")

    bot.run(TOKEN)

run_discord_bot()
