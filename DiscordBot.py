
import discord
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

    async def get_available_file_name(self, file_name, channel_id=1182998507460771890):
        channel = self.bot.get_channel(channel_id)
        all_messages = set()
        async for msg in channel.history(limit=None):
            if not msg.reference:  # Check if the message is not a reply
                all_messages.add(msg.content)

        found_valid_name = False
        i = 1
        available_name = file_name
        while not found_valid_name:
            if available_name in all_messages:
                available_name = file_name+f"({i})"
                i += 1
            else:
                found_valid_name = True
        return available_name

    async def create_new_storage_area(self,channel_name):

        guild_id = 1182329387115348039
        guild = self.bot.get_guild(guild_id)
        category = discord.utils.get(guild.categories, id=1254808335140524102) # CHANGED THIS STORAGE ID
        new_channel = await guild.create_text_channel(channel_name, category=category)
        return new_channel.id

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
        """
            Send a file in chunks to a specified Discord channel.

            :param file_name: The name of the file being sent.
            :param file_content: The content of the file being sent.
            :param channel_id: The ID of the Discord channel to send the file to. Default is 1182998507460771890.
            :return: A list containing the file name and message ID if successful, otherwise None.
            """
        try:
            file_name = await self.get_available_file_name(file_name, channel_id)
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
            return [file_name, message_id]
        except Exception as e:
            print(f"Error sending file in chat: {e}")
            return None

    async def assemble_file_from_chat(self, message_id, channel_id=1182998507460771890):
        try:
            if isinstance(channel_id, int):
                channel = self.bot.get_channel(channel_id)
            else:
                channel = self.bot.get_channel(int(channel_id))
            await channel.send("File assembly in progress...")
            reference_message = await channel.fetch_message(message_id)
            all_messages = []
            async for msg in reference_message.channel.history(after=reference_message, limit=20):
                all_messages.append(msg)
            reply_messages = [msg for msg in all_messages if msg.reference and msg.reference.message_id == message_id]
            sorted_reply_messages = sorted(reply_messages, key=lambda msg: msg.created_at)
            print(f"Type of sorted: {type(sorted_reply_messages)} type of [0] {type(sorted_reply_messages[0])}")
            file_bytes = self.file_manager.assemble_file(sorted_reply_messages)
            await channel.send("File assembly completed!")
            return file_bytes
        except Exception as e:
            await channel.send("File assembly failed!")
            print(f"Error during file assembling: {e}")
            return b""

    async def delete_file_from_chat(self, message_id, channel_id=1182998507460771890):
        try:
            if isinstance(channel_id, int):
                channel = self.bot.get_channel(channel_id)
            else:
                channel = self.bot.get_channel(int(channel_id))

            reference_message = await channel.fetch_message(message_id)
            await channel.send(f"Deleting File: {reference_message.content}")

            all_messages = []
            async for msg in reference_message.channel.history(after=reference_message, limit=20):
                all_messages.append(msg)
            reply_messages = [msg for msg in all_messages if msg.reference and msg.reference.message_id == message_id]

            for msg in reply_messages:
                await msg.delete()
            await reference_message.delete()
            print(f"Deletion process completed")
            return True

        except Exception as e:
            return False

    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return  # Don't respond to ourselves

        username = str(message.author)
        user_message = str(message.content)
        channel = message.channel
        print(f"{username} said: {user_message} in {channel} attachments {message.attachments}")
        await message.channel.send(f"Noticed Input")



        # message commands - mainly used for manual debuging through discord
        if user_message.lower().startswith("send"):
            name = (user_message[5::])
            file_name = name
            file = open(file_name, "rb")
            file_data = file.read()
            file.close()
            await self.send_file_in_chat(name, file_data)

        elif user_message.lower().startswith("delete"):
            message_params = user_message.split(" ")
            await self.delete_file_from_chat(int(message_params[1]), int(message_params[2]))
            print("deleting")

        elif user_message.lower().startswith("log"):
            pass
        elif user_message.lower().startswith("clear"):
            all_messages = []
            async for msg in message.channel.history(limit=int(user_message[6::])):
                all_messages.append(msg)

            for msg in all_messages:
                await msg.delete()

        elif user_message.lower().startswith("drop"):
            # Extract the category ID from the command
            category_id = user_message[5:].strip()

            # Iterate over all channels to find and delete channels within the specified category
            for channel in message.guild.channels:
                if isinstance(channel, discord.CategoryChannel) and str(channel.id) == category_id:
                    # Found the category, now delete all channels within it
                    for sub_channel in channel.channels:
                        await sub_channel.delete()
                    await channel.delete()
                    print(f"All channels in category {channel.name} have been deleted.")
                    break  # Exit the loop once the category is found and processed
            else:
                print(f"Category with ID {category_id} not found.")




    def run_discord_bot(self):
        @self.bot.event
        async def on_ready():
            await self.on_ready()

        @self.bot.event
        async def on_message(message):
            await self.on_message(message)

        self.bot.run(self.token)

"""
bot = DiscordBot("")
bot.run_discord_bot()"""
