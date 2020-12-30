# ----RUNNING LOCALLY----
# https://realpython.com/python-redis/#using-redis-py-redis-in-python
# https://hackersandslackers.com/redis-py-python/
# downloading redis-stable tarball into /usr/local/lib

# 1) redis-server /etc/redis/6379.conf
# this creates server that runs in the background
# to check the process: "pgrep redis-server"
# to kill the process: "redis-cli" --> "shutdown"
# 2) run the python script
# 3) check your work with "rdb --command json dump.rdb"

# If I restart my computer, I need to restart the redis server
# the data is saved in the dump.rdb from which the server fetches automatically

# Python:
# r = redis.StrictRedis(decode_responses=True)
# ------------------------

# ----RUNNING REMOTELY----
# REDIS_URL config variable is made
# tells the server what configuration to used based on a url
# we can see that behind the scenes, heroku uses AWS

# turning the whole shebang on and off is done by toggling the worker on the heroku website

# Python:
# r = redis.from_url(REDIS_URL)

# ------------------------

# no support for label or multilabel
# to do label, we need ownership list and another hash table

# standard library
import os

# discord library
import discord
from discord.ext import commands

# redis for storing persistent data about prefixes and saved entries
import redis

TOKEN = os.getenv('DISCORD_TOKEN')
REDIS_URL = os.getenv('REDIS_URL')
SHRUG = r'¯\_(ツ)_/¯'
DEFAULT_PREFIX = '#'

r = redis.from_url(REDIS_URL, decode_responses=True)


async def determine_prefix(bot, message):
    guild = message.guild
    if guild:

        # try to get prefix, if the bot has been on the server before
        prefix = r.hget('prefix', guild.id)

        # ok, we haven't visited server
        # set prefix to default
        if not prefix:
            r.hset('prefix', guild.id, DEFAULT_PREFIX)
            # r.save()  forced save does not work on Heroku redis for some reason
            return DEFAULT_PREFIX

        return prefix

    return DEFAULT_PREFIX


# discord bot command_prefix can be linked to a callable
# callable occurs every message
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

# have a separator for both of them, first matches in personal library, then matches in channel library
id_help_string = (
    'Display entries based on ID.'
)

prefix_help_string = (
    'Change the prefix used by the discord bot.'
)


@bot.command(name='save', help=save_help_string)
async def save_text(ctx, ID, text):

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
        f'Saved to `{savetype}` {emoji} library :white_check_mark:'
    )

    # redis storage
    key = str(savetype.id) + ':' + ID
    value = text
    r.hset('text_library', key, value)
    # r.save()

    await ctx.send(response)


@bot.command(name='id', help=id_help_string)
async def get_text_by_id(ctx, ID):

    # detect DM
    if isinstance(ctx.channel, discord.channel.DMChannel):
        key = str(ctx.author.id) + ':' + ID

    else:
        key = str(ctx.channel.id) + ':' + ID

    value = r.hget('text_library', key)

    if value == None:
        await ctx.send('No text found based on the given id :cry:')

    else:
        await ctx.send(value)


def prefix_check(prefix, old_prefix):
    if len(prefix) == 1:
        if not (prefix.isdigit() or prefix.isalpha()):
            if prefix != '@':
                return True, f'Prefix changed from {old_prefix} to {prefix} :white_check_mark:'
            return False, 'Prefix cannot be changed to @ :x:'
        return False, 'Prefix cannot be number or letter :x:'
    return False, 'Prefix cannot be more than one character long :x:'


@bot.command(name='prefix', help=prefix_help_string)
async def change_prefix(ctx, prefix):
    guild = ctx.guild
    if guild:
        old_prefix = r.hget('prefix', ctx.guild.id)
        passed, response = prefix_check(prefix, old_prefix)

        if passed:
            # go into redis prefix hash
            r.hset('prefix', ctx.guild.id, prefix)
            r.save()

        await ctx.send(response)

    else:
        await ctx.send('Prefix command cannot be used in DM channels :x:')


bot.run(TOKEN)
