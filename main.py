from discord.ext import commands
from discord.ext.commands.context import Context
from discord.ext.commands import CommandNotFound
from discord.ext.commands.errors import BadArgument
from discord.user import User
from discord.guild import Guild
from discord.abc import GuildChannel

from os import getenv

from dotenv import load_dotenv

from functions.roll import roll

from Classes.Game import Game

load_dotenv()

DISCORD_TOKEN = getenv("DISCORD_TOKEN")

bot = commands.Bot(command_prefix=";")

GAMES_TYPES = ["SOLO", "TEAM"]

active_games = {}

@bot.event
async def on_ready():
    print("We have logged in as {0.user}".format(bot))

@bot.command(aliases=["r", "roll"])
async def rollCommand(ctx: Context, max: int = 100):
    number = roll(max)

    if ctx.guild.id in active_games:
        game: Game = active_games[ctx.guild.id]

        id_ = None

        if game.type == "TEAM" :
            if ctx.channel.id == game.team1_id:
                id_ = "team1"
            elif ctx.channel.id == game.team2_id:
                id_ = "team2"
        else:
            id_ = ctx.author.id

        if not id_ in game.players:
            game.players[id_] = 1

        if max == game.players[id_]:
            if id_ is not None:
                if number == game.players[id_]:
                    game.players[id_] += 1

                    str_number = f"🎉🎉 {number} 🎉🎉 {f'({1/number:.1%})'}"

                    if "team" in str(id_):
                        await ctx.send(f"La Team {id_[len(id_)-1:]}" + " a fait: " + str_number)
                    else:
                        await ctx.send(ctx.author.name+ " a fait: " + str_number)

                    if game.players[id_] - 1 == game.max:
                        await ctx.send(f"La partie est terminé ! Le vainqueur est {'la Team' + str(id_)[len(str(id_))-1:] if 'team' in str(id_) else ctx.author.name}")

                        for key, curr in game.players.items():
                            if curr != game.players[id_]:
                                if "team" in str(id_):
                                    await ctx.send(f"{key} : {curr - 1}")
                                else: 
                                    player: User = await bot.fetch_user(key)

                                    await ctx.send(f"{player.name} : {curr - 1}")
                        del active_games[ctx.guild.id]
                    return

            
    await ctx.send(ctx.author.name + " a fait: " + str(number))

@bot.command(aliases=["start"])
async def startGame(ctx: Context, *args):
    max: int = 20
    game_type: str = "SOLO"

    for arg in args:
        if arg.isnumeric():
            max = int(arg)
        else:
            if arg.upper() in GAMES_TYPES:
                game_type = arg.upper()

    team1_id = 0
    team2_id = 0

    if game_type == "TEAM":
        guild: Guild = ctx.guild

        channels: list[GuildChannel] = await guild.fetch_channels()

        if not any(channel for channel in channels if channel.name == "team1"):
            new_channel = await guild.create_text_channel("team1")
            team1_id = new_channel.id
        if not any(channel for channel in channels if channel.name == "team2"):
            new_channel = await guild.create_text_channel("team2")
            team2_id = new_channel.id

    active_games[ctx.guild.id] = Game(max=max, game_type=game_type, team1_id = team1_id, team2_id = team2_id)
    if game_type == "TEAM":
        active_games[ctx.guild.id].players["team1"] = 1
        active_games[ctx.guild.id].players["team2"] = 1

    await ctx.send(f"Partie commencé ! Elle durera jusqu'a ce que quelqu'un atteigne {max}")


@bot.command(aliases=["stop"])
async def stopGame(ctx: Context):
    if active_games[ctx.guild.id].type == "TEAM":
        guild: Guild = ctx.guild

        # Remove channel team1
        channel1: GuildChannel = guild.get_channel(active_games[ctx.guild.id].team1_id)
        await channel1.delete()

        # Remove channel team2
        channel2: GuildChannel = guild.get_channel(active_games[ctx.guild.id].team2_id)
        await channel2.delete()
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