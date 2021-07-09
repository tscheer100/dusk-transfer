import test
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord.ext.commands import errors
from pymongo import MongoClient

load_dotenv('./.env')
MONGO_URL = os.getenv('MONGO_URL')

cluster = MongoClient(MONGO_URL)
db = cluster['dusk-bank']
collection = db['bank']

# test = {'_id':1, 'name':'Test'}
# collection.insert_one(test)

class Bank(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def status(self, ctx):
        await ctx.send("status called")
        
def setup(client):
    client.add_cog(Bank(client))