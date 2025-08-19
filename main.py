import os, re, discord
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")
REGISTER_CHANNEL_ID = int(os.getenv("REGISTER_CHANNEL_ID", "1407288165466898452"))
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", "1406985699156037734"))
VERIFIED_ROLE_ID = int(os.getenv("VERIFIED_ROLE_ID", "1407289000300908735"))

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
ID_REGEX = re.compile(r"^\s*(\d{6,20})\s*$")  # only numbers (6–20)

@bot.event
async def on_ready():
    print(f"✅ Login successful: {bot.user}")

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot or not message.guild:
        return
    if message.channel.id != REGISTER_CHANNEL_ID:
        return

    try:
        await message.delete()  # privacy: delete message immediately
    except:
        pass

    verified = message.guild.get_role(VERIFIED_ROLE_ID)
    if verified and verified in message.author.roles:
        return

    m = ID_REGEX.match(message.content)
    if not m:
        try:
            await message.author.send("I couldn't find your ID. Please write only numbers in a single line.: `123456789`")
        except:
            pass
        return

    player_id = m.group(1)

    log_ch = bot.get_channel(LOG_CHANNEL_ID)
    if log_ch:
        dn = message.author.display_name
        await log_ch.send(f"**{dn}** player id `{player_id}`")

    try:
        if verified and verified not in message.author.roles:
            await message.author.add_roles(verified, reason="Player ID verified")
    except Exception as e:
        if log_ch:
            await log_ch.send(f"⚠️ No role assigned → {message.author.mention} · Hata: `{e}`")

    try:
        await message.author.send("✅ Player ID has been retrieved and access has been granted. Enjoy!")
    except:
        pass

bot.run(TOKEN)
