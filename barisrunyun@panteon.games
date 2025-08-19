import os, discord

# ── ENV / IDs ────────────────────────────────────────────────────────────────
TOKEN = os.getenv("DISCORD_TOKEN")
REGISTER_CHANNEL_ID = int(os.getenv("REGISTER_CHANNEL_ID", "1407288165466898452"))  # #register
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", "1406985699156037734"))            # #player-id-log
VERIFIED_ROLE_ID = int(os.getenv("VERIFIED_ROLE_ID", "1407289000300908735"))

# (opsiyonel) Community Managers iletişim bilgisi:
CM_ROLE_ID = int(os.getenv("CM_ROLE_ID", "0"))             # örn. @Community Managers rol ID
SUPPORT_USER_ID = os.getenv("SUPPORT_USER_ID", "0")        # tek bir yetkili kullanıcı ID (string)

# ── RULES ────────────────────────────────────────────────────────────────────
EXACT_DIGITS = 9  # Player ID must be exactly 9 digits

# ── TEXTS (EN) ───────────────────────────────────────────────────────────────
BRAND = "Raid Rush"
CHANNEL_MENTION = f"<#{REGISTER_CHANNEL_ID}>"
COLOR_OK = 0x57F287

def cm_contact():
    if SUPPORT_USER_ID and SUPPORT_USER_ID.isdigit() and SUPPORT_USER_ID != "0":
        return f"<@{SUPPORT_USER_ID}>"
    if CM_ROLE_ID:
        return f"<@&{CM_ROLE_ID}>"
    return "the Community Managers"

HINT_NONDIGIT = (
    "{mention} Only numbers are allowed. Please send **just your Player ID** in {ch}. "
    "Example: `123456789`"
)
HINT_EXACT = (
    "{mention} Your Player ID must be **exactly {n} digits**. "
    "Send only numbers in {ch}. Example: `123456789`"
)
DM_OK = "✅ Player ID saved and your access has been granted. Enjoy!"

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
    print(f"✅ Login successful: {client.user} (EXACT_DIGITS={EXACT_DIGITS})")

@client.event
async def on_message(message: discord.Message):
    # Ignore bots/DMs
    if message.author.bot or not message.guild:
        return
    # Only listen in registration channel
    if message.channel.id != REGISTER_CHANNEL_ID:
        return

    content = message.content.strip()

    # Always delete for privacy
    try:
        await message.delete()
    except:
        pass

    guild = message.guild
    verified_role = guild.get_role(VERIFIED_ROLE_ID)
    is_verified = verified_role in message.author.roles if verified_role else False
    log_ch = guild.get_channel(LOG_CHANNEL_ID)
    uid = message.author.id

    # ── ONE-TIME REGISTRATION: block updates ─────────────────────────────────
    if is_verified:
        text = (
            f"{message.author.mention} You are **already verified**. "
            f"Updates are disabled. Please DM {cm_contact()} to request a change."
        )
        await send_temp(message.channel, text)
        # (opsiyonel) log the attempt
        if log_ch:
            try:
                await log_ch.send(f"⛔ Update attempt blocked for <@{uid}>. Typed `{content}`")
            except:
                pass
        return

    # ── VALIDATION (exactly 9 digits) ────────────────────────────────────────
    if not content.isdigit():
        await send_temp(message.channel, HINT_NONDIGIT.format(mention=message.author.mention, ch=CHANNEL_MENTION))
        return
    if len(content) != EXACT_DIGITS:
        await send_temp(
            message.channel,
            HINT_EXACT.format(mention=message.author.mention, ch=CHANNEL_MENTION, n=EXACT_DIGITS)
        )
        return

    player_id = content  # valid

    # ── LOG (plain text with @mention so it always tags) ─────────────────────
    if log_ch:
        try:
            await log_ch.send(f"<@{uid}> player id `{player_id}`")
        except:
            pass

    # ── ROLE (assign now) ────────────────────────────────────────────────────
    try:
        if verified_role:
            await message.author.add_roles(verified_role, reason="Player ID verified")
    except Exception as e:
        if log_ch:
            await log_ch.send(f"⚠️ Could not assign role to <@{uid}>: `{e}`")

    # ── DM confirm ───────────────────────────────────────────────────────────
    try:
        emb_ok = discord.Embed(description=DM_OK, color=COLOR_OK)
        emb_ok.set_author(name=f"{BRAND} Verify")
        emb_ok.add_field(name="Player ID", value=f"`{player_id}`", inline=True)
        await message.author.send(embed=emb_ok)
    except:
        await send_temp(message.channel, f"{message.author.mention} Verified. Welcome!")

client.run(TOKEN)
