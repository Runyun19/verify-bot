import os, discord

# ── ENV / IDs ────────────────────────────────────────────────────────────────
TOKEN = os.getenv("DISCORD_TOKEN")
REGISTER_CHANNEL_ID = int(os.getenv("REGISTER_CHANNEL_ID", "1407288165466898452"))  # #kayit
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", "1406985699156037734"))            # #player-id-log
VERIFIED_ROLE_ID = int(os.getenv("VERIFIED_ROLE_ID", "1407289000300908735"))

# ── RULES ────────────────────────────────────────────────────────────────────
EXACT_DIGITS = 9  # ⟵ tam 9 hane zorunlu

# ── TEXTS (EN) ───────────────────────────────────────────────────────────────
BRAND = "Raid Rush"
CHANNEL_MENTION = f"<#{REGISTER_CHANNEL_ID}>"

HINT_EXACT = (
    "{mention} Your Player ID must be **exactly {n} digits**. "
    "Send only numbers in {ch}. Example: `123456789`"
)
HINT_NONDIGIT = (
    "{mention} Only numbers allowed. Please send just your Player ID in {ch}. "
    "Example: `123456789`"
)
DM_OK = "✅ Player ID saved and your access has been granted. Enjoy!"

COLOR_OK   = 0x57F287  # green
COLOR_WARN = 0xFEE75C  # yellow

# ── BOT ──────────────────────────────────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents)

async def send_temp(channel: discord.TextChannel, text: str):
    try:
        return await channel.send(text, delete_after=10)
    except:
        return None

@client.event
async def on_ready():
    print(f"✅ Login successful: {client.user}")

@client.event
async def on_message(message: discord.Message):
    # Ignore bots/DMs
    if message.author.bot or not message.guild:
        return
    # Only listen in the registration channel
    if message.channel.id != REGISTER_CHANNEL_ID:
        return

    content = message.content.strip()

    # Always delete user's message for privacy
    try:
        await message.delete()
    except:
        pass

    guild = message.guild
    verified_role = guild.get_role(VERIFIED_ROLE_ID)
    had_role = verified_role in message.author.roles if verified_role else False

    # ---------- VALIDATION ----------
    if not content.isdigit():
        await send_temp(
            message.channel,
            HINT_NONDIGIT.format(mention=message.author.mention, ch=CHANNEL_MENTION)
        )
        return

    if len(content) != EXACT_DIGITS:
        await send_temp(
            message.channel,
            HINT_EXACT.format(mention=message.author.mention, ch=CHANNEL_MENTION, n=EXACT_DIGITS)
        )
        return

    player_id = content  # valid 9-digit ID

    # ---------- LOG (mention the user directly) ----------
    log_ch = guild.get_channel(LOG_CHANNEL_ID)
    uid = message.author.id
    if log_ch:
        try:
            emb_title = "Verification" if not had_role else "ID Update"
            emb = discord.Embed(title=emb_title, color=COLOR_OK)
            emb.description = f"<@{uid}>"
            emb.add_field(name="Player ID", value=f"`{player_id}`", inline=True)
            await log_ch.send(embed=emb)
        except:
            await log_ch.send(f"<@{uid}> player id `{player_id}`")

    # ---------- ROLE (assign if not already) ----------
    try:
        if verified_role and not had_role:
            await message.author.add_roles(verified_role, reason="Player ID verified")
    except Exception as e:
        if log_ch:
            await log_ch.send(f"⚠️ Could not assign role to <@{uid}>: `{e}`")

    # ---------- DM confirm ----------
    try:
        emb_ok = discord.Embed(description=DM_OK, color=COLOR_OK)
        emb_ok.set_author(name=f"{BRAND} Verify")
        emb_ok.add_field(name="Player ID", value=f"`{player_id}`", inline=True)
        await message.author.send(embed=emb_ok)
    except:
        # If DMs are closed, show a brief success in channel
        await send_temp(message.channel, f"{message.author.mention} Verified. Welcome!")

client.run(TOKEN)
