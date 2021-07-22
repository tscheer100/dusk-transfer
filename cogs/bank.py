from logging import error
import os
import random
import asyncio
from discord import member
from discord.ext.commands.core import command
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord.ext.commands import context, errors
from motor import motor_asyncio
from typing import Union

load_dotenv('./.env')
MONGO_URL = os.getenv('MONGO_URL')

cluster = motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = cluster['dusk-bank']
collection = db['bank']

class Bank(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print("bank ready")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.open_bank(member)

    async def open_bank(self, ctx: Union[commands.Context, discord.Member]):
        if isinstance(ctx, commands.Context):
            self.ID = ctx.author.id
            self.name = ctx.author.name
        elif isinstance(ctx, discord.Member):
            self.ID = ctx.id
            self.name = ctx.name
        result = await collection.find_one({'_id': self.ID})
        if result == None:
            print(result)
            wallet = 0
            bank = 0
            new = {'_id': self.ID, 'name': self.name, 'wallet': wallet, 'bank': bank}
            await collection.insert_one(new)
            print(new)
        else:
            print("member already has a bank")

    # Commands
    @commands.command(aliases = ["bal", "wallet", "money"])
    async def balance(self, ctx, member: discord.Member = None):
        req = ctx.author
        if not member:
            await self.open_bank(ctx.author)
            self.user = ctx.author
            self.ID = ctx.author.id
            
        else:
            await self.open_bank(member)
            self.user = member
            self.ID = member.id

        result = await collection.find_one({'_id': self.ID})
        wallet_amt = result['wallet']
        bank_amt = result['bank']

        embed = discord.Embed(
            title = f"{self.user.display_name}'s balance",
            color = discord.Color.purple()
        )
        embed.add_field(name = "Wallet balance", value = wallet_amt)
        embed.add_field(name = "Bank balance", value = bank_amt)
        embed.set_footer(icon_url = req.avatar_url, text = f"requested by {req.display_name}")
        await ctx.send(embed = embed)
    @balance.error
    async def balance_error(self, err):
        if isinstance(err, errors.MissingRequiredArgument):
            return
        else:
            raise error

    @commands.command(aliases = ["dep"])
    async def deposit(self, ctx, amount = None):
        await self.open_bank(ctx.author)
        ID = ctx.author.id
        user = await collection.find_one({'_id': ID})

        wallet_amt = user['wallet']
        bank_amt = user['bank']

        if amount == None:
            await ctx.send("Invalid syntax, try `.deposit <amount>`")
            return

        new_wallet = wallet_amt - int(amount)
        new_bank = bank_amt + int(amount)
        if new_wallet >= 0:
            collection.update_one({'_id': self.ID}, {'$set': {'wallet': new_wallet} })
            collection.update_one({'_id': self.ID}, {'$set': {'bank': new_bank} })
            await ctx.send(f"You have deposited **{amount}** coins!")
        else:
            await ctx.send("You don't have enough in your wallet to deposit that much!")

    @commands.command()
    async def withdraw(self, ctx, amount = None):
        await self.open_bank(ctx.author)
        ID = ctx.author.id
        user = await collection.find_one({'_id': ID})

        wallet_amt = user['wallet']
        bank_amt = user['bank']

        if amount == None:
            await ctx.send("Invalid syntax, try `.withdraw <amount>`")
            return

        new_wallet = wallet_amt + int(amount)
        new_bank = bank_amt - int(amount)

        if new_bank >= 0:
            collection.update_one({'_id': self.ID}, {'$set': {'wallet': new_wallet} })
            collection.update_one({'_id': self.ID}, {'$set': {'bank': new_bank} })
            await ctx.send(f"You have withdrawn **{amount}** coins!")
        else:
            await ctx.send("You don't have enough in your bank to withdraw that much!")

    @commands.command()
    @commands.cooldown(1,60, commands.BucketType.user)
    async def beg(self, ctx):
        await self.open_bank(ctx)
        self.user = ctx.author
        self.ID = ctx.author.id
        
        result = await collection.find_one({'_id': self.ID})
        wallet_amt = result['wallet']
        bank_amt = result['bank']
        earnings = random.randrange(100)
        if wallet_amt + bank_amt < 200:
            await ctx.send(f"Someone gave you **{earnings}** coins!")
            new_wallet = wallet_amt + earnings
            await collection.update_one({'_id': self.ID}, {'$set': {'wallet': new_wallet} })
        else:
            await ctx.send("You can only beg if your net worth is below __**200 coins**__")
    @beg.error 
    async def beg_error(self, ctx, err):
        if isinstance(err, commands.CommandOnCooldown):
            msg = "**You are on a cooldown!** please wait **{:.2f}s**".format(err.retry_after)   
            await ctx.send(msg)

    @commands.command(aliases = ["send","give"])
    async def gift(self, ctx, Member: discord.Member, amount = None):
        await self.open_bank(ctx.author)
        await self.open_bank(member)
        ID = ctx.author.id
        MEM_ID = Member.id
        
        user = await collection.find_one({'_id': ID})
        mem = await collection.find_one({'_id': MEM_ID})
        wallet_amt = user['wallet']
        mem_amt = mem['wallet']
        if amount == None:
            await ctx.send("Please enter the amount")
            print("amount is None_type")
            return

        amount = int(amount)

        if amount > user['wallet']: # <-- problem starts here?
            await ctx.send("Insufficient amount in your wallet")
            return
        if amount == 0:
            await ctx.send(f"Sent {Member.display_name} a paperclip and chewed gum. \nYou good?")
            return
        if amount < 0:
            await ctx.send("Amount must be positive!")
            return
        
        await collection.update_one({'_id': ID}, {'$set': {'wallet': wallet_amt + (-1*amount)}})
        await collection.update_one({'_id': MEM_ID}, {'$set': {'wallet': mem_amt + amount}})

        await ctx.send(f"You sent {amount} coins to {Member.display_name}")
    @gift.error
    async def gift_error(self, ctx, err):
        if isinstance(err, errors.MemberNotFound):
            await ctx.send("Member not found. Try `.gift @member <amount>`")
        else:
            raise error

    # This method is wonky.
    @commands.command(aliases = ["slot"])
    async def slots(self, ctx, amount = None):
        await self.open_bank(ctx.author)
        user = await collection.find_one({'_id': ctx.author.id})
        wallet = user['wallet']

        if amount == None:
            await ctx.send("Please enter the amount.")
            return
        else:
            amount = int(amount)
        if amount > wallet:
            await ctx.send("Insufficient funds in your wallet.")
            return
        if amount < 0:
            await ctx.send("Amount can't be negative.")
        final = []

        # dusk emojis

        # among_rand = "<a:among_rand:855159685538512937>"
        # choices = ["<:among_yellow:855213922180005969>",
        # "<:among_white:855213922062958593>",
        # "<:among_red:855160363090706464>",
        # "<:among_purple:855160523939381278>",
        # "<:among_cyan:855213921899773984>",
        # "<:among_blue:855160063495897130>"]
 
        # test server emojis
        among_rand = "<a:among_rand:848648377922224229>"
        choices = ["<:among_blue:848646255252471868>",
        "<:among_purple:848646255264399370>",
        "<:among_red:848646255248146523>",
        # "<:among_yellow:855192733555621938>",
        # "<:among_cyan:855194895333720115>", removed to make chances more fair
        # "<:among_white:855196037647171595>"
        ]
        
        first = ""
        done = ""
        duplicate_check = set()

        # setting up final and results
        for i in range(3):
            final.append(random.choice(choices))
        
        for k in range(len(final)):
            done += final[k]
            done += " "
            duplicate_check.add(final[k])

        initial_embed = discord.Embed(
            title = "The slots begin to whirl furiously...",
            color = discord.Color.dark_purple()
        )
        initial = among_rand + " " + among_rand + " " + among_rand
        initial_embed.add_field(name = initial, value = "you wait anxiously...")
        msg = await ctx.send(embed = initial_embed)
        await asyncio.sleep(1)

        first_embed = discord.Embed(
            title = "The slots begin to whirl furiously...",
            color = discord.Color.dark_purple()
        )
        first += final[0] + " " + among_rand + " " + among_rand
        first_embed.add_field(name = first, value = "you wait anxiously...")
        await msg.edit(embed = first_embed)

        await asyncio.sleep(1)

        second_embed = discord.Embed(
            title = "The slots begin to whirl furiously...",
            color = discord.Color.dark_purple()
        )
        second = final[0] + " " + final[1] + " " + among_rand
        second_embed.add_field(name = second, value = "you wait anxiously...")
        await msg.edit(embed = second_embed)

        await asyncio.sleep(1)
        results_embed = discord.Embed(
            title = "The slots finally stop spinning...",
            color = discord.Color.dark_purple()
        )
        print(duplicate_check)
        len_diff = len(final) - len(duplicate_check)
        # results, send after slot finishes
        if len_diff == 2:
            await collection.update_one({'_id': ctx.author.id}, {'$set': {'wallet': wallet + (4*amount)} })
            results_embed.add_field(name = done, value = f"OH BABY A TRIPLE! You've won {4*amount} coins! :Fire16:")
        elif len_diff == 1:
            await collection.update_one({'_id': ctx.author.id}, {'$set': {'wallet': wallet + amount} })
            results_embed.add_field(name = done, value = f"Congratulations! You've won {2*amount} coins! :Fire16:")
        else:
            await collection.update_one({'_id': ctx.author.id}, {'$set': {'wallet': wallet - amount} })
            results_embed.add_field(name= done, value = f" Oh no! You've lost {amount} coins.")
        await msg.edit(embed = results_embed)
    

def setup(client):
    client.add_cog(Bank(client))