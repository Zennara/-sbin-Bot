# /sbin/ Discord Bot, by @Zennara

# imports
import discord  # api
import os  # for virtual environment secrets on replit
import asyncio  # not needed unless creating loop tasks etc (you'll run into it)
import json  # for database
import requests  # to check discord api for limits/bans
from datetime import datetime
import os.path
import html

# api limit checker
# https://discordpy.readthedocs.io/en/stable/api.html
r = requests.head(url="https://discord.com/api/v1")
try:
    print(f"You are being Rate Limited : {int(r.headers['Retry-After']) / 60} minutes left")
except:
    print("No rate limit")

f = open('database.json')  # open json
data = json.load(f)  # read data
f.close()  # close

f = open('config.json')  # open json
config = json.load(f)  # read data
f.close()  # close

# declare client
intents = discord.Intents.all()  # declare what Intents you use, these will be checked in the Discord dev portal
client = discord.Client(intents=intents)

# declare vars
joinrole = 928770525830971403
guild = client.get_guild(806706495466766366)
redditChannel = 935549461457948715


# error message
async def error(message, code):
    await message.channel.send("```\n" + code + "\n```")


async def checkReddit():
    while True:
        SUBREDDITS_TO_CHECK = ["Discord_Bots"]
        FLAIRS = ["Bot Request [Paid]", "Bot Request [Existing ONLY]", "Bot Request [Free]"]
        NUM_POSTS_TO_CHECK = 10
        PATH = ""

        def getNumNewPosts(oldJson, latestJson):
            for j in range(NUM_POSTS_TO_CHECK):
                oldLatestPost = oldJson['data']['children'][j]['data']['permalink']
                # if it reaches the end of the for loop then all posts are new
                for i in range(NUM_POSTS_TO_CHECK):
                    latestPost = latestJson['data']['children'][i]['data']['permalink']
                    if latestPost == oldLatestPost:
                        print("Matched post after " + str(i) + " iteration")
                        return i, j
                    else:
                        print(latestPost + " != " + oldLatestPost)
                print("Couldn't find the last saved post, trying the next last saved post...")
            print("Failed to find any posts. Giving up and posting them all.")
            return NUM_POSTS_TO_CHECK

        print(datetime.now())
        for sub in SUBREDDITS_TO_CHECK:
            print("checking " + sub)
            r = requests.get("https://old.reddit.com/r/" + sub + "/new/.json?count=" + str(NUM_POSTS_TO_CHECK),
                             headers={
                                 'User-agent': 'Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36'})
            latestJson = json.loads(r.text)

            # Number of new posts since last check
            newPosts = NUM_POSTS_TO_CHECK
            numRemovedPosts = 0
            if os.path.exists(PATH + sub + ".json"):
                with open(PATH + sub + ".json", "r") as f:
                    oldJson = json.loads(f.read())
                    newPosts, numRemovedPosts = getNumNewPosts(oldJson, latestJson)
            else:
                print("File not found. If this is the first time checking the subreddit, ignore this message.")
                newPosts = 2
            with open(PATH + sub + ".json", "w") as f:
                f.write(r.text)
            print("Number of new posts: " + str(newPosts))
            for i in range(newPosts):
                post = latestJson['data']['children'][i]['data']
                description = post['link_flair_text']
                if i == 0 and numRemovedPosts > 1:
                    description += "\nNote: The last post before this one was removed from this subreddit!"

                username = "/r/" + sub
                content = "<@427968672980533269>"
                embed = discord.Embed(title=html.unescape(post['title']), description=description,
                                      url="https://reddit.com" + post['permalink'])
                print(post['url'])
                if post['url'].endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    embed.set_image(url=post['url'])
                print(post["link_flair_text"])
                if post["link_flair_text"] in FLAIRS:
                    print("done")
                    # get webhook
                    hooks = await guild.get_channel(redditChannel).webhooks()
                    hookFind = False
                    if hooks:
                        x = 0
                        for hook in hooks:
                            if hook.token != None:
                                webhook = hooks[x]
                                hookFind = True
                                break
                            x += 1
                    if not hookFind:
                        webhook = await client.get_channel(redditChannel).create_webhook(name="Reddit Updates",
                                                                                         avatar=None,
                                                                                         reason="For the /sbin/ bot")
                    await webhook.send(content=content, username=username, embed=embed)
        await asyncio.sleep(5)


async def checkCounters():
    while True:
        # discord API limits rates to twice every 10m for channel edits
        await asyncio.sleep(600)

        # update channels
        for guild in client.guilds:
            # get amount of bots
            bots = 0
            for member in guild.members:
                if member.bot:
                    bots += 1
            for channel in guild.stage_channels:
                if channel.name.startswith("Members"):
                    if (channel.name != "Members: " + str(guild.member_count - bots)):
                        await channel.edit(name="Members: " + str(guild.member_count - bots))
                if channel.name.startswith("Bots"):
                    if (channel.name != "Bots: " + str(bots)):
                        await channel.edit(name="Bots: " + str(bots))
                if channel.name.startswith("Channels"):
                    if (channel.name != "Channels: " + str(
                            len(guild.text_channels) + len(guild.voice_channels) - len(guild.categories))):
                        await channel.edit(name="Channels: " + str(
                            len(guild.text_channels) + len(guild.voice_channels) - len(guild.categories)))
                if channel.name.startswith("Text Channels"):
                    if (channel.name != "Text Channels: " + str(len(guild.text_channels))):
                        await channel.edit(name="Text Channels: " + str(len(guild.text_channels)))
                if channel.name.startswith("Voice Channels"):
                    if (channel.name != "Voice Channels: " + str(len(guild.voice_channels))):
                        await channel.edit(name="Voice Channels: " + str(len(guild.voice_channels)))
                if channel.name.startswith("Categories"):
                    if (channel.name != "Categories: " + str(len(guild.categories))):
                        await channel.edit(name="Categories: " + str(len(guild.categories)))
                if channel.name.startswith("Roles"):
                    if (channel.name != "Roles: " + str(len(guild.roles))):
                        await channel.edit(name="Roles: " + str(len(guild.roles)))
                if channel.name.startswith("Bans"):
                    if (channel.name != "Bans: " + str(len(await guild.bans()))):
                        await channel.edit(name="Bans: " + str(len(await guild.bans())))


@client.event
async def on_ready():
    print("\n/sbin/ Ready.\n")
    global startDate
    startDate = datetime.now()
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="in the shell"))


@client.event
async def on_raw_reaction_add(payload):
    if payload.member.id != client.user.id:
        for role in payload.member.guild.roles:
            if [str(payload.channel_id), str(payload.message_id), str(role.id), str(payload.emoji)] in \
                    data[str(payload.guild_id)]["role_reactions"]:
                await payload.member.add_roles(payload.member.guild.get_role(int(role.id)), atomic=True)


@client.event
async def on_raw_reaction_remove(payload):
    if payload.user_id != client.user.id:
        for role in client.get_guild(int(payload.guild_id)).roles:
            if [str(payload.channel_id), str(payload.message_id), str(role.id), str(payload.emoji)] in \
                    data[str(payload.guild_id)]["role_reactions"]:
                await client.get_guild(int(payload.guild_id)).get_member(int(payload.user_id)).remove_roles(
                    client.get_guild(int(payload.guild_id)).get_role(int(role.id)), atomic=True)


@client.event
async def on_member_join(member):
    await member.add_roles(member.guild.get_role(joinrole), atomic=True)


history = []


@client.event
async def on_message(message):
    # check for bots
    if message.author.bot:
        return

    # get prefix
    prefix = data[str(message.guild.id)]["prefix"]

    # convert the message to all lowercase
    messagecontent = message.content.lower()

    # add to history
    if messagecontent.startswith(prefix) and messagecontent.strip() != "$":
        # check if prefix not spaced
        if not messagecontent.startswith("$ "):
            await error(message, "invalid usage, commands start with $_")
            return

        if len(history) >= 20:
            del history[0]
        history.append(str(message.author.id) + "|" + messagecontent)

        # get uptime
        global startDate
        uptime = datetime.now() - startDate

        # history command
        if messagecontent == prefix + " history":
            text = ""
            count = 0
            for x in history:
                if x.startswith(str(message.author.id)):
                    count += 1
                    text = text + str(count) + (" " * (4 - len(str(count)))) + x[19:] + "\n"
            await message.channel.send("```\n" + text + "\n```")

        # this will clear the database if something is broken, WARNING: will delete all entries
        elif messagecontent == "$ clear":
            # my database entries are seperates by server id for each key. this works MOST of the time unless you have a large amount of data
            data[str(message.guild.id)] = {"prefix": "$", "role_reactions": []}
            writeData(data)

        # ping command
        elif messagecontent == prefix + " ping":
            await message.channel.send("```\n/sbin/ has been online for " + str(uptime) + "\n```")

        # uname command
        elif messagecontent == prefix + " uname":
            await message.channel.send(
                "```\n/sbin/ Bot\nAuthor:       Zennara#8377\nCreated:      1/7/2021\nPublic:       False\nDescription:  A custom bot for this server. This can't be found anywhere else.\n```")

        # neofeatch
        elif messagecontent == prefix + " neofetch":
            await message.channel.send("""```
           , - ~ ~ ~ - ,             /sbin/ Discord Bot
       , '               ' ,       . ------------------
     ,      .                ,     . Host: Linode.com
    ,     /#|#\               ,    . Uptime: """ + str(uptime) + """
   ,      # |                  ,   . Version: 1.1.0
   ,      \#|#\                ,   . Library: Py-Cord 2.5.0
   ,        | #                ,   . Packages: 15
    ,     \#|#/  ______       ,    . Theme: Linux Terminal
     ,      '                ,     . Prefix: $
       ,                   ,       . Author: @Zennara
         ' - , _ _ _ , - '         . Status: Custom, Private
      ```""")

        # echo command
        elif messagecontent.startswith(prefix + " echo"):
            if len(messagecontent.split(" ", 2)) >= 3:
                await message.channel.send("```\n" + message.content.split(" ", 2)[2] + "\n```")

        # find command
        elif messagecontent.startswith(prefix + " find"):
            splits = messagecontent.split(" ", 2)
            if message.mentions:
                splits[2] = message.mentions[0].name
            for mbr in message.author.guild.members:
                if splits[2] in mbr.name.lower():
                    await message.channel.send(
                        "```\n" + mbr.name + "#" + mbr.discriminator + "\nStatus: " + mbr.raw_status + "\nCreated: " + str(
                            mbr.created_at) + "\nJoined: " + str(mbr.joined_at) + "\nID: " + str(mbr.id) + "\n```")
                print(splits[2] + " | " + mbr.name)

        # whoami command
        elif messagecontent == prefix + " whoami":
            mbr = message.author
            await message.channel.send(
                "```\n" + mbr.name + "#" + mbr.discriminator + "\nStatus: " + mbr.raw_status + "\nCreated: " + str(
                    mbr.created_at) + "\nJoined: " + str(mbr.joined_at) + "\nID: " + str(mbr.id) + "\n```")


        # ls command
        elif messagecontent.startswith(prefix + " ls"):
            if messagecontent == prefix + " ls roles":
                text = "```\nno role reactions found"
                if data[str(message.guild.id)]["role_reactions"]:
                    text = "```\n"
                    for role in data[str(message.guild.id)]["role_reactions"]:
                        text += "#" + str(client.get_channel(int(role[0]))) + "   " + str(role[1]) + "   " + str(
                            message.guild.get_role(int(role[2]))) + "   " + str(role[3]) + "\n"
                await message.channel.send(text + "\n```")

        # cp
        elif messagecontent.startswith(prefix + " cp"):
            if messagecontent.startswith(prefix + " cp role"):
                splits = messagecontent.split()
                if len(splits) == 6:
                    channelID = splits[3][-37:-19]
                    messageID = splits[3][-18:]
                    roleID = splits[4].replace("<", "").replace(">", "").replace("&", "").replace("@", "")
                    emoji = splits[5]
                    if channelID.isnumeric() and messageID.isnumeric():
                        if client.get_channel(int(channelID)):
                            channel = client.get_channel(int(channelID))
                            if await channel.fetch_message(int(messageID)):
                                msg = await channel.fetch_message(int(messageID))
                                if roleID.isnumeric():
                                    if message.guild.get_role(int(roleID)):
                                        try:
                                            await msg.add_reaction(emoji)
                                        except:
                                            await error(message, "cp: " + roleID + ": invalid emoji")
                                        else:
                                            data[str(message.guild.id)]["role_reactions"].append(
                                                [channelID, messageID, roleID, emoji])
                                            writeData(data)
                                            await message.channel.send("```\nrole reaction added\n```")
                                    else:
                                        await error(message, "cp: " + roleID + ": invalid role")
                                else:
                                    await error(message, "cp: " + roleID + ": role id not numeric")
                            else:
                                await error(message, "cp: " + splits[2] + ": invalid message")
                        else:
                            await error(message, "cp: " + splits[2] + ": invalid channel")
                    else:
                        await error(message, "cp: " + splits[2] + ": invalid message link")
                else:
                    await error(message, "cp: not enough arguments passed")

        # rm
        elif messagecontent.startswith(prefix + " rm"):
            # rm roles
            if messagecontent.startswith(prefix + " rm role"):
                splits = messagecontent.split()
                if len(splits) == 6:
                    channelID = splits[3][-37:-19]
                    messageID = splits[3][-18:]
                    roleID = splits[4].replace("<", "").replace(">", "").replace("&", "").replace("@", "")
                    emoji = splits[5]
                    if channelID.isnumeric() and messageID.isnumeric():
                        if [channelID, messageID, roleID, emoji] in data[str(message.guild.id)]["role_reactions"]:
                            data[str(message.guild.id)]["role_reactions"].remove([channelID, messageID, roleID, emoji])
                            writeData(data)
                            channel = client.get_channel(int(channelID))
                            msg = await channel.fetch_message(int(messageID))
                            await msg.remove_reaction(emoji, message.guild.get_member(client.user.id))
                            await message.channel.send("```\nrole reaction removed\n```")
                        else:
                            await error(message, "rm: -role: no such reaction role")
                    else:
                        await error(message, "rm: -role: invalid message link")
                else:
                    await error(message, "rm: -role: not enough arguments passed")

        # pwd
        elif messagecontent == prefix + " pwd":
            await message.channel.send("```\nhttps://github.com/Zennara/-sbin-Bot\n```")

        # touch command - create embed
        elif messagecontent.startswith(prefix + " touch"):
            splits = message.content.split(" ", 3)
            if len(splits) == 4:
                channelID = splits[2]
                if splits[2].isnumeric():
                    if message.guild.get_channel(int(splits[2])):
                        cnl = message.guild.get_channel(int(splits[2]))
                        if json.loads(splits[3].replace("'", '"')):
                            jsn = json.loads(splits[3].replace("'", '"'))
                            if discord.Embed.from_dict(jsn):
                                embed = discord.Embed.from_dict(jsn)
                                await cnl.send(embed=embed)
                                await message.channel.send("```\nEmbed message sent in #" + cnl.name + "\n```")
                            else:
                                await error(message, "touch: cannot load dict to embed")
                        else:
                            await error(message, "touch: cannot load to dictionary")
                    else:
                        await error(message, "touch: invalid channel")
                else:
                    await error(message, "touch: channel id must be int or mention")
            else:
                await error(message, "touch: not enough arguments passed")

        # nano command - edit embed
        elif messagecontent.startswith(prefix + " nano"):
            splits = message.content.split(" ", 3)
            if len(splits) == 4:
                channelID = splits[2][-37:-19]
                messageID = splits[2][-18:]
                if channelID.isnumeric() and messageID.isnumeric():
                    if message.guild.get_channel(int(channelID)):
                        cnl = message.guild.get_channel(int(channelID))
                        if await cnl.fetch_message(int(messageID)):
                            msg = await cnl.fetch_message(int(messageID))
                            try:
                                jsn = json.loads(splits[3].replace("'", '"'))
                            except:
                                await error(message, "nano: cannot load to dictionary")
                            else:
                                if discord.Embed.from_dict(jsn):
                                    embed = discord.Embed.from_dict(jsn)
                                    await msg.edit(embed=embed)
                                    await message.channel.send("```\nEmbed message edited in #" + cnl.name + "\n```")
                                else:
                                    await error(message, "nano: cannot load dict to embed")
                        else:
                            await error(message, "nano: invalid message")
                    else:
                        await error(message, "nano: invalid channel")
                else:
                    await error(message, "nano: invalid message link")
            else:
                await error(message, "nano: not enough arguments passed")

        # cat command - display message contents
        elif messagecontent.startswith(prefix + " cat"):
            splits = messagecontent.split()
            if len(splits) == 3:
                channelID = splits[2][-37:-19]
                messageID = splits[2][-18:]
                if channelID.isnumeric() and messageID.isnumeric():
                    if client.get_channel(int(channelID)):
                        channel = client.get_channel(int(channelID))
                        if await channel.fetch_message(int(messageID)):
                            msg = await channel.fetch_message(int(messageID))
                            embedText = ""
                            if msg.embeds:
                                embedText = "["
                                for embed in msg.embeds:
                                    embedText = embedText + str(msg.embeds[0].to_dict()) + (
                                        ", " if len(msg.embeds) != 1 else "")
                                embedText = embedText
                                embedText += "]"
                                embedText = embedText.replace(", ]", "]")
                            await message.channel.send(
                                "```\n" + msg.content + ("\n\n" + embedText if embedText != "" else "") + "\n```")
                        else:
                            await error(message, "cat: " + splits[2] + ": invalid message")
                    else:
                        await error(message, "cat: " + splits[2] + ": invalid channel")
                else:
                    await error(message, "cat: invalid message link")
            else:
                await error(message, "cat: not enough arguments passed")

        # no command
        else:
            splits = messagecontent.split()
            if len(splits) == 2:
                await error(message, "Command '" + splits[1] + "' not found")
            else:
                await error(message, splits[1] + ": command not found")


@client.event
async def on_guild_join(guild):
    data[str(guild.id)] = {"prefix": "$"}  # for database support
    writeData(data)


# function to re-read data again from json database
def readData():
    f = open('database.json')  # open json
    global data
    data = json.load(f)  # read data
    f.close()  # close


# function to write json data
def writeData(data):
    # Serializing json
    json_object = json.dumps(data, indent=2)

    # Writing to sample.json
    with open("database.json", "w") as outfile:
        outfile.write(json_object)

    # reread data
    readData()


client.loop.create_task(checkCounters())
client.loop.create_task(checkReddit())

# keep the bot running after the window closes, use UptimeRobot to ping the website at least every <60min. to prevent the website from going to sleep, turning off the bot

# run bot
client.run(config['token'])
