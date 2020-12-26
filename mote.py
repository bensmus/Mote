# standard library
import os
import re

# discord
import discord
from discord.ext import commands

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

bot = commands.Bot(command_prefix='#')

SHRUG = r'¯\_(ツ)_/¯'

save_help_string = (
    'Save text to your library of texts and give it an id and a label\n'
)

id_help_string = (
    'Display text saved in your library based on id\n'
)

prefix_help_string = (
    'Change the prefix used by the discord bot\n'
)


@bot.event
async def on_guild_join(guild):
    response = (
        'Joined :white_check_mark:\n'
        '`-` My prefix is: `#`\n'
        '`-` To change prefix: `#prefix <prefix>`\n'

        '*Mote can be used to store plain text like hyperlinks '
        'or emoticons!*\n'

        'Type `#help` for more details.'
    )

    general = discord.utils.get(guild.channels, name='general')
    await general.send(response)


@bot.command(name='save', help=save_help_string)
async def save_text(ctx, id, text, label=None):
    response = 'save command detected'
    await ctx.send(response)


@bot.command(name='id', help=id_help_string)
async def get_text_by_id(ctx, id):
    response = 'id command detected'
    await ctx.send(response)


@bot.command(name='prefix', help=prefix_help_string)
async def change_prefix(ctx, prefix):
    old_prefix = bot.command_prefix
    response = f'prefix changed from {old_prefix} to {prefix}'
    bot.command_prefix = prefix
    await ctx.send(response)

bot.run(TOKEN)
