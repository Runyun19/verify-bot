import os, re, csv, discord
from pathlib import Path

# ── ENV / IDs ────────────────────────────────────────────────────────────────
TOKEN = os.getenv("DISCORD_TOKEN")

REGISTER_CHANNEL_ID = 1407288165466898452   # #special-reward
LOG_CHANNEL_ID = 1406985699156037734        # #player-id-log

# ── RULES ────────────────────────────────────────────────────────────────────
EXACT_DIGITS = 9  # Player ID must be exactly 9 digits

# ── TEXTS (English only) ─────────────────────────────────────────────────────
BRAND = "Raid Rush"
CHANNEL_MENTION = f"<#{REGISTER_CHANNEL_ID}>"
COLOR_OK = 0x57F287

EMAIL_RE = re.compile(r"^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$", re.I)

HINT_FORMAT = (
    "{mention} Please send your **email and Player ID** in one message separated by space.\n"
    "Example: `email@example.com 123456789`"
)
HINT_INVALID_EMAIL = "{mention} Invalid email format. Please try again.\n" + HINT_FORMAT
HINT_INVALID_DIGITS = "{mention} Player ID must contain only digits. Please try again."
HINT_INVALID_LENGTH = "{mention} Player ID must be exactly {n} digits. Please try again."
HINT_ALREADY_SUBMITTED = "{mention} You have **already submitted** your information. Updates are disabled."
DM_OK = "✅ Your information has been saved. Your code will be sent by email."

# ── PERSISTENCE (CSV) ────────────────────────────────────────────────────────
SAVE_PATH = Path("submissions.csv")

def load_submitted_user_ids() -> set[int]:
    ids = set()
    if SAVE_PATH.exists():
        try:
            with SAVE_PATH.open("r", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Expecting columns: discord_user_id,email,player_id
                    uid_str = row.get("discord_user_id")
                    if uid_str and uid_str.isdigit():
                        ids.add(int(uid_str))
        except Exception:
            pass
    return ids

def append_submission(discord_user_id: int, email: str, player_id: str):
    file_exists = SAVE_PATH.exists()
    with SAVE_PATH.open("a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["discord_user_id", "email", "player_id"])
        writer.writerow([discord_user_id, email, player_id])

# ── BOT ──────────────────────────────────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents)

# In-memory cache of users who already submitted (also prefilled from CSV)
submitted_users = set()

async def send_temp(channel: discord.TextChannel, text: str):
    try:
        return await channel.send(text, delete_after=10)
    except:
        return None

@client.event
async def on_ready():
    global submitted_users
    submitted_users = load_submitted_user_ids()
    print(f"✅ Login successful: {client.user} (EXACT_DIGITS={EXACT_DIGITS})")
    print(f"Loaded {len(submitted_users)} submitted user(s) from CSV.")

@client.event
async def on_message(message: discord.Message):
    # Ignore bots/DMs
    if message.author.bot or not message.guild:
        return
    # Only listen in the registration channel
    if message.channel.id != REGISTER_CHANNEL_ID:
        return

    content = message.content.strip()

    # Always delete for privacy
    try:
        await message.delete()
    except:
        pass

    log_ch = message.guild.get_channel(LOG_CHANNEL_ID)
    uid = message.author.id

    # One-time submission check
    if uid in submitted_users:
        await send_temp(message.channel, HINT_ALREADY_SUBMITTED.format(mention=message.author.mention))
        if log_ch:
            try:
                await log_ch.send(f"⛔ Duplicate submission attempt by <@{uid}>. Typed `{content}`")
            except:
                pass
        return

    # Parse input: "email@example.com 123456789"
    parts = content.replace("\n", " ").split()
    if len(parts) != 2:
        await send_temp(message.channel, HINT_FORMAT.format(mention=message.author.mention))
        return

    email, player_id = parts[0].strip(), parts[1].strip()

    # Validate
    if not EMAIL_RE.fullmatch(email):
        await send_temp(message.channel, HINT_INVALID_EMAIL.format(mention=message.author.mention))
        return

    if not player_id.isdigit():
        await send_temp(message.channel, HINT_INVALID_DIGITS.format(mention=message.author.mention))
        return

    if len(player_id) != EXACT_DIGITS:
        await send_temp(
            message.channel,
            HINT_INVALID_LENGTH.format(mention=message.author.mention, n=EXACT_DIGITS)
        )
        return

    # Mark as submitted (memory + CSV)
    submitted_users.add(uid)
    try:
        append_submission(uid, email, player_id)
    except Exception as e:
        # Failing to write CSV shouldn't block the flow; still proceed
        if log_ch:
            await log_ch.send(f"⚠️ CSV write error for <@{uid}>: `{e}`")

    # Log valid submission (private channel)
    if log_ch:
        try:
            emb = discord.Embed(title="New Submission", color=0x3498DB)
            emb.add_field(name="Discord", value=f"{message.author} (`{uid}`)", inline=False)
            emb.add_field(name="Email", value=email, inline=True)
            emb.add_field(name="Player ID", value=player_id, inline=True)
            await log_ch.send(embed=emb)
        except:
            await log_ch.send(f"<@{uid}> email `{email}` | player id `{player_id}`")

    # DM confirmation (English only)
    try:
        emb_ok = discord.Embed(description=DM_OK, color=COLOR_OK)
        emb_ok.set_author(name=f"{BRAND} Verify")
        emb_ok.add_field(name="Email", value=email, inline=True)
        emb_ok.add_field(name="Player ID", value=f"`{player_id}`", inline=True)
        await message.author.send(embed=emb_ok)
    except:
        await send_temp(message.channel, f"{message.author.mention} Saved successfully.")

client.run(TOKEN)
