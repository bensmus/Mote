# standard library
import os

# discord library
import discord
from discord.ext import commands

# redis for storing persistent data about prefixes and saved entries
import redis
r = redis.StrictRedis('localhost', 6379, charset="utf-8",
                      decode_responses=True)

TOKEN = os.getenv('DISCORD_TOKEN')
SHRUG = r'¯\_(ツ)_/¯'
DEFAULT_PREFIX = '#'


async def determine_prefix(bot, message):
    guild = message.guild
    if guild:

        # try to get prefix, if the bot has been on the server before
        prefix = r.hget('prefix', guild.id)

        # ok, we haven't visited server
        # set prefix to default
        if not prefix:
            r.hset('prefix', guild.id, DEFAULT_PREFIX)
            return DEFAULT_PREFIX

        return prefix

    return DEFAULT_PREFIX


# discord bot command_prefix can be linked to a callable
bot = commands.Bot(command_prefix=determine_prefix)


@ bot.event
async def on_guild_join(guild):
    response = (
        'Joined :white_check_mark:\n'
        '`-` My prefix is: `#`\n'
        '`-` To change prefix: `#prefix <prefix>`\n'

        '*Mote can be used to store plain text like hyperlinks '
        'or emoticons!*\n'

        'Type `#help` for more details.\n'
        f'{SHRUG}'
    )

    general = discord.utils.get(guild.channels, name='general')
    await general.send(response)


save_help_string = (
    'Save text with ID and label. This command is context dependent.\n'
    '`-` if you invoke (type it) the command in a DM, it will save to your '
    'personal library\n'
    '`-` if you invoke it in a server text channel, '
    'it will save to the channel library.'
)

save_channel_help_string = (
    'Save text with ID and label. Visible to everyone on this channel, while on this server.'
)

# have a separator for both of them, first matches in personal library, then matches in channel library
id_help_string = (
    'Display entries based on ID, saved in your personal library and in channel library.'
)

prefix_help_string = (
    'Change the prefix used by the discord bot.'
)


@bot.command(name='save', help=save_help_string)
async def save_text(ctx, ID, text, label=None):

    # detect DM
    if isinstance(ctx.channel, discord.channel.DMChannel):
        savetype = ctx.author
        emoji = ':person_standing:'

    else:
        emoji = ':person_standing:' * 3
        savetype = ctx.channel

    response = (
        f'ID: `{ID}`\n'
        f'Text: `{text}`\n'
        f'Label: `{label}`\n'
        f'Saved to `{savetype}` {emoji} library :white_check_mark:'
    )

    # redis storage
    key = str(savetype.id) + ':' + ID
    value = text + ':' + str(label)  # label could be None
    r.hset('library', key, value)

    await ctx.send(response)


@bot.command(name='id', help=id_help_string)
async def get_text_by_id(ctx, ID):

    # detect DM
    if isinstance(ctx.channel, discord.channel.DMChannel):
        key = str(ctx.author.id) + ':' + ID

    else:
        key = str(ctx.channel.id) + ':' + ID

    value = str(r.hget('library', key))
    text = value.split(':')[0]

    await ctx.send(text)


@bot.command(name='prefix', help=prefix_help_string)
async def change_prefix(ctx, prefix):
    guild = ctx.guild
    if guild:
        old_prefix = r.hget('prefix', ctx.guild.id)
        response = f'prefix changed from {old_prefix} to {prefix}'

        # go into redis prefix hash
        r.hset('prefix', ctx.guild.id, prefix)

        await ctx.send(response)


bot.run(TOKEN)
