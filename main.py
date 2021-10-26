from discord.ext import commands
from discord.ext.commands.context import Context
from discord.ext.commands import CommandNotFound
from discord.ext.commands.errors import BadArgument

from os import getenv
from discord.user import User

from dotenv import load_dotenv

from functions.format import formatNb
from functions.factorize import factorize
from functions.roll import roll

from Classes.Game import Game

load_dotenv()

DISCORD_TOKEN = getenv("DISCORD_TOKEN")

bot = commands.Bot(command_prefix=";")

active_games = {}

@bot.event
async def on_ready():
    print("We have logged in as {0.user}".format(bot))


@bot.command(aliases=["r", "roll"])
async def rollCommand(ctx: Context, max: int = 100):
    number = roll(max)

    if ctx.guild.id in active_games:
        game: Game = active_games[ctx.guild.id]

        if not ctx.author.id in game.players:
            game.players[ctx.author.id] = 1

        if max == game.players[ctx.author.id]:
            if number == game.players[ctx.author.id]:
                game.players[ctx.author.id] += 1
                percentage = formatNb(1/factorize(max))

                await ctx.send(f"🎉🎉 {number} 🎉🎉 {f'({percentage})' if percentage != '0%' else ''}")
        

                if game.players[ctx.author.id] - 1 == game.max:
                    await ctx.send(f"La partie est terminé ! Le vainqueur est {ctx.author.name}")

                    for player_id, curr in game.players.items():
                        player: User = await bot.fetch_user(player_id)

                        await ctx.send(f"{player.name} : {curr - 1}")
                        
                    del active_games[ctx.guild.id]

                return
            
    await ctx.send(number)


@bot.command(aliases=["start"])
async def startGame(ctx: Context, max: int = 20):
    active_games[ctx.guild.id] = Game(max)
    await ctx.send(f"Partie commencé ! Elle durera jusqu'a ce que quelqu'un atteigne {max}")


@bot.command(aliases=["stop"])
async def stopGame(ctx: Context):
    del active_games[ctx.guild.id]
    await ctx.send("Partie arreté par un modérateur !!")
   

@bot.event
async def on_command_error(ctx: Context, error):
    if isinstance(error, CommandNotFound):
        return

    if isinstance(error, BadArgument):
        return

    raise error

if __name__ == '__main__':
    bot.run(DISCORD_TOKEN)