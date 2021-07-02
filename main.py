import os
import discord
from discord.ext import tasks
from dotenv import load_dotenv
import datetime
from pytz import timezone
import re
from replit import db
from deploy import deploy
import random

load_dotenv()

client = discord.Client()
hackNightRegex = "next ((?:s?hr?|cr|u|o)(?:e|a|i|o|u)?c?o?w?(?:k|c|p|t|oo?|u(?:t|p)?)(?:e|a)?(?:s|y|lacka)?(?:\s|-)?(?:n|b)?(?:e|i|oo?|a)?u?(?:k|w|g|c|o|t)?k?a?(?:ey|ht|ky|e|t|wu|o(?:p|t)?|lacka))"
THRegex = "^next ((h(h{2}|3))|(3h)|(t\w*.?h(a|c|k|h)*))"
tz = timezone('US/Eastern')
thDay = 6
error = ['You need a higher level to use this command','This command is locked, comeback later with higher role', 'Authencation: **Successful**\nAuthorization: **Failed**', 'What are you trying to pull of ? ಠಿ_ಠ', 'Permission denied, bring sudo next time <( ￣^￣)','/usr/bin/sudo: Permission Denied','Ask <@KIITHackClub>']
game = ['with other golems to assert dominance','counting down to the next TH','hack nights','Hack Half Hour', 'Triple H']

def setTime(date, hours, mins, secs):
    date = date.replace(hour=hours, minute=mins, second=secs)
    return date


def THhappeningNow():

    Time = datetime.datetime.now(timezone('Asia/Kolkata'))
    day = int(Time.strftime("%w"))
    hours = int(Time.hour)
    mins = int(Time.minute)

    # Check if Wednesday
    if day == thDay:
        #Check if current time between 19:30 and 20:00 IST
        if (hours > 19 or
            (hours == 19 and mins >= 30)) and (hours < 20 or
                                               (hours == 20 and mins <= 00)):
            return True


def happeningNow():

    Time = datetime.datetime.now(tz)
    day = int(Time.strftime("%w"))
    hours = int(Time.hour)
    mins = int(Time.minute)

    # Check if today is Wednesday
    if day == 3:
        # Check if current time is between 15:30 and 23:59 ET
        if (hours > 15 or
            (hours == 15 and mins >= 30)) and (hours < 23 or
                                               (hours == 23 and mins <= 59)):
            return True

    # Check if today is Saturday
    if day == 6:
        # Check if current time is between 20:30 and 23:59 ET
        if (hours > 20 or
            (hours == 20 and mins >= 30)) and (hours < 23 or
                                               (hours == 23 and mins <= 59)):
            return True
    return False


def THnextDate():
    d = datetime.datetime.now(timezone('Asia/Kolkata'))
    d = d.replace(day=d.day + (((thDay + 7 - int(d.strftime('%w'))) %
                                7)))  # Sets to date of the next Wednesday
    d = setTime(d, 19, 30, 0)
    # Sets time to 19:30 IST
    return d


def nextDate():
    d = datetime.datetime.now(tz)
    today = int(datetime.datetime.now(tz).strftime("%w"))
    if today in range(0, 4):
        d = d.replace(day=d.day + (((3 + 7 - int(d.strftime('%w'))) %
                                    7)))  # Sets to date of the next Wednesday
        d = setTime(d, 15, 30, 0)
        # Sets time to 15:30 Eastern
    elif today in range(4, 7):
        # Today is Thu - Sat
        d = d.replace(day=d.day + (((6 + 7 - int(d.strftime('%w'))) %
                                    7)))  # Sets to date of the next Saturday
        d = setTime(d, 20, 30, 0)
        # Sets time to 20:30 Eastern
    return d


def THgenTimeMessage(textMatch):
    TH = db['TRIPLE_H']
    prompt = ''
    if THhappeningNow():
        prompt = f'_{textMatch[1].title()}_ is happening right now, what are you still doing here!? Join the call!\n{TH}'
    else:
        nextHackNight = THnextDate()
        prompt = f"The next _{textMatch[1]}_ is **{nextHackNight.strftime('%b %d at %I:%M %p')} IST**. See you there!"
    return prompt


def genTimeMessage(textMatch):
    prompt = ''
    if happeningNow():
        prompt = f'_{textMatch[1].title()}_ is happening right now, what are you still doing here!? Join the call!\nhttps://hack.af/night'
    else:
        nextHackNight = nextDate().astimezone(timezone('Asia/Kolkata'))
        prompt = f"The next _{textMatch[1]}_ is **{nextHackNight.strftime('%b %d at %I:%M %p')} IST**. See you there!"
    return prompt


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    checkUpdate.start(client.get_channel(int(os.getenv('CHANNEL_ID'))))
    changeStatus.start()


@client.event
async def on_message(message):
    channel = client.get_channel(int(os.getenv('CHANNEL_ID')))
    if message.author == client.user:
        return

    role = message.author.roles
    possibleRoles = ['Community Manager','Lead','Co-Lead']
    role = [i.name for i in role]
      
    message = message.content
   
    if message.startswith('next set'):
      if any(item in role for item in possibleRoles):
        text = message.split(' ')
        db["TRIPLE_H"] = text[-1]
        await channel.send(f'Meeting link set to {db["TRIPLE_H"]}')
      else:
        await channel.send(f'{random.choice(error)}')
      return

    textMatch = re.search(hackNightRegex, message, re.IGNORECASE)
    if textMatch != None:
        await channel.send(genTimeMessage(textMatch))

    textMatch = re.search(THRegex, message, re.IGNORECASE)
    if textMatch != None:
        await channel.send(THgenTimeMessage(textMatch))


@tasks.loop(seconds=30)
async def checkUpdate(channel):
    prompt = None
    mutex = db['mutex']
    if happeningNow():
        if mutex > 0:
            prompt = f':crescent_moon: It\'s **Hack Night!**\n\nMeet some new people, build something cool, talk about it. There are no prizes or expectations—just have fun!\n\nThe Hack Night call link has been reactivated by yours truly the Night Golem.\n\n:arrow_right: Join Hack Night (https://hack.af/night)'
            mutex -= 1
            await channel.send(prompt)
    elif THhappeningNow():
        TH = db['TRIPLE_H']
        if mutex > 0:
            prompt = f':zap::zap: **Triple H (Hack Half Hour)** :zap::zap:\n\nPresent what you have been hacking on recently while getting to know  your friends at KIIT Hack Club community better.\nTweet and post instagram stories tagging us and get a chance to be featured on our channel :wink:\n\n:arrow_right: Join now {TH}'
            mutex -= 1
            await channel.send(prompt)
    else:
        mutex = 1
    db['mutex'] = mutex

@tasks.loop(minutes=30)
async def changeStatus():
  await client.change_presence(activity=discord.Game(name=random.choice(game)))

client.run(os.getenv('BOT_TOKEN'))
