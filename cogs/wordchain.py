from discord.ext import commands, tasks
import discord
import random
import string

# Load dictionary of words
with open("words_alpha_3plus.txt", "r") as f:
    WORDS = set(line.strip() for line in f)
 
class WordChain(commands.Cog,name="wordchain"):
    def __init__(self, bot):
        self.bot = bot
        self.current_user = None
        self.prev_user = None
        self.used_words = set()
        self.leaderboard = {}  # example leaderboard

    def get_leaderboard_embed(self):
        leaderboard = dict(sorted(self.leaderboard.items(), key=lambda item: item[1], reverse=True))
        embed = discord.Embed(title="Leaderboard", description="XENO Word Chain Leaderboard", color=discord.Color.dark_green())
        for i, (key, value) in enumerate(leaderboard.items()):
            if i >= 5:
                break
            embed.add_field(name=key, value=value, inline=False)
        return embed

    @commands.hybrid_command(name='sh', description="shuffle for a new starting letter in wordchain(need mod access)")
    @commands.has_role("Mod Manus")  # Replace with your role name
    async def new_word(self, ctx):
        self.current_user = None
        self.prev_user = None
        self.pword = random.choice(string.ascii_lowercase)
        await ctx.send(f"New word is '{self.pword}'")
        return
    
    @commands.hybrid_command(name='add', description="adds new word to dict(need mod access)")
    @commands.has_role("Mod Manus")  # Replace with your role name
    async def add_word(self, ctx):
        content = ctx.message.content.lower()
        if content.startswith(".add"):
            addword = content[5:]
            WORDS.add(addword)
        await ctx.send(f"New word added dict size now '{len(WORDS)}'")
        return
    

    @commands.hybrid_command(name='lb', description="check word chain leaderboard")
    async def show_leaderboard(self, ctx):
        embed = self.get_leaderboard_embed()
        await ctx.send(embed=embed)

    @commands.hybrid_command(name='ms', description="check your score in word chain")
    async def my_score(self, ctx):
        score = self.leaderboard.get(ctx.author.name, 0)
        await ctx.send(f"**{ctx.author.name}** Your score is {score}")

    @tasks.loop(hours=24)
    async def write_words_txt(self):
        with open("used_words.txt", "w") as f:
            f.write("\n".join(self.used_words))

    @tasks.loop(hours=24)
    async def write_words(self):
        with open("leaderboard.txt", "w") as f:
            f.write("\n".join(self.used_words))

    @tasks.loop(hours=24)
    async def write_words_updated(self):
        with open("words_alpha_3plus_update.txt", "w") as f:
            f.write("\n".join(self.used_words))

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot :
            return

        if message.channel.id != 1078401478206705734:
            return

        content = message.content.lower()

        # Ignore invalid inputs
        if any(x in content for x in [' ', ':']):
            return

        # Check if it's the user's turn
        if self.current_user == message.author:
            await message.channel.send("It's not your turn.")
            return

        # Check if the word starts with the correct letter
        if not content.startswith(self.pword):
            await message.channel.send(f"Sorry, that word does not start with '{self.pword}'. Please try again.")
            return

        # Check if the word is valid and hasn't been used before
        if len(content) < 3:
            await message.channel.send("The word should consist of at least 3 letters.")
        elif content in self.used_words:
            await message.channel.send("Sorry, that word was already used. Please try another word.")
        elif content not in WORDS:
            await message.channel.send(f"'{content}' is present not in my dictionary")
        else:
            # Add score to the leaderboard
            score = 10 if content[0] == content[-1] else 5
            self.leaderboard[message.author.name] = self.leaderboard.get(message.author.name, 0) + score

            # Update game state
            self.used_words.add(content)
            self.prev_user = self.current_user
            self.current_user = message.author
            self.pword = content[-1]

            # Send confirmation message
            await message.add_reaction('✅')

async def setup(bot):
    await bot.add_cog(WordChain(bot))

