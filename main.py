#Discord.py Bot Template, by Zennara#8377

#imports
import discord #api
import os #for virtual environment secrets on replit
import keep_alive #this keeps our bot alive from the keep_alive.py file
import asyncio #not needed unless creating loop tasks etc (you'll run into it)
import json #to write db to a json file
import requests #to check discord api for limits/bans
from replit import db #database storage
import time
from datetime import datetime

#api limit checker
#rate limits occur when you access the api too much. You can view Discord.py's api below. There it will tell you whether an action will access the api.
#https://discordpy.readthedocs.io/en/stable/api.html
r = requests.head(url="https://discord.com/api/v1")
try:
  print(f"You are being Rate Limited : {int(r.headers['Retry-After']) / 60} minutes left")
except:
  print("No rate limit")

#declare client
intents = discord.Intents.all() #declare what Intents you use, these will be checked in the Discord dev portal
client = discord.Client(intents=intents)

#declare vars
joinrole = 928770525830971403

#error message
async def error(message, code):
  await message.channel.send("```\n"+code+"\n```")

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
      if [str(payload.channel_id),str(payload.message_id),str(role.id),str(payload.emoji.name)] in db[str(payload.guild_id)]["role_reactions"]:
        await payload.member.add_roles(payload.member.guild.get_role(int(role.id)), atomic=True)

@client.event
async def on_raw_reaction_remove(payload):
  if payload.user_id != client.user.id:
    for role in client.get_guild(int(payload.guild_id)).roles:
      if [str(payload.channel_id),str(payload.message_id),str(role.id),str(payload.emoji.name)] in db[str(payload.guild_id)]["role_reactions"]:
        await client.get_guild(int(payload.guild_id)).get_member(int(payload.user_id)).remove_roles(client.get_guild(int(payload.guild_id)).get_role(int(role.id)), atomic=True)

@client.event
async def on_member_join(member):
  await member.add_roles(member.guild.get_role(joinrole), atomic=True)

history = []
@client.event
async def on_message(message):
  #check for bots
  if message.author.bot:
    return

  #get prefix
  prefix = db[str(message.guild.id)]["prefix"]

  #convert the message to all lowercase
  messagecontent = message.content.lower()

  #this is to dump your databse into database.json. Change this to FALSE to stop this.
  DUMP = True
  if DUMP:
    data2 = {}
    count = 0
    for key in db.keys():
      data2[str(key)] = db[str(key)]
      count += 1

    with open("database.json", 'w') as f:
      json.dump(str(data2), f)

  #add to history
  if messagecontent.startswith(prefix) and messagecontent.strip() != "$":
    #check if prefix not spaced
    if not messagecontent.startswith("$ "):
      await error(message, "invalid usage, commands start with $_")
      return
      
    if len(history) >= 20:
      del history[0]
    history.append(str(message.author.id) +"|"+ messagecontent)
  
    #get uptime
    global startDate
    uptime = datetime.now() - startDate
  
    #history command
    if messagecontent == prefix+" history":
      text = ""
      count = 0
      for x in history:
        if x.startswith(str(message.author.id)):
          count += 1
          text = text+ str(count)+(" "*(4-len(str(count)))) + x[19:] + "\n"
      await message.channel.send("```\n"+text+"\n```")

    #this will clear the database if something is broken, WARNING: will delete all entries
    elif messagecontent == "$ clear":
      #my database entries are seperates by server id for each key. this works MOST of the time unless you have a large amount of data
      db[str(message.guild.id)] = {"prefix": "$", "role_reactions":[]}
        
    #ping command
    elif messagecontent == prefix+" ping":
      await message.channel.send("```\n/sbin/ has been online for " + str(uptime) + "\n```")
  
    #uname command
    elif messagecontent == prefix+" uname":
      await message.channel.send("```\n/sbin/ Bot\nAuthor:       Zennara#8377\nCreated:      1/7/2021\nPublic:       False\nDescription:  A custom bot for this server. This can't be found anywhere else.\n```")
  
    #neofeatch
    elif messagecontent == prefix+" neofetch":
      await message.channel.send("""```
           , - ~ ~ ~ - ,             /sbin/ Discord Bot
       , '               ' ,       . ------------------
     ,      .                ,     . Host: repl.it
    ,     /#|#\               ,    . Uptime: """+str(uptime)+"""
   ,      # |                  ,   . Version: 1.0.0
   ,      \#|#\                ,   . Library: Discord.py 1.7.3
   ,        | #                ,   . Packages: 9
    ,     \#|#/  ______       ,    . Theme: Linux Terminal
     ,      '                ,     . Prefix: $
       ,                   ,       . Author: Zennara#8377
         ' - , _ _ _ , - '         . Status: Custom, Private
      ```""")
  
    #echo command
    elif messagecontent.startswith(prefix+" echo"):
      if len(messagecontent.split(" ",2)) >= 3:
        await message.channel.send("```\n"+message.content.split(" ",2)[2]+"\n```")
  
    #find command
    elif messagecontent.startswith(prefix+" find"):
      splits = messagecontent.split(" ", 2)
      if message.mentions:
        splits[2] = message.mentions[0].name
      for mbr in message.author.guild.members:  
        if splits[2] in mbr.name.lower():
          await message.channel.send("```\n"+mbr.name+"#"+mbr.discriminator+"\nStatus: "+mbr.raw_status+"\nCreated: "+str(mbr.created_at)+"\nJoined: "+str(mbr.joined_at)+"\nID: "+str(mbr.id)+"\n```")
        print(splits[2] +" | "+ mbr.name)
  
    #whoami command
    elif messagecontent == prefix+" whoami":
      mbr = message.author
      await message.channel.send("```\n"+mbr.name+"#"+mbr.discriminator+"\nStatus: "+mbr.raw_status+"\nCreated: "+str(mbr.created_at)+"\nJoined: "+str(mbr.joined_at)+"\nID: "+str(mbr.id)+"\n```")
          
    
    #ls command
    elif messagecontent.startswith(prefix+" ls"):
      if messagecontent == prefix+" ls roles":
        text = "```\nno role reactions found"
        if db[str(message.guild.id)]["role_reactions"]:
          text = "```\n"
          for role in db[str(message.guild.id)]["role_reactions"]:
            text += "#"+str(client.get_channel(int(role[0])))+"   "+str(role[1])+"   "+str(message.guild.get_role(int(role[2])))+"   "+str(role[3]) + "\n"
        await message.channel.send(text+"\n```")
        
    #cp
    elif messagecontent.startswith(prefix+" cp"):
      if messagecontent.startswith(prefix+" cp role"):
        splits = messagecontent.split()
        if len(splits) == 6:
          channelID = splits[3][-37:-19]
          messageID = splits[3][-18:]
          roleID = splits[4].replace("<","").replace(">","").replace("&","").replace("@","")
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
                      await error(message, "cp: "+roleID+": invalid emoji")
                    else:
                      db[str(message.guild.id)]["role_reactions"].append([channelID,messageID,roleID,emoji])
                      await message.channel.send("```\nrole reaction added\n```")
                  else:
                    await error(message, "cp: "+roleID+": invalid role")
                else:
                  await error(message, "cp: "+roleID+": role id not numeric")
              else:
                await error(message, "cp: "+splits[2]+": invalid message")
            else:
              await error(message, "cp: "+splits[2]+": invalid channel")
          else:
            await error(message, "cp: "+splits[2]+": invalid message link")
        else:
          await error(message, "cp: not enough arguments passed")
  
    #rm
    elif messagecontent.startswith(prefix+" rm"):
      #rm roles
      if messagecontent.startswith(prefix+" rm role"):
        splits = messagecontent.split()
        if len(splits) == 6:
          channelID = splits[3][-37:-19]
          messageID = splits[3][-18:]
          roleID = splits[4].replace("<","").replace(">","").replace("&","").replace("@","")
          emoji = splits[5]
          if channelID.isnumeric() and messageID.isnumeric():
            if [channelID,messageID,roleID,emoji] in db[str(message.guild.id)]["role_reactions"]:
              db[str(message.guild.id)]["role_reactions"].remove([channelID,messageID,roleID,emoji])
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
  
    #pwd
    elif messagecontent == prefix+" pwd":
      await message.channel.send("```\nhttps://replit.com/@KeaganLandfried/sbin-bot\n```")

    #no command
    else:
      splits = messagecontent.split()
      if len(splits) == 2:
        await error(message, "Command '"+splits[1]+"' not found")
      else:
        await error(message, splits[1]+": command not found")
  
  
@client.event
async def on_guild_join(guild):
  db[str(guild.id)] = {"prefix": "$"} #for database support


keep_alive.keep_alive() 
#keep the bot running after the window closes, use UptimeRobot to ping the website at least every <60min. to prevent the website from going to sleep, turning off the bot

#run bot
#Add a secret environment variable named TOKEN in replit (lock icon on left sidebar)
client.run(os.environ.get("TOKEN"))