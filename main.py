import discord
from discord.ext import commands, tasks
import aiohttp
import os
import random
from dotenv import load_dotenv
import asyncio
import discord
from discord.ext import commands, tasks
from flask import Flask
from threading import Thread


load_dotenv()  # <- esta linha é obrigatória


app = Flask('')

@app.route('/')
def home():
    return "Bot rodando com sucesso!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()


# IDs dos canais
CANAL_BOAS_VINDAS = 1376938854551912514  # Substitua pelo ID do canal de boas-vindas
CANAL_PRINCIPAL = 1376938855533645988    # Substitua pelo ID do chat principal
CANAL_CURIOSIDADES = 1415681912118181921  # ID do canal de curiosidades
CANAL_VERIFICACAO = 1376938854774345834  # ID do canal #verificação
CARGO_MEMBRO = "👻 | Membro"  # nome do cargo que libera o servidor
SEU_CANAL_WALLPAPER = 1376938855533645990
BASE_URL = "https://raw.githubusercontent.com/kitsunebishi/Wallpapers/master/images/"

# Ativando intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Criando o bot
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

@tasks.loop(hours=2)
async def mandar_curiosidade():
    canal = bot.get_channel(CANAL_CURIOSIDADES)
    if not canal:
        return

    url = "https://api.jikan.moe/v4/random/anime"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()
                anime = data["data"]

                embed = discord.Embed(
                    title=f"📺 {anime['title']}",
                    description=(anime['synopsis'][:300] + "...") if anime['synopsis'] else "Sem descrição disponível.",
                    color=discord.Color.blue()
                )
                embed.set_image(url=anime["images"]["jpg"]["image_url"])
                embed.set_footer(text="Curiosidade automática sobre animes")

                await canal.send(embed=embed)

# Quando o bot ficar online
mensagens = [
    "Fala galera! 👋",
    "Já beberam água hoje? 💧",
    "Bora jogar alguma coisa?",
    "Vocês estão on ou só de enfeite?",
    "O café acabou, e agora?",
    "Quem vai puxar a call hoje?",
    "Se rir perdeu. 😂",
    "Eu ouvi barulho de loot caindo 👀",
    "Dia de sol, mendigo na cal ☀️",
    "Hora de farmar, hein?",
    "Quem aí tá de boa?",
    "Me deem atenção! 🤖",
    "Eu sou um bot, mas tenho sentimentos (acho).",
    "E se eu fosse humano?",
    "Bora zoar alguém 😈",
    "Eu não durmo, eu só espero vocês. 🌙",
    "Tá muito quieto aqui...",
    "Alguém chama o fundador pra call!",
    "Mendigo unido jamais será vencido!",
    "🔥 PDM é o melhor servidor!"
]

@tasks.loop(minutes=10)
async def mensagens_automaticas():
    canal = bot.get_channel(CANAL_PRINCIPAL)  # vai mandar no chat principal
    if canal:
        await canal.send(random.choice(mensagens))

# Evento de boas-vindas
@bot.event
async def on_member_join(member):
    channel = bot.get_channel(CANAL_VERIFICACAO)
    if channel:
        mensagem = f"""
👋 Olá {member.mention}, seja muito bem-vindo(a) ao *Papo de Mendigo (PDM)*!  

➡ Leia as regras em #registro  
➡ Escolha sua cor em #cargos 🎨  
➡ Participe das conversas no chat principal 🚀  

Estamos felizes em ter você com a gente! 😃
"""
        await channel.send(mensagem)
        await channel.send(file=discord.File("boas_vindas.png"))

@bot.command()
@commands.has_permissions(administrator=True)
async def setupverificacao(ctx):
    canal = bot.get_channel(CANAL_VERIFICACAO)
    if canal:
        mensagem = await canal.send(
            "👋 Bem-vindo ao **Papo de Mendigo (PDM)**!\n\n"
            "Para acessar o servidor, você precisa confirmar que leu as regras no canal registro.\n\n"
            "✅ Clique no emoji abaixo para liberar seu acesso!"
        )
        await mensagem.add_reaction("✅")

@bot.event
async def on_ready():
    print(f"🤖 Bot {bot.user} está online!")

    if not mandar_curiosidade.is_running():
        mandar_curiosidade.start()

    if not mandar_wallpaper_github.is_running():
        mandar_wallpaper_github.start()

    if not mensagens_automaticas.is_running():   # <-- linha 120
        mensagens_automaticas.start()            # <-- precisa estar indentado



@tasks.loop(minutes=10)
async def mandar_wallpaper_github():
    canal = bot.get_channel(1376938855533645990)  # substitua pelo ID do canal
    if not canal:
        return

    numero = random.randint(0, 388)  # total de 389 wallpapers
    nome_base = f"{numero:05}"       # exemplo: "00023"

    async with aiohttp.ClientSession() as session:
        for ext in ["jpg", "png"]:  # tenta primeiro jpg, depois png
            url = f"{BASE_URL}{nome_base}.{ext}"
            async with session.get(url) as resp:
                if resp.status == 200:
                    embed = discord.Embed(
                        title="🖼️ Seu wallpaper novo chegou!",
                        color=discord.Color.dark_gold()
                    )
                    embed.set_image(url=url)
                    embed.set_footer(text="Wallpapers automáticos - Pack Kitsunebishi")
                    await canal.send(embed=embed)
                    return  # sai assim que achar a imagem válida        

# Interação no chat principal
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return  # evita loop

    if message.channel.id == CANAL_PRINCIPAL:  
        if "oi" in message.content.lower():  
            await message.channel.send(f"Oi {message.author.mention}! Seja bem-vindo 😃")  
        elif "como vai" in message.content.lower():  
            await message.channel.send("Estou ótimo! E você? 🤖")  
        elif "pdm" in message.content.lower():  
            await message.channel.send("🔥 PDM é o melhor servidor do Discord!")  

    await bot.process_commands(message)

# Comando de ping
@bot.command()
async def ping(ctx):
    await ctx.send("Pong! 🏓")

# Comando para mutar alguém
@bot.command()
@commands.has_permissions(manage_roles=True)
async def mutar(ctx, member: discord.Member, tempo: int = 0):
    mutado = discord.utils.get(ctx.guild.roles, name="Mutado")
    if not mutado:
        mutado = await ctx.guild.create_role(name="Mutado")
        for canal in ctx.guild.channels:
            await canal.set_permissions(mutado, send_messages=False, speak=False)
    
    await member.add_roles(mutado)
    await ctx.send(f"{member.mention} foi mutado! 🔇")

    if tempo > 0:
        await discord.utils.sleep_until(tempo)
        await member.remove_roles(mutado)
        await ctx.send(f"{member.mention} foi desmutado! 🔊")

# Comando para adicionar cargo
@bot.command()
@commands.has_permissions(manage_roles=True)
async def addcargo(ctx, member: discord.Member, *, cargo_nome):
    cargo = discord.utils.get(ctx.guild.roles, name=cargo_nome)
    if not cargo:
        cargo = await ctx.guild.create_role(name=cargo_nome)
    await member.add_roles(cargo)
    await ctx.send(f"{member.mention} recebeu o cargo *{cargo_nome}* ✅")

# Comando de help personalizado
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="📜 Lista de Comandos - Papo de Mendigo (PDM)",
        color=discord.Color.orange()
    )
    embed.add_field(name="!ping", value="Teste de resposta do bot.", inline=False)
    embed.add_field(name="!mutar @usuario [tempo]", value="Muta o usuário mencionado. Requer permissão de Gerenciar Cargos.", inline=False)
    embed.add_field(name="!addcargo @usuario NomeDoCargo", value="Adiciona um cargo ao usuário. Requer permissão de Gerenciar Cargos.", inline=False)
    embed.add_field(name="Interações no chat principal", value="O bot responde automaticamente a: 'oi', 'como vai', 'pdm'.", inline=False)
    await ctx.send(embed=embed)

# Evento que dá o cargo quando o usuário reage no canal de verificação
@bot.event
async def on_raw_reaction_add(payload):
    if payload.channel_id == CANAL_VERIFICACAO and str(payload.emoji) == "✅":
        guild = bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        if member and not member.bot:
            cargo = discord.utils.get(guild.roles, name=CARGO_MEMBRO)
            if cargo:
                await member.add_roles(cargo)
                print(f"{member} recebeu o cargo {CARGO_MEMBRO}!")

@bot.event
async def on_ready():
    print(f"🤖 Bot {bot.user} está online!")

    if not mandar_curiosidade.is_running():
        mandar_curiosidade.start()

    if not mandar_wallpaper_github.is_running():
        mandar_wallpaper_github.start()

# Evento unificado de updates de membro
@bot.event
async def on_member_update(before, after):
    cargo_membro = discord.utils.get(after.guild.roles, name=CARGO_MEMBRO)

    # 1️⃣ Detecta se o usuário acabou de receber o cargo de membro
    if cargo_membro not in before.roles and cargo_membro in after.roles:
        canal = bot.get_channel(CANAL_VERIFICACAO)
        if canal:
            await canal.send(
                f"🎉 {after.mention} acabou de ser verificado e agora faz parte da comunidade **Papo de Mendigo (PDM)**!",
                file=discord.File("cargo.png")
            )

    # 2️⃣ Detecta se o usuário entrou online
    if before.status == discord.Status.offline and after.status == discord.Status.online:
        canal = bot.get_channel(1376938854774345831)
        if canal:
            await canal.send(
                f"👋 {after.mention}, obrigado por entrar novamente na nossa comunidade **Papo de Mendigo (PDM)**! 🎉",
                file=discord.File("obrigado.png")
            )



@bot.event
async def on_voice_state_update(member, before, after):
    # checa se foi o FUNDADOR que entrou numa call
    if member.id == 1376901792696111246:
        # entrou em call
        if before.channel is None and after.channel is not None:
            canal_texto = bot.get_channel(1376938854774345831)
            if canal_texto:
                await canal_texto.send(f"🎤 O fundador **{member.display_name}** entrou na call **{after.channel.name}**!")
        # saiu da call
        elif before.channel is not None and after.channel is None:
            canal_texto = bot.get_channel(1376938854774345831)
            if canal_texto:
                await canal_texto.send(f"👋 O fundador **{member.display_name}** saiu da call **{before.channel.name}**.")


# Rodar o bot
keep_alive()
bot.run(os.getenv("DISCORD_TOKEN"))


