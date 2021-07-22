import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

intents = discord.Intents(members = True, messages = True, guilds = True)

client = commands.Bot(intents = intents, command_prefix = ".", status = discord.Status.online, activity = discord.Game("just a testing bot"), help_command = None)

load_dotenv('./.env')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

@client.event
async def on_ready():
    print("transfer loaded")

client.run(DISCORD_TOKEN)