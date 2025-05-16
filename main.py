import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import os

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="/", intents=intents)
GUILD_ID = int(os.getenv("GUILD_ID"))

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    try:
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f'Synced {len(synced)} slash commands.')
    except Exception as e:
        print(e)

@bot.tree.command(name="requestarv", description="Request a partner to double crew for ARV", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(message="Optional message for your request")
async def requestarv(interaction: discord.Interaction, message: str = "No additional message."):
    role = discord.utils.get(interaction.guild.roles, name="ARV")  # Uses ARV role
    channel = discord.utils.get(interaction.guild.text_channels, name="arv-requests")

    if not channel or not role:
        await interaction.response.send_message("Role or channel not found.", ephemeral=True)
        return

    embed = discord.Embed(
        title="🚨 ARV Double Crew Request",
        description=f"{interaction.user.mention} is requesting a partner for ARV duty.\n\n**Message:** {message}",
        color=discord.Color.red()
    )
    embed.set_footer(text="This request will expire in 1 hour.")

    msg = await channel.send(content=role.mention, embed=embed)
    await msg.add_reaction("✅")

    await interaction.response.send_message("Your ARV request has been posted and will expire in 1 hour.", ephemeral=True)

    await asyncio.sleep(3600)

    msg = await channel.fetch_message(msg.id)
    reaction = discord.utils.get(msg.reactions, emoji="✅")

    responders = []
    if reaction:
        users = await reaction.users().flatten()
        responders = [user.mention for user in users if not user.bot]

    responder_text = ", ".join(responders) if responders else "No one responded."

    expired_embed = discord.Embed(
        title="❌ ARV Request Expired",
        description=f"{interaction.user.mention}'s request for a partner has expired.\n\n**Responders:** {responder_text}",
        color=discord.Color.dark_gray()
    )
    expired_embed.set_footer(text="Request expired after 1 hour.")

    await msg.edit(content="(Expired)", embed=expired_embed)

bot.run(os.getenv("TOKEN"))
