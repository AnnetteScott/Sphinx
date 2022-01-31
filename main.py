#import discord #import all the necessary modules
from discord.ext import commands, tasks
import os
from datetime import datetime, timedelta
import json
from dotenv import load_dotenv
load_dotenv()

bot = commands.Bot(command_prefix='!') #define command decorator

userCommands = ['helpMe', 'hello', 'createReminder', 'reminders', 'DELremind']
channelIDs = {'sphinx':937053360702509126, 'general':936900906488827936, 'links':936905539739353128, 'important-docs':936905648128532540, 'food':936905748447895552, 'bills':936918392076664873}
reminderDICT = {}


@bot.event
async def on_message(message):
    await bot.process_commands(message)

#Show list of commands
@bot.command(pass_context=True)
async def helpMe(ctx):
    await ctx.channel.send('The available commands are:')
    new_message = "" 
    for com in userCommands:
        new_message += com + ", "
    await ctx.channel.send(new_message) 
    

#Say Hello
@bot.command(pass_context=True)
async def hello(ctx):
    await ctx.send('Hello Da Bebe!')

@bot.command()
async def createReminder(ctx):
    with open('reminders.json', 'r') as openfile:
        # Reading from json file
        reminderDICT = json.load(openfile)

    def check(msg):
        return msg.author.id == ctx.author.id and msg.channel.id == ctx.channel.id

    await ctx.channel.send("What is the name of your reminder?")
    name = (await bot.wait_for('message', check = check)).content
    while name in reminderDICT.keys():
        await ctx.channel.send("That name already exists! Please type a new name:")
        name = (await bot.wait_for('message', check = check)).content

    await ctx.channel.send("When does the reminder first occur? (dd/mm/yy format)")
    first_date = (await bot.wait_for('message', check = check)).content

    await ctx.channel.send("What channel would you like this reminder to occur in?")
    channel = await bot.wait_for('message', check = check)
    channel = channel.content
    while channel not in channelIDs.keys():
        await ctx.channel.send(channel + " is unavailable or does not exist. Please type new channel:")
        channel = await bot.wait_for('message', check = check)

    await ctx.channel.send("Does the reminder repeat? (yes/no)")
    repeating = (await bot.wait_for('message', check = check)).content
    how_often = ''
    if('yes' in repeating or 'yep' in repeating):
        await ctx.channel.send("Does the reminder reapeat daily, weekly, monthly or yearly?")
        ans = (await bot.wait_for('message', check = check)).content
        if 'daily' in ans:
            how_often = 'daily'
        elif 'weekly' in ans:
            how_often = 'weekly'
        elif 'monlthy' in ans:
            how_often = 'monthly'
        elif 'yearly' in ans:
            how_often = 'yearly'
        await ctx.channel.send("Great! I've added the reminder!")
    else:
        await ctx.channel.send("Ok! The reminder won't repeat and I've added it!")
        repeating = False

    reminderDICT[name] = {'first date': first_date, 'repeat': how_often, 'channel': channel, "next date": first_date}
    # Serializing json 
    json_object = json.dumps(reminderDICT, indent = 4)
    
    # Writing to sample.json
    with open("reminders.json", "w") as outfile:
        outfile.write(json_object)


@bot.command(pass_context=True)
async def reminders(ctx):
    with open('reminders.json', 'r') as openfile:
        # Reading from json file
        reminderDICT = json.load(openfile)
    reminder_keys = reminderDICT.keys()
    if reminderDICT != {}:
        await ctx.channel.send('Your current reminders are:')
        for key in reminder_keys:
            await ctx.channel.send(str(key))
        await ctx.channel.send('That is all of your reminders')
    else:
        await ctx.channel.send('You have no reminders')


@tasks.loop(minutes=80)
async def reminder_due():
    reminder_keys = reminderDICT.keys()
    if reminderDICT != {}:
        for key in reminder_keys:
            today_date = str(datetime.now() + timedelta(hours=13)).split(" ")[0].split('-')
            user_todayDate = today_date[2] + "/" + today_date[1] + "/" + today_date[0][2:]
            reminder_date = reminderDICT[key][0]
            if user_todayDate == reminder_date:
                channel = bot.get_channel(reminderDICT[key][2])
                how_often = reminderDICT[key][1].split(' ')
                daily = int(how_often[0].split('d')[0])
                montly = int(how_often[1].split('m')[0])
                year = int(how_often[2].split('y')[0])
                get_new_date(key, reminder_date, daysAdd=daily, monthly=montly, yearly=year)
                await channel.send(key + " is occuring/due today!")
                next_date = reminderDICT[key][0]
                await channel.send("It will next occur on: " + str(next_date))


def get_new_date(key, date, daysAdd=0, monthsAdd=0, yearsAdd=0, monthly=0, yearly=0):
    oDay = int(date.split("/")[0])
    oMonth = int(date.split("/")[1])
    oYear = int(date.split("/")[2])

    nDays = oDay + daysAdd
    nMonth = oMonth + monthly + monthsAdd
    nYear = oYear + yearly + yearsAdd
    if nMonth > 12:
        nYear += (nMonth // 12)
        nMonth = nMonth % 12
        

    while nDays > get_month_day(nMonth):
        #nMonth += 1
        nDays -= get_month_day(nMonth)
        nMonth += 1

    fMonth = nMonth % 12
    fYear = nYear + (nMonth // 12)
    fDays = nDays

    if nDays < 10:
        fDays = "0" + str(nDays)

    fDate = str(fDays) + '/' + str(fMonth) + '/' + str(fYear)
    db_object = reminderDICT[key]
    reminderDICT[key] = [fDate, db_object[1], db_object[2]]


def get_month_day(month):
    if month == 1: #Jan
        return 31
    elif month == 2: #Feb
        return 28
    elif month == 3: #Mar
        return 31
    elif month == 4: #Apr
        return 30
    elif month == 5: #May
        return 31
    elif month == 6: #Jun
        return 30
    elif month == 7: #Jul
        return 31
    elif month == 8: #Aug
        return 31
    elif month == 9: #Sep
        return 30
    elif month == 10: #Oct
        return 31
    elif month == 11: #Nov
        return 30
    elif month == 12: #Dec
        return 31
    else:
        return 30
    

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    with open('reminders.json', 'r') as openfile:
        # Reading from json file
        reminderDICT = json.load(openfile)
    reminder_due.start()


bot.run(os.getenv('TOKEN'))