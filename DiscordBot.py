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

    async def on_ready(self):
        print(f"{self.bot.user} is running")
        activity = Activity(name="Information", type=ActivityType.watching)
        await self.bot.change_presence(activity=activity)

    async def send_file_in_chat(self, file_name, file_content, channel_id=1182998507460771890):
        print("i was called!")
        try:
            if isinstance(channel_id, int):
                channel = self.bot.get_channel(channel_id)
            await channel.send("File sending in process.")
            await channel.send(file_name)
            message_id = await self.get_message_id_by_content(str(channel), file_name)
            reference_message = await channel.fetch_message(message_id)
            data_list = self.file_manager.split_file_data(file_content)
            for i, chunk in enumerate(data_list):
                file_data = discord.File(chunk, filename=f"{reference_message.content}{i}.txt")
                await channel.send(content=f"Chunk {i + 1}:", file=file_data, reference=reference_message)
            await channel.send("File sending complete.")
        except Exception as e:
            print(f"Error sending file in chat: {e}")

    async def assemble_file_from_chat(self, message_id, channel_id=1182998507460771890):
        try:
            if isinstance(channel_id, int):
                channel = self.bot.get_channel(channel_id)
            await channel.send("File assembly in progress...")
            reference_message = await channel.fetch_message(message_id)
            all_messages = []
            async for msg in reference_message.channel.history(limit=None):
                all_messages.append(msg)
            reply_messages = [msg for msg in all_messages if msg.reference and msg.reference.message_id == message_id]
            sorted_reply_messages = sorted(reply_messages, key=lambda msg: msg.created_at)
            print(f"Type of sorted: {type(sorted_reply_messages)} type of [0] {type(sorted_reply_messages[0])}")
            self.file_manager.assemble_file(sorted_reply_messages)
            await channel.send("File assembly completed!")
        except Exception as e:
            await channel.send("File assembly failed!")
            print(f"Error during file assembling: {e}")

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
            name = (user_message[5::])
            await self.send_file_in_chat(name, file_data)

        elif user_message.startswith("get"):
            message_id = await self.get_message_id_by_content(str(channel), user_message[4::])
            await self.assemble_file_from_chat(message_id)

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


