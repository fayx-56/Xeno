from discord.ext import commands, tasks
import discord
import random
import string
import json
import requests


# import sys
# sys.path.append('wordchain')
# from wordchain import wordchain_stats_processing
FolderName = 'word_chain_data/'

# Load dictionary of words
with open(FolderName + "words_alpha_3plus.txt", "r") as f:
    WORDS = set(line.strip() for line in f)
 
class WordChain(commands.Cog,name="wordchain"):
    def __init__(self, bot):
        self.bot = bot
        self.current_user = None
        self.prev_user = None
        self.used_words = self.load_used_words()
        self.leaderboard = self.load_leaderboard()
        self.global_leaderboard = self.load_global_leaderboard()
        self.base_score = self.calculate_base_score(self.used_words)  # type: ignore
        self.word_count = 0
        self.ycount = self.count_words_ending_with('y')

    def load_used_words(self):
        try:
            with open(FolderName + "used_words.json", "r") as file:
                return set(json.load(file))
        except FileNotFoundError:
            return set()

    def load_leaderboard(self):
        try:
            with open(FolderName + "leaderboard.json", "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}
    
    def load_global_leaderboard(self):
        try:
            with open(FolderName + "global_leaderboard.json", "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}
    
    def count_words_starting_and_ending_with(self, c):
        starting_count = 0
        ending_count = 0
        for word in self.used_words:
            if word.startswith(c):
                starting_count += 1
            if word.endswith(c):
                ending_count += 1
        return starting_count, ending_count
    
    def count_words_ending_with(self, c):
        ending_count = 0
        for word in self.used_words:
            if word.endswith(c):
                ending_count += 1
        return  ending_count
    
    def word_meaning(self, word):
        api_url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"

    # Make a GET request to the API
        response = requests.get(api_url)

    # Check if the request was successful (status code 200)
        if response.status_code == 200:
        # Parse the JSON response
            data = response.json()

        # Iterate through the meanings and get the first noun definition
            for meaning in data[0]["meanings"]:
                part_of_speech = meaning["partOfSpeech"]
                if part_of_speech == "noun":
                    definition = meaning["definitions"][0]  # Get the first definition
                    meaning_string = f"Definition of {word}: {definition['definition']}\n"
                    if 'example' in definition:
                        meaning_string += f"  Example: {definition['example']}\n"
                    return meaning_string

            return f"No noun definition found for '{word}'"
        else:
            return f"Failed to fetch definitions for the word '{word}'"

    def get_leaderboard_embed(self, leaderboard_data):
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        leaderboard = dict(sorted(leaderboard_data.items(), key=lambda item: item[1], reverse=True))
        embed = discord.Embed(title="Leaderboard", description="XENO Word Chain Leaderboard", color=discord.Color.from_rgb(r, g, b))
        for i, (key, value) in enumerate(leaderboard.items()):
            if i >= 5:
                break
            embed.add_field(name=key, value=value, inline=False)
        return embed

    
    def get_new_user_embed(self):
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        
        embed = discord.Embed(title="Welcome to Xeon Word Chain V3", description="Read pinned Rules for gaining an easy spot on the leaderboard.", color=discord.Color.from_rgb(r, g, b))
        embed.add_field(name="Scoring System", value=f"Each word earns a base point. If a word starts and ends with the same alphabet, the player earns double the base points, base point is {self.base_score} right now",inline=False)
        embed.add_field(name="y?", value='The letter "y" is no longer an issue, after 500 words with Y have been recorded', inline=False)
        embed.add_field(name="**Word Meaning**", value='now you can find the meaning of the word my adding .m at the end ex - harbinger.m', inline=False)
        embed.set_footer(text="To learn more about what I'm currently working on, feel free to check out the threads or pinned messages.")
        return embed

    # def stats_embed(self):
    #     embed = discord.Embed(title="WordChain Stats", color=discord.Color.dark_green())
    #     embed.set_image(url=wordchain_stats_processing.wordchain_stats_processing().wordchain_stats_processing(self.used_words))
    #     return embed


    @commands.hybrid_command(name='sh', description="shuffle for a new starting letter in wordchain(need mod access)")
    @commands.has_guild_permissions(administrator = True)  # Replace with your role name
    async def new_word(self, ctx):
        self.current_user = None
        self.prev_user = None
        letters = 'abcfhijmopquvwz'
        self.pword = random.choice(letters)
        await ctx.send(f"New word is '{self.pword}'")
        return
    
    
    @commands.hybrid_command(name='add', description="adds new word to dict(need mod access)")
    @commands.has_guild_permissions(administrator = True)  # Replace with your role name
    async def add_word(self, ctx):
        content = ctx.message.content.lower()
        if content.startswith(".add"):
            addword = content[5:]
            WORDS.add(addword)
        await ctx.send(f"New word added dict size now '{len(WORDS)}'")
        return
    

    @commands.hybrid_command(name='lb', description="check word chain leaderboard")
    async def show_leaderboard(self, ctx):
        embed = self.get_leaderboard_embed(self.leaderboard)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name='glb', description="check word chain global leaderboard")
    async def show_global_leaderboard(self, ctx):
        embed = self.get_leaderboard_embed(self.global_leaderboard)
        await ctx.send(embed=embed)
    
    

    @commands.hybrid_command(name='ms', description="check your score in word chain")
    async def my_score(self, ctx):
        score = self.leaderboard.get(ctx.author.name, 0)
        await ctx.send(f"**{ctx.author.name}** Your score is {score}")

    @commands.hybrid_command(name='bs', description="check base score")
    async def base_score(self, ctx):
        baseScore = self.base_score
        await ctx.send(f"base point is {baseScore} , it increases after every 1000 word")

    @commands.hybrid_command(name='slog', description="saves lb, used words logs")
    async def write_words_txt(self, ctx):
    # Save used_words to used_words.json
        with open(FolderName + "used_words.json", "w") as f:
            json_array = json.dumps(list(self.used_words))
            f.write(json_array)

    # Save leaderboard to leaderboard.json
        with open(FolderName + "leaderboard.json", "w") as f:
            json.dump(self.leaderboard, f)

    # Update global_leaderboard and save to global_leaderboard.json
        with open(FolderName + "global_leaderboard.json", "w") as f:
            json.dump(self.global_leaderboard, f)

        await ctx.send(f"Logs saved for **{ctx.author.name}**")



  

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot :
            return

        if message.channel.id != 1103242944670085211:
            return

        content = message.content.lower()

        if content.startswith('.ct'):
            starting_count, ending_count = self.count_words_starting_and_ending_with(content[4:])
            await message.channel.send(f"The count of words starting with **{content[3:]}** is **{starting_count}**")
            await message.channel.send(f"The count of words ending with **{content[3:]}** is **{ending_count}**")
            return 

        meaning_flag = False
        if content.endswith('.m'):
            meaning_flag = True
            content = content[:-2]
          

        # Ignore invalid inputs
        if any(x in content for x in [' ', ':','.']):
            return
        
        if  meaning_flag and content in self.used_words:
            await message.channel.send(self.word_meaning(content))
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
            await message.channel.send("Your word must possess a minimum of 3 letters to qualify.")
        elif content in self.used_words:
            await message.channel.send("Apologies, but that particular word has already graced our vocabulary. try again?")
        elif content not in WORDS:
            await message.channel.send(f"My dictionary's pages lack the word '{content}'")
        else:
            # Add score to the leaderboard
            score = self.base_score*2 if content[0] == content[-1] else self.base_score # type: ignore
            if message.author.name not in self.leaderboard: 
                self.leaderboard[message.author.name] = score 
                embed = self.get_new_user_embed()
                await message.channel.send(embed=embed)
            else:
                self.leaderboard[message.author.name] += score
            if message.author.name not in self.global_leaderboard:
                self.leaderboard[message.author.name] = score
            else:
                self.global_leaderboard[message.author.name] += score 
                

            # Update game state
            self.used_words.add(content)
            self.prev_user = self.current_user
            self.current_user = message.author
            self.pword = content[-1]
            self.word_count = self.word_count + 1
            if(content[-1] == 'y'):
                self.ycount=self.ycount + 1
            if(self.word_count % 1000 ==0):
                self.base_score = self.base_score + 1 # type: ignore
            # Send confirmation message
            await message.add_reaction('✅')
            if(meaning_flag):
                # meaning_result = self.word_meaning(content)
                await message.channel.send(self.word_meaning(content))
            if(content[-1] == 'y' and self.ycount>500):
                ctx = await self.bot.get_context(message)
                await ctx.invoke(self.new_word)

        print(self.ycount)
    def calculate_base_score(self, used_words):
        if not used_words:
            return 2
        else:
            return len(used_words) // 1000 + 2
                
            

async def setup(bot):
    await bot.add_cog(WordChain(bot))
