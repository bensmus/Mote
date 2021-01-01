# Mote: A Discord bot for saving text

## Add the bot to your server by visiting:
https://discord.com/api/oauth2/authorize?client_id=791605122341404683&permissions=8&scope=bot 

# Motivation
Save websites or other information onto a discord channel or in your personal library. This bot offers an alternative to making a shared spreadsheet.

# List of commands

Commands are entered by typing #\<Your comand here>.\
\# is known as a prefix, and can be changed with the prefix command. Commands take arguments, which are separated by spaces.

- **save:** Saves text at a given ID. This command can be used to overwrite an already existing ID. 
- **get:** Get text at a given ID.
- **delete:** Delete text at a given ID.
- **dump:** Shows all ID in use in alphabetical order.
- **prefix:** Change the prefix from # to a custom prefix.
- **help:** Shows help, which will help you out.

# Usage
#save url www.besturl.com\
#save shrug ```¯\_(ツ)_/¯```\
#save mike-email mike@mail.com\
#get url
> www.besturl.com

#dump
> mike-email\
shrug\
url

#prefix !\
!delete mike-email\
!dump
> shrug\
url

# Implementation
The bot is written using the discord.py library, which is an API wrapper for Discord. More info here: https://discordpy.readthedocs.io/en/latest/

It is deployed onto Heroku, and uses Heroku-Redis. In practice this means that: 
- Dependencies, the entry point of the application, and other information is specified so that Heroku knows what to do. See https://devcenter.heroku.com/articles/buildpacks 

- Heroku-Redis is a "Heroku add-on" that allows the script to store and get persistent information. In general, a Redis database allows you to store data structures like lists, sets, and hash tables, and is used in many different contexts. See https://redis.io/ 

- Heroku integrates seamlessly with my git repo, and I can deploy a branch to Heroku, saving me a lot of work.



