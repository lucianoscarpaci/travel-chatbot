from dotenv import load_dotenv
from kaomoji import kaomoji
import discord
import os
import asyncio
import random
import emoji
from src.chatgpt_bot.openai import turbo_response
from src.chatgpt_bot.openai import chat_response
import subprocess
load_dotenv()
discord_token = os.getenv('DISCORD_TOKEN')
discord_user_id = os.getenv('USER_ID')
photo_dir = os.getenv('PHOTOS')
all_kinzie_photos = os.listdir(photo_dir)
kaomoji_mode = False


class MyClient(discord.Client):
    async def on_ready(self):
        user = await client.fetch_user(client.user.id)
        await self.user.edit(username="Wubby")
        print(f"Hello {self.user} It's good to see you again.")

        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Shibuya, Tokyo, Japan 🌸🗼🇯🇵"), status=discord.Status.online)

        # start the background task to send hello message
        client.loop.create_task(self.hello_message())

    async def hello_message(self):

        # trigger the action
        user = await client.fetch_user(discord_user_id)
        channel = await user.create_dm()
        text_response = chat_response(
            prompt="Tell me all the sweet nothings. I could really use some support and love right now.\n")
        kinzie_photos = []
        for photo in all_kinzie_photos:
            filename = os.path.join(photo_dir, photo)
            kinzie_photos.append(filename)
        random_photo = random.choice(kinzie_photos)
        with open(random_photo, 'rb') as f:
            file = discord.File(f)
        await channel.send(file=file)
        await channel.send(f"{text_response}")

    async def on_message(self, message):
        global kaomoji_mode
        timeout = 300
        # if the message is from the bot itself, ignore it
        if message.author == self.user:
            return

        if message.content.lower().startswith("!kaomoji"):
            kaomoji_mode = not kaomoji_mode
            embed = discord.Embed(
                title=f"Kaomoji mode is now {'on' if kaomoji_mode else 'off'}", color=0xffc0cb)
            await message.channel.send(embed=embed)
        else:
            try:
                kao = kaomoji.Kaomoji()
                all_kaomoji = [x for x in kao.all_kaomoji()]
                if kaomoji_mode and any(x in message.content for x in all_kaomoji):
                    kaomoji_response = chat_response(
                        prompt="In your response include one kaomoji to express how you feel about me.\n")
                    await message.channel.send(f"{kaomoji_response}")
                    await self.wait_for('message', timeout=timeout)
            except asyncio.TimeoutError:
                if kaomoji_mode:
                    kaomoji_mode = False
                    embed = discord.Embed(
                        title=f"Kaomoji mode is now {'on' if kaomoji_mode else 'off'}", color=0xffc0cb)
                    await message.channel.send(embed=embed)

        if message.content.startswith("!help"):
            embed = discord.Embed(
                title="Commands", description="Commands for this bot", color=0xffc0cb)
            embed.add_field(name="Web browser", value="!search", inline=False)
            embed.add_field(name="Turbo Response", value="⁇", inline=False)
            embed.add_field(name="Chat Response", value="。", inline=False)
            embed.add_field(name="Kaomoji mode",
                            value="!kaomoji", inline=False)
            await message.channel.send(embed=embed)

        if message.content.endswith("⁇"):
            own_message = message.content.replace("⁇", "")
            bot_response = turbo_response(prompt=own_message)
            await message.channel.typing()
            await asyncio.sleep(1)
            await message.channel.send(f"{bot_response}")

        if message.content.endswith("。"):
            send_message = message.content
            emoji_response = chat_response(
                prompt=send_message + "In your response only use emojis to describe how you feel about me.\n")
            text_response = chat_response(
                prompt=send_message + "In your response include words.\n")

            for i in range(0, 1):
                animate_text = text_response[:i]
                animate_text = emoji.emojize(
                    ":bear:") + emoji.emojize(":heart:")

                finished = await message.channel.send(animate_text)
                await asyncio.sleep(1)

            await finished.delete()
            await message.channel.send(f"{emoji_response}")
            await message.channel.send(f"{text_response}")

        if message.content.startswith("Search"):
            query = message.content[7:]
            query_string = 'https://duckduckgo.com/?q=' + \
                '+'.join(query.split())
            await message.channel.send(query_string)

    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.user:
            return

        channel = self.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        if message.author == self.user and str(payload.emoji) == emoji.emojize(":bear:"):
            game = subprocess.Popen(
                ["python3", "-c", "from src.game_bot.game import HowManyWubbies; HowManyWubbies.player_start()"], stdout=subprocess.PIPE)
            game = game.communicate()
            game = game[0].decode("UTF-8")

            await message.channel.send(f'{game}')


intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True

client = MyClient(intents=intents)
