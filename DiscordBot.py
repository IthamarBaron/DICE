import io
import time
import discord
import requests
from FileManager import FileManager
from discord import Activity, ActivityType


class DiscordBot:
    def __init__(self, token):
        self.token = token
        self.intents = discord.Intents.all()
        self.intents.typing = False
        self.intents.presences = False
        self.intents.messages = True
        self.intents.message_content = True
        self.bot = discord.Client(intents=self.intents)
        self.file_manager = FileManager()

    async def get_message_id_by_content(self, channel_name: str, message_content: str) -> int:
        guild = self.bot.guilds[0]
        channel = discord.utils.get(guild.channels, name=channel_name)

        if channel:
            async for message in channel.history(limit=100):
                if message.content == message_content:
                    return message.id

        return -1  # message not found

    def assemble_file_from_replays(self, sorted_reply_messages):
        file_data = b""
        for replay in sorted_reply_messages:
            chunk_link = replay.attachments[0].url
            chunk_data = requests.get(chunk_link).content
            file_data += chunk_data

        with open("recreated-file", "wb") as file:
            file.write(file_data)

    async def on_ready(self):
        print(f"{self.bot.user} is running")
        activity = Activity(name="Information", type=ActivityType.watching)
        await self.bot.change_presence(activity=activity)

    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return  # Don't respond to ourselves

        username = str(message.author)
        user_message = str(message.content)
        channel = message.channel
        print(f"{username} said: {user_message} in {channel} attachments {message.attachments}")
        await message.channel.send(f"Noticed Input")

        file_name = "DosImage.png"
        file = open(file_name, "rb")
        file_data = file.read()
        file.close()

        # Check if the message is "send" or "get"
        if user_message.startswith("send"):  # send <filename>
            await channel.send("File sending in process.")
            await channel.send(user_message[5::])
            message_id = await self.get_message_id_by_content(str(channel), user_message[5::])
            reference_message = await message.channel.fetch_message(message_id)
            data_list = self.file_manager.split_file_data(file_data)
            for i, chunk in enumerate(data_list):
                file_data = discord.File(chunk, filename=f"{reference_message.content}{i}.txt")
                await channel.send(content=f"Chunk {i + 1}:", file=file_data, reference=reference_message)
            await channel.send("File sending complete.")

        elif user_message.startswith("get"):
            await message.channel.send("File assembly in progress...")
            file_name = user_message[4::]
            message_id = await self.get_message_id_by_content(str(channel), file_name)
            reference_message = await message.channel.fetch_message(message_id)
            all_messages = []
            async for msg in reference_message.channel.history(limit=None):
                all_messages.append(msg)
            reply_messages = [msg for msg in all_messages if msg.reference and msg.reference.message_id == message_id]
            sorted_reply_messages = sorted(reply_messages, key=lambda msg: msg.created_at)
            print(f"Type of sorted: {type(sorted_reply_messages)} type of [0] {type(sorted_reply_messages[0])}")
            self.file_manager.assemble_file(sorted_reply_messages)
            await message.channel.send("File assembly completed!")

        elif user_message.startswith("LOG"):
            await message.channel.send("Logged the data in the console!")
            message_id = await self.get_message_id_by_content(str(channel), "168mb")
            reference_message = await message.channel.fetch_message(message_id)
            print(f"ID: {message_id} is: {reference_message.content} in {reference_message.channel} attachments {reference_message.attachments}")
            start_time = time.time()
            all_messages = []
            async for msg in reference_message.channel.history(limit=None):
                all_messages.append(msg)
            reply_messages = [msg for msg in all_messages if msg.reference and msg.reference.message_id == message_id]
            elapsed_time = time.time() - start_time
            sorted_reply_messages = sorted(reply_messages, key=lambda msg: msg.created_at)
            print(f"messages that replay to id: {message_id} are: {len(reply_messages)} TIME ELAPSED: {elapsed_time}")


    def run_discord_bot(self):
        @self.bot.event
        async def on_ready():
            await self.on_ready()

        @self.bot.event
        async def on_message(message):
            await self.on_message(message)

        self.bot.run(self.token)


# Usage
TOKEN = "MTE4Mjk5MTE2MTg3NTQ5NzAyMQ.G_2_1U.jArN2b2YYPeVD_nNAIsj2J1G9llZ5poeh0STyk"
bot_instance = DiscordBot(TOKEN)
bot_instance.run_discord_bot()
