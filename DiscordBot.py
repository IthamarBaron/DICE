import discord
from discord import Activity, ActivityType
import time
import requests
from FileManager import FileManager
import io

intents = discord.Intents.all()
intents.typing = False
intents.presences = False
intents.messages = True
intents.message_content = True

def assemble_file_from_replays(sorted_reply_messages):
    for replay in sorted_reply_messages:
        chunk_link = replay.attachments[0].url
        chunk_data = requests.get(chunk_link).content # bytes containing message attachment file

def run_discord_bot():
    TOKEN = ""
    bot = discord.Client(intents=intents)

    @bot.event
    async def on_ready():
        print(f"{bot.user} is running")
        activity = Activity(name="Information", type=ActivityType.watching)
        await bot.change_presence(activity=activity)

    async def get_message_id_by_content(channel_name: str, message_content: str) -> int:
        guild = bot.guilds[0]
        channel = discord.utils.get(guild.channels, name=channel_name)

        if channel:
            async for message in channel.history(limit=100):
                if message.content == message_content:
                    return message.id

        return -1  # message not found

    @bot.event
    async def on_message(message: discord.Message):
        if message.author == bot.user:
            return  # Don't respond to ourselves
        username = str(message.author)
        user_message = str(message.content)
        channel = message.channel
        print(f"{username} said: {user_message} in {channel} attachments {message.attachments}")
        await message.channel.send(f"Noticed Input")

        file_name = "34mb.exe"
        file = open(file_name, "rb")
        file_data = file.read()
        file.close()

        # Check if the message is "send" or "get"
        if user_message.startswith("send"): #send <filename>
            # region message reference allocation
            await channel.send("File sending in process.")
            await channel.send(user_message[5::])
            message_id = await get_message_id_by_content(str(channel), user_message[5::])
            # endregion
            FM = FileManager()
            data_list = FM.split_file_data(file_data)
            reference_message = await message.channel.fetch_message(message_id)
            for i, chunk in enumerate(data_list):
                file_data = discord.File(chunk, filename=f"{reference_message.content}{i}.txt")
                await channel.send(content=f"Chunk {i + 1}:", file=file_data, reference=reference_message)
            await channel.send("File sending complete.")

        elif user_message.startswith("get"):
            # assemble file

            await message.channel.send("File assembly in progress...")
            file_name = user_message[4::]
            message_id = await get_message_id_by_content(str(channel), file_name)
            reference_message = await message.channel.fetch_message(message_id)

            all_messages = []
            # Iterate over the async generator and collect messages in a list
            async for message in reference_message.channel.history(limit=None):
                all_messages.append(message)
            reply_messages = [message for message in all_messages if message.reference and message.reference.message_id == message_id]
            sorted_reply_messages = sorted(reply_messages, key=lambda message: message.created_at)
            assemble_file_from_replays(sorted_reply_messages)
            await message.channel.send("File assembly in completed!")


        elif user_message.startswith("LOG"):
            await message.channel.send("Logged the data in the console!")
            message_id = await get_message_id_by_content(str(channel), "34mb-example")
            reference_message = await message.channel.fetch_message(message_id)
            print(f"ID: {message_id} is: {reference_message.content} in {reference_message.channel} attachments {reference_message.attachments}")
            start_time = time.time()

            all_messages = []
            # Iterate over the async generator and collect messages in a list
            async for message in reference_message.channel.history(limit=None):
                all_messages.append(message)
            reply_messages = [message for message in all_messages if message.reference and message.reference.message_id == message_id]
            elapsed_time = time.time() - start_time
            sorted_reply_messages = sorted(reply_messages, key=lambda message: message.created_at)
            # The `reply_messages` list now contains all messages replying to the original message
            print(f"messages that replay to id: {message_id} are: {len(reply_messages)} TIME ELAPSED: {elapsed_time}")

            for i,chunk_message in enumerate(sorted_reply_messages):
                print(f"message {i} attachments: {chunk_message.attachments}")
            assemble_file_from_replays(sorted_reply_messages)

    bot.run(TOKEN)

run_discord_bot()

