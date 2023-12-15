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

    async def get_message_id_by_content(bot, guild, channel_name, message_content):
        channel = discord.utils.get(guild.channels, name=channel_name)

        if channel:
            async for message in channel.history(limit=100):
                if message.content == message_content:
                    return message.id

        return None  # Message not found

    # Example of usage
    async def get_id():
        bot_instance = bot
        guild_instance = bot_instance.guilds[0]
        channel_name = "bot-playground"
        message_content = "helloworld"

        message_id = await get_message_id_by_content(bot_instance, guild_instance, channel_name, message_content)

        if message_id:
            print(f"The message ID is: {message_id}")
        else:
            print("Message not found.")


    @bot.event
    async def on_message(message:discord.Message):
        if message.author == bot.user:
            return  # Don't respond to ourselves

        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)
        print(f"{username} said: {user_message} in {channel} attachments {message.attachments}")
        await message.channel.send(f"Noticed Input")

        file_name = "34mb.exe"
        file = open(file_name, "rb")
        file_data = file.read()
        file.close()
        # Check if the message is "send" or "get"
        if user_message.lower() == "send":
            FM = FileManager()
            data_list = FM.split_file_data(file_data)
            reference_message = await message.channel.fetch_message(1185151312933945465)

            for i, chunk in enumerate(data_list):
                file_data = discord.File(chunk, filename=f"TempFile{i}.txt")
                await message.channel.send(content=f"Chunk {i + 1}:", file=file_data, reference=reference_message)
            await message.channel.send("File Sending complete.")

        elif user_message.lower() == "get":
            #assemble file
            await message.channel.send("File assembly complete.")

        elif user_message.lower() == "id":
            await get_id()

    bot.run(TOKEN)

run_discord_bot()
