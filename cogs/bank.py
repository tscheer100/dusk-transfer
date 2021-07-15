from discord.ext.commands.core import command
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord.ext.commands import errors
import pymongo
from pymongo import MongoClient
from pymongo import errors

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

    # Events
    @commands.Cog.listener()
    async def on_member_join(self, member):
        print("A member has joined")
        id = member.id
        wallet = 0
        bank = 0
        new = {'_id': id, 'wallet': wallet, 'bank': bank}
        collection.insert_one(new)
        print(new)
    @on_member_join.error()
    async def on_member_join_error(self, err):
        if isinstance(err, pymongo.errors):
            print("User already has a balance")

    # @commands.command()
    # @commands.command(1,60, commands.BucketType.user)
    # async def beg(self,ctx):
        


    # @commands.command()
    # @commands.cooldown(1,60, commands.BucketType.user)
    # async def beg(self, ctx):
    #     await self.open_account(ctx.author)
    #     self.user = ctx.author
    #     users = await self.get_bank_data()
    #     wallet_amt = users[str(self.user.id)]["wallet"]
    #     bank_amt = users[str(self.user.id)]["bank"]
    #     earnings = random.randrange(100)

    #     if wallet_amt + bank_amt < 200:
    #         await ctx.send(f"Someone gave you **{earnings}** coins!")
    #         users[str(self.user.id)]["wallet"] += earnings
    #     else:
    #         await ctx.send("You can only beg if your net worth is below __**200 coins**__")

    #     with open("bank.json", "w") as f:
    #         json.dump(users, f)

    #     return self.user

    @commands.command()
    async def status(self, ctx):
        await ctx.send("status called")
        
def setup(client):
    client.add_cog(Bank(client))