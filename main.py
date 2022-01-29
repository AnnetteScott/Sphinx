import discord #import all the necessary modules
from discord.ext import commands
import os
from dotenv import load_dotenv
load_dotenv()
bot = commands.Bot(command_prefix='!') #define command decorator

userCommands = ['helpMe', 'hello', 'remind', 'remindHelp', 'reminders', 'channelID']
reminder_dict = {}


@bot.event
async def on_message(message):
    if message.content.startswith('!remind'):
        content = message.content.split(", ")
        name = content[1]
        date = content[2]
        how_often = content[3]
        channel = content[4]
        reminder_dict[date] = [name, how_often, channel]
        await message.channel.send('I have added: ' + name + ' to the list')
    else:
        await bot.process_commands(message)


@bot.command(pass_context=True)
async def helpMe(ctx):
    await ctx.channel.send('The available commands are:')
    new_message = "" 
    for com in userCommands:
        new_message += com + ", "
    await ctx.channel.send(new_message) 
    

@bot.command(pass_context=True)
async def hello(ctx):
    await ctx.send('Hello Da Bebe!')


@bot.command(pass_context=True)
async def reminders(ctx):
    await ctx.channel.send('Your current reminders are:')
    new_message = "" 
    if reminder_dict != {}:
        for rem in reminder_dict.keys():
            new_message += reminder_dict[rem][0] + ", "
        await ctx.channel.send(new_message)
    else:
        await ctx.channel.send('You have no reminders')



@bot.command(pass_context=True)
async def remindHelp(ctx):
   await ctx.channel.send('Formating to add a new reminder: !remind, name, date in dd/mm/yy, how often in xday, xmonth or xyear, channelID(use !channelID to get the ID')



@bot.command(pass_context=True)
async def channelID(ctx):
   await ctx.channel.send(ctx.channel)






@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    
bot.run(os.getenv('TOKEN'))  #run the client using using my bot's token