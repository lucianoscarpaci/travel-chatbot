from dotenv import load_dotenv
import discord
import os
import asyncio
import random
import emoji
from src.chatgpt_bot.openai import chatgpt_response
from src.giphy_bot.giphy import gif_response
from src.giphy_bot.giphy import sticker_response

load_dotenv()
discord_token = os.getenv('DISCORD_TOKEN')
emoji_arr = []
all_emoji = [emoji.emojize(x) for x in emoji.EMOJI_DATA]


class MyClient(discord.Client):
    async def on_ready(self):
        print("login successful, you are: ", self.user)
    
    
    
    async def on_message(self, message):
        print(message.content)
        if message.author == self.user:
            return
        command, own_message=None, None

        for text in ['Kinzie', 'kinzie']:
            if message.content.startswith(text):
                command=message.content.split(' ')[0]
                own_message=message.content.replace(text, '')
                print(command, own_message)

        if command == 'Kinzie' or command == 'kinzie':
            bot_response = chatgpt_response(prompt=own_message)
            await message.channel.typing()
            await asyncio.sleep(1)
            await message.channel.send(f"{bot_response}")
        
        if "Giphy " in message.content:
            await message.channel.send(gif_response(message.content.replace("Giphy ", "")))
        elif "sticker " in message.content:
            await message.channel.send(sticker_response(message.content.replace("sticker ", "")))
        elif any(x in message.content for x in all_emoji):
            range_indexes = range(5)
            for i in range_indexes:
                emoji_arr.append(random.choice(list(emoji.EMOJI_DATA)))
                result = ''.join(emoji_arr)
                result = result[-5:]
            await message.channel.send(result)


    
    


intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)


        

