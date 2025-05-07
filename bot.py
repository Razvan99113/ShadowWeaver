import discord
from discord.ext import commands, tasks
import asyncio
import random
import yt_dlp
import datetime
from PIL import Image, ImageDraw, ImageFont
import io

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

KING_ID = 553513089199374338
PATRON_ID = 458879133523509250
LEGIONAR_ROLE_NAME = "Legionar"

MUZICA_SENTINTA = "https://youtu.be/RT-5Tj-Mv-w?t=13"

CHANNEL_ONE_ID = 1332104647414124616
CHANNEL_TWO_ID = 1332104684642766931

ALLOWED_CHANNEL_ID = 1332190062099697675
RUGACIUNE_CHANNEL_ID = 1369619919901294643
PUSCARIE_CHANNEL_ID = 1332881899005411339

lachire_verification = {}
looping_users = {}
member_to_channel = {}
song_queue = []

yt_dlp.utils.bug_reports_message = lambda: ""
ytdl_format_options = {
    "format": "bestaudio/best",
    "noplaylist": True,
}
ffmpeg_options = {
    "options": "-vn",
}
ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

async def download_audio(url, loop=None, stream=True):
    """Download or stream audio using yt-dlp."""
    loop = loop or asyncio.get_event_loop()
    data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
    if "entries" in data:
        data = data["entries"][0]
    filename = data["url"] if stream else ytdl.prepare_filename(data)
    return filename, data.get("title")

@bot.event
async def on_ready():
    print(f"Sir, yes sir {bot.user}")

bot.remove_command("help")

def is_allowed_channel(ctx):
    """Check if the command is from the allowed text channel."""
    return ctx.channel.id == ALLOWED_CHANNEL_ID

def is_king(member: discord.Member) -> bool:
    """Check if the member is the KING."""
    if member.id == KING_ID:
        return True
    elif member.id == PATRON_ID:
        return True 

@bot.event
async def on_command(ctx):
    print(f"Command '{ctx.command}' was used by {ctx.author.display_name} {ctx.author} ({ctx.author.id})")

@bot.event
async def on_voice_state_update(member, before, after):
    if member.id in member_to_channel:
        target_channel = member_to_channel[member.id]
        if after.channel != target_channel:
            await member.move_to(target_channel)
            print(f"Moved {member.name} back to {target_channel.name}", delete_after = 5)

@bot.command()
async def gay(ctx, mention: discord.Member):

    if is_king(mention):
        percentage = random.randint(0, 30)
    else:
        percentage = random.randint(50, 100)
        await ctx.send(f"{mention.mention} is {percentage}% gay")

@bot.command()
async def join(ctx):
    """Make the bot join the voice channel."""

    if not is_allowed_channel(ctx):
        await ctx.send("Ai drepturi patroane?", delete_after = 5)
        return
    if not ctx.author.voice:
        return await ctx.send("You need to be in a voice channel for me to join!", delete_after = 5)
    channel = ctx.author.voice.channel
    if ctx.voice_client:
        if ctx.voice_client.channel == channel:
            return await ctx.send("I'm already connected to your voice channel!", delete_after = 5)
        else:
            await ctx.voice_client.move_to(channel)
            return await ctx.send(f"Moved to {channel.name}!", delete_after = 5)
    try:
        await channel.connect()
        await ctx.send(f"Connected to {channel.name}!", delete_after = 5)
    except Exception as e:
        await ctx.send(f"An error occurred while connecting: {e}", delete_after = 5)

@bot.command()
async def leave(ctx):
    """Make the bot leave the voice channel."""

    if not is_allowed_channel(ctx):
        await ctx.send("Ai drepturi patroane?", delete_after = 5)
        return

    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected from the voice channel.", delete_after = 5)
    else:
        await ctx.send("I'm not in a voice channel!", delete_after = 5)

@bot.command()
async def play(ctx, url):
    """Play a song from a YouTube URL, queue it if one is playing."""
    
    if not is_allowed_channel(ctx):
        await ctx.send("Ai drepturi patroane?", delete_after = 5)
        return
    if not ctx.author.voice:
        return await ctx.send("You need to be in a voice channel for me to join!", delete_after = 5)

    channel = ctx.author.voice.channell
    if not ctx.voice_client:
        await channel.connect()
        await ctx.send(f"Joined {channel.name}!", delete_after = 5)
    elif ctx.voice_client.channel != channel:
        await ctx.voice_client.move_to(channel)
        await ctx.send(f"Moved to {channel.name}!", delete_after = 5)
    song_queue.append(url)
    if not ctx.voice_client.is_playing():
        await play_next_song(ctx)
    else:
        await ctx.send(f"Queued: {url}", delete_after = 30)

async def play_next_song(ctx):
    """Play the next song in the queue."""

    if not is_allowed_channel(ctx):
        await ctx.send("Ai drepturi patroane?", delete_after = 5)
        return

    if song_queue:
        url = song_queue.pop(0)
        async with ctx.typing():
            try:
                filename, title = await download_audio(url, loop=bot.loop, stream=True)
                ctx.voice_client.play(
                    discord.FFmpegPCMAudio(filename, **ffmpeg_options),
                    after=lambda e: asyncio.run_coroutine_threadsafe(play_next_song(ctx), bot.loop) if not e else None
                )
                await ctx.send(f"Now playing: {title}", delete_after = 30)
            except Exception as e:
                await ctx.send(f"An error occurred: {e}", delete_after = 5)
    else:
        await ctx.send("The queue is empty.", delete_after = 5)

@bot.command()
async def stop(ctx):
    """Stop the currently playing song."""

    if not is_allowed_channel(ctx):
        await ctx.send("Ai drepturi patroane?", delete_after = 5)
        return

    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Music stopped.", delete_after = 5)
    else:
        await ctx.send("No music is playing right now.", delete_after = 5)

@bot.command()
async def pause(ctx):
    """Pause the current song."""

    if not is_allowed_channel(ctx):
        await ctx.send("Ai drepturi patroane?", delete_after = 5)
        return

    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("Music paused.", delete_after = 5)
    else:
        await ctx.send("No music is playing to pause.", delete_after = 5)

@bot.command()
async def resume(ctx):
    """Resume the paused song."""

    if not is_allowed_channel(ctx):
        await ctx.send("Ai drepturi patroane?", delete_after = 5)
        return

    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("Music resumed.", delete_after = 5)
    else:
        await ctx.send("There's no music paused right now.", delete_after = 5)

@bot.command()
async def inchisoare(ctx, member: discord.Member):
    """Puscarie pentru salahor (tine user-ul captiv pe un canal)"""
    
    if is_king(member):
        try:
            await play(ctx, MUZICA_SENTINTA)
        except Exception as e:
            await ctx.send(f"Ceva n-a mers bine cu muzica: {str(e)}")
        
        await asyncio.sleep(40)
        try:
            duration = 600
            await ctx.author.timeout(discord.utils.utcnow() + datetime.timedelta(seconds=duration), reason="Cui dai tu inchisoare rege?")
        except discord.HTTPException as e:
            await print(f"Ceva nu a mers bine: {str(e)}")

        try:
            await leave(ctx)
        except discord.HTTPException as e:
            await print(f"Ceva nu a mers bine: {str(e)}")
        return

    if not is_allowed_channel(ctx):
        await ctx.send("Ai drepturi patroane?", delete_after = 5)
        return

    channel = bot.get_channel(PUSCARIE_CHANNEL_ID)

    await member.move_to(channel)
    member_to_channel[member.id] = channel
    await ctx.send(f"Puscarie pe viata pentru {member.name}", delete_after = 5)

@bot.command()
async def eliberare(ctx, member: discord.Member):
    """Anuleaza comanda de puscarie"""

    if ctx.author.id in member_to_channel:
        ctx.send("Cand vreodata poti sa mi spui tu cand sa te eliberez salahorule?")
        return

    if not is_allowed_channel(ctx):
        await ctx.send("Ai drepturi patroane?", delete_after = 5)
        return
    if member.id in member_to_channel:
        del member_to_channel[member.id]
        await ctx.send(f"Salahorul {member.name} eliberat", delete_after = 5)
    else:
        await ctx.send(f"{member.name} nu e puscarias.", delete_after = 5)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.channel.id != RUGACIUNE_CHANNEL_ID:
        await bot.process_commands(message)
        return

    roles = [role.name for role in message.author.roles]
    if "Sclav" not in roles and "Sclav Premium" not in roles:
        await bot.process_commands(message)
        return

    author_id = message.author.id
    content = message.content.strip()

    expected_trigger = f"Te rog frumos, regele meu, lasa-ma sa intru si eu {bot.user.mention}"

    # Step 1: Trigger message
    if content == expected_trigger:
        await message.channel.send(f"{message.author.mention}, răspunde sincer: Ce esti tu?")
        lachire_verification[author_id] = True
        await bot.process_commands(message)
        return

    # Step 2: Answer to bot's question
    if author_id in lachire_verification:
        if content.lower() == "o pizda lachita":
            guild = message.guild
            role = discord.utils.get(guild.roles, name=LEGIONAR_ROLE_NAME)
            if role:
                if role not in message.author.roles:
                    await message.author.add_roles(role)
                    await message.channel.send(f"Felicitări, {message.author.mention}, ai devenit un **{LEGIONAR_ROLE_NAME}**!")
                else:
                    await message.channel.send(f"Deja ai rolul **{LEGIONAR_ROLE_NAME}**, {message.author.mention}.")
            else:
                await message.channel.send("Rolul 'Legionar' nu a fost găsit.")
        else:
            await message.channel.send(f"Răspuns greșit, {message.author.mention}. Reîncearcă de la început.")
        lachire_verification.pop(author_id)
        await bot.process_commands(message)
        return

    # Default: Incorrect or random message
    injuratori = [
        f'Sã te futã broasca în cur pe unde bei apã {message.author.mention}.',
        f'Te bag în pizda mã-tii cu picioarele înainte ca sã-ti dau si muie dupã aia {message.author.mention}.',
        f'Zi-i lu’ mă-ta să nu-și mai schimbe rujurile că-mi face pula curcubeu {message.author.mention}.',
        f'Sã mă cac în pizda mã-tii cu bucãți de pulă {message.author.mention}.',
        f'Băgami-aș pula în mă-ta pânã îi fac pizda tunel de metrou {message.author.mention}.',
        f'Sugeți pula la negrii pânã se face albã {message.author.mention}.',
        f'Părerea mea e sã vă duceți toți în pula mea că e destulă pentru toată lumea {message.author.mention}.',
        f'Să-mi usuc chiloții pe crucea mă-tii {message.author.mention}.',
        f'Să-mi luați căcatul la polizor pânã vă sare span în ochi {message.author.mention}.',
        f'Băgami-aș pula în capul vostru de imbecili avortați {message.author.mention}.',
        f'Nu valorezi nici cât microbii de anthrax dintre celulele de spermă coclită infestată cu sifilis din pizdele curvelor de mame ce aveți {message.author.mention}.',
        f'Băgați-mi limba-n gaura curului să-mi gâdilați hemoroizii {message.author.mention}.',
        f'Spune-i mă-tii să-mi dea banii înapoi {message.author.mention}.',
        f'Ești mereu la fel de idiot sau azi este o ocazie specială, {message.author.mention}.',
        f'De ziua muncii mă-ta defilează pe autostradă {message.author.mention}.',
        f'Dacă aș avea un dinte în cur te-aș mușca de nas {message.author.mention}.',
        f'Dacă aș avea un ochi în pula m-aș uita toată ziua în gura mă-tii {message.author.mention}.'
    ]
    mesaj_de_trimis = random.choice(injuratori)
    await message.channel.send(mesaj_de_trimis, delete_after=5)

    await bot.process_commands(message)

@bot.command()
async def trezirea(ctx, member: discord.Member):
    """Cosmarul fiecarui user pe deafen (spameaza move intre doua canale continuu)"""

    if is_king(member):
        try:
            await play(ctx, MUZICA_SENTINTA)
        except Exception as e:
            await ctx.send(f"Ceva n-a mers bine cu muzica: {str(e)}")
        
        await asyncio.sleep(40)
        try:
            duration = 600
            await ctx.author.timeout(discord.utils.utcnow() + datetime.timedelta(seconds=duration), reason="Cui dai tu inchisoare rege?")
        except discord.HTTPException as e:
            await print(f"Ceva nu a mers bine: {str(e)}")

        try:
            await leave(ctx)
        except discord.HTTPException as e:
            await print(f"Ceva nu a mers bine: {str(e)}")
        return

    if not is_allowed_channel(ctx):
        await ctx.send("Ai drepturi patroane?", delete_after = 5)
        return

    if member.id in looping_users:
        await ctx.send(f"Salahorul {member.display_name} este deja la plimbare, CE PULA MEA VREI SA MAI FAC?.", delete_after = 5)
        return

    looping_users[member.id] = True
    await ctx.send(f"Salahorul {member.display_name} a fost trimis la plimbare.", delete_after = 5)
    
    # Begin the loop
    while looping_users.get(member.id):
        guild = ctx.guild
        channel_one = guild.get_channel(CHANNEL_ONE_ID)
        channel_two = guild.get_channel(CHANNEL_TWO_ID)
        
        try:
            if channel_one:
                await member.move_to(channel_one)
                await asyncio.sleep(0.2)
                
            # Move to channel two
            if channel_two:
                await member.move_to(channel_two)
                await asyncio.sleep(0.2)
        except discord.errors.HTTPException:
            looping_users.pop(member.id, None)
            await ctx.send(f"Nu am putut plimba salahorul {member.display_name} din cauza gropilor de pe autostrada, va rugam reveniti.", delete_after = 5)
            return

@bot.command()
async def somn(ctx, member: discord.Member):
    """Opreste comanda de trezire"""

    if ctx.author.id in looping_users:
        return

    if not is_allowed_channel(ctx):
        await ctx.send("Ai drepturi patroane?", delete_after = 5)
        return

    if member.id in looping_users:
        looping_users.pop(member.id, None)
        await ctx.send(f"Salahorul {member.display_name} si a cerut scuze, l-am iertat.", delete_after = 5)
    else:
        await ctx.send(f"Salahorul {member.display_name} nu este la plimbare.", delete_after = 5)

@bot.command()
async def liniste(ctx, member: discord.Member):
    """Spameaza deafen pe un user"""

    if is_king(member):
        try:
            await play(ctx, MUZICA_SENTINTA)
        except Exception as e:
            await ctx.send(f"Ceva n-a mers bine cu muzica: {str(e)}")
        
        await asyncio.sleep(40)
        try:
            duration = 600
            await ctx.author.timeout(discord.utils.utcnow() + datetime.timedelta(seconds=duration), reason="Cui dai tu inchisoare rege?")
        except discord.HTTPException as e:
            await print(f"Ceva nu a mers bine: {str(e)}")

        try:
            await leave(ctx)
        except discord.HTTPException as e:
            await print(f"Ceva nu a mers bine: {str(e)}")
        return

    if not is_allowed_channel(ctx):
        await ctx.send("Ai drepturi patroane?", delete_after = 5)
        return

    if member.id in looping_users:
        await ctx.send(f"{member.display_name} se linisteste deja.", delete_after = 5)
        return

    looping_users[member.id] = True
    await ctx.send(f"Salahorul {member.display_name} se linisteste acum.", delete_after = 5)
    while looping_users.get(member.id):
        try:
            # Deafen the user
            await member.edit(deafen=True)
            await asyncio.sleep(1)
            
            # Unmute (undeafen) the user
            await member.edit(deafen=False)
            await asyncio.sleep(0.2)
        except discord.errors.HTTPException:
            looping_users.pop(member.id, None)
            await ctx.send(f"Nu pot reduce la tacere salahorul {member.display_name} datorita sistemului democrat.", delete_after = 5)
            return

@bot.command()
async def ddox(ctx, member: discord.Member):
    """IS THIS YOU LIL NIG???"""

    if not is_allowed_channel(ctx):
        await ctx.send("Ai drepturi patroane?", delete_after = 5)
        return
        
    pfp_url = member.avatar.url  
    embed = discord.Embed(title=f"{member.name}'s Profile Picture")
    embed.set_image(url=pfp_url)
    await ctx.send("IS THIS YOU MFK? :skull: :skull: :skull:", delete_after = 30)
    await ctx.send(embed=embed, delete_after = 30)

@bot.command()
async def sterge(ctx, number_of_messages: int = 1):
    """Sterge ultimele (NUMAR) mesaje"""

    number_of_messages = number_of_messages + 1
    if number_of_messages <= 0:
        await ctx.send("Please provide a positive number of messages to delete.", delete_after = 5)
        return
    if number_of_messages > 100:
        await ctx.send("You can only delete up to 100 messages at once.", delete_after = 5)
        return
    deleted = await ctx.channel.purge(limit=number_of_messages)
    await ctx.send(f"Successfully deleted {len(deleted)} messages.", delete_after=5)

@bot.command()
async def stop_liniste(ctx, member: discord.Member):
    """Opreste comanda de liniste"""

    if ctx.author.id in looping_users:
        ctx.send("Salahorule, n ai cum tu vreodata sa mi spui sa ma opresc!")
        return

    if not is_allowed_channel(ctx):
        await ctx.send("Ai drepturi patroane?", delete_after = 5)
        return

    if member.id in looping_users:
        looping_users.pop(member.id, None)
        await ctx.send(f"Salahorul {member.display_name} poate vorbi acum.", delete_after = 5)
    else:
        await ctx.send(f"Salahorul {member.display_name} vorbeste deja", delete_after = 5)

@bot.event
async def on_command_error(ctx, error):
    """Handle command errors."""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f'{ctx.author.mention} Coaie, esti belit? Citeste manualul de instructiuni in pula mea!', delete_after = 5)

def generate_board_image(board):
    img_size = 300
    cell_size = img_size // 3
    img = Image.new("RGB", (img_size, img_size), "white")
    draw = ImageDraw.Draw(img)
    
    # Draw grid lines
    for i in range(1, 3):
        draw.line([(i * cell_size, 0), (i * cell_size, img_size)], fill="black", width=5)
        draw.line([(0, i * cell_size), (img_size, i * cell_size)], fill="black", width=5)
    
    font = ImageFont.load_default()
    
    for i in range(3):
        for j in range(3):
            if board[i][j] != " ":
                text = board[i][j]
                text_size = draw.textbbox((0, 0), text, font=font)
                text_x = j * cell_size + (cell_size - text_size[2]) // 2
                text_y = i * cell_size + (cell_size - text_size[3]) // 2
                draw.text((text_x, text_y), text, fill="black", font=font)
    
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

def check_winner(board):
    for row in board:
        if row[0] == row[1] == row[2] != " ":
            return row[0]
    
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] != " ":
            return board[0][col]
    
    if board[0][0] == board[1][1] == board[2][2] != " ":
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != " ":
        return board[0][2]
    
    return None

def is_full(board):
    return all(cell != " " for row in board for cell in row)

def minimax(board, depth, is_maximizing):
    winner = check_winner(board)
    if winner == "O":
        return 1
    if winner == "X":
        return -1
    if is_full(board):
        return 0
    
    if is_maximizing:
        best_score = -float("inf")
        for i in range(3):
            for j in range(3):
                if board[i][j] == " ":
                    board[i][j] = "O"
                    score = minimax(board, depth + 1, False)
                    board[i][j] = " "
                    best_score = max(score, best_score)
        return best_score
    else:
        best_score = float("inf")
        for i in range(3):
            for j in range(3):
                if board[i][j] == " ":
                    board[i][j] = "X"
                    score = minimax(board, depth + 1, True)
                    board[i][j] = " "
                    best_score = min(score, best_score)
        return best_score

def best_move(board):
    best_score = -float("inf")
    move = None
    for i in range(3):
        for j in range(3):
            if board[i][j] == " ":
                board[i][j] = "O"
                score = minimax(board, 0, False)
                board[i][j] = " "
                if score > best_score:
                    best_score = score
                    move = (i, j)
    return move

@bot.command()
async def tictactoe(ctx):
    board = [[" " for _ in range(3)] for _ in range(3)]
    player_turn = random.choice([True, False])
    await ctx.send("Starting a game of Tic-Tac-Toe!")
    
    while True:
        board_image = generate_board_image(board)
        await ctx.send(file=discord.File(board_image, "board.png"))
        winner = check_winner(board)
        if winner:
            await ctx.send(f"{winner} wins!")
            break
        if is_full(board):
            await ctx.send("It's a draw!")
            break
        
        if player_turn:
            await ctx.send("Enter row (0-2) and column (1-3):")
            def check(msg):
                return msg.author == ctx.author and msg.channel == ctx.channel
            
            msg = await bot.wait_for("message", check=check)
            try:
                row, col = map(int, msg.content.split())
                col -= 1  # Adjust for 0-based index
                if 0 <= row < 3 and 0 <= col < 3 and board[row][col] == " ":
                    board[row][col] = "X"
                    player_turn = False
                else:
                    await ctx.send("Invalid move, try again.")
            except:
                await ctx.send("Invalid input, please enter two numbers separated by space.")
        else:
            move = best_move(board)
            if move:
                board[move[0]][move[1]] = "O"
                player_turn = True

@bot.command()
async def help(ctx):
    """Ofera toate comenzile user ului"""
    if not is_allowed_channel(ctx):
        await ctx.send("Ai drepturi patroane?")
        return
    
    help_message = """
    **📝 Bot Commands:**
        
    **1. `!trezirea @User`**  
        Trezeste un handicapat care sta pe deafen
        *Usage*: `!trezirea @User`
        
    **2. `!somn @User`**  
        Opreste comanda de trezire
        *Usage*: `!somn @User`
        
    **3. `!liniste @User`**  
        Ofera un moment de reculegere unui handicapat
        *Usage*: `!liniste @User`
    
    **4. `!stop_liniste @User`**
        Intoarce handicapatul la episoadele de ADHD
        *Usage*: `!stop_liniste @User`

    **5. `!ddox @User`**
        IS THIS YOU LIL NIG????
        *Usage*: `!ddox @User`

    **6. `!sterge (Numar)`**
        Sterge un anumit numar de mesaje
        *Usage*: `!sterge NUMAR`

    **7. `!inchisoare @User`**
        Tine captiv un handicapat in inchisoare
        *Usage*: `!inchisoare @User`

    **8. `!eliberare @User`**
        Elibereaza salahorul din puscarie (Dani Mocanu stay strong king)
        *Usage*: `!eliberare @User`

    **8. `!play link`**
        Sa cante lautarii
        *Usage*: `!play link`

    **8. `!gay @User`**
        Calculeaza cat de gay este user-ul
        *Usage*: `!gay @User`
        
    **⚠️ Important Notes:**
    - Trebuie sa ai grade patroane, este un sistem aproape comunist
    - Daca trimiti comanda pe general, iti iei cu suspendare
        
    **🔐 Daca esti prost si nu intelegi @grimmoire00 pe discord!**
    """
    
    try:
        await ctx.author.send(help_message)
        await ctx.send("Manualul de instructiuni a fost trimis inaptului!")
    except discord.errors.Forbidden:
        await ctx.send("Ce pula mea vrei ajutor daca nu vrei sa ti scrie lumea")

TOKEN = "MTIzODUwOTc2MTE1MDg0OTA4NQ.GlfGZs.jlBrMJXhbZnBMzK-vz0cmnlWSrH1En17R9DYUY"
bot.run(TOKEN)