from customer_information import check
import asyncio
import random
import json
import discord

with open('license_elements.json') as te_file:
    te = json.load(te_file)
with open('config.json') as config_file:
    config = json.load(config_file)
with open('licenses.json') as license_file:
    license_list = json.load(license_file)
with open('customers.json') as customer_file:
    custo = json.load(customer_file)

customers = custo["customers"]
license_elements = te["license_elements"]
license_length = config["license_length"]
discord_token = config["discord_token"]
gen_limit = config["generate_limit"]
licenses = license_list["licenses"]
prefix = config["prefix"]

def license_generator(time, count):
    li_list = []
    while len(li_list) < int(count):
        random_letters = []
        for i in range(license_length):
            list_choice = random.randint(0, 3)
            if list_choice == 0 or list_choice == 1:
                random_letter = random.randint(0, 25)
            if list_choice == 2:
                random_letter = random.randint(0, 9)
            if list_choice == 3:
                random_letter = random.randint(0, 2)
            random_letters.append(license_elements[list_choice][random_letter])
        license_result = "".join(map(str, random_letters))
        if license_result not in licenses[0] or licenses[1] or licenses[2]:
            li_list.append(license_result)
            possibilities = ["Day","Week","Month"]
            for u in range(3):
                if time == possibilities[u]:
                    licenses[u].append(license_result)
            overwrite = {
                "licenses": licenses
            }
            with open("licenses.json", "w") as outfile:
                json.dump(overwrite, outfile)
    return li_list

def customer_info():
    with open('customers.json') as customer_file:
        customer = json.load(customer_file)
    customers = customer["customers"]
    return customers

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Bot(intents=intents, help_command=None)

@bot.event
async def on_ready():
    line = "-" * 40
    space = " " * 11
    print(f"\n\n{line}\n{space}Activ on {len(bot.guilds)} servers\n   Logged in as {bot.user}\n{line}\n")
    task = asyncio.create_task(license_checker())

async def license_checker():
    while True:
        customers = customer_info()
        from datetime import datetime
        time = datetime.now()
        count = 0
        for i in range(len(customers[1])):
            if datetime.strptime(customers[1][count], "%Y:%m:%d %H:%M:%S") < time:
                print(f"{customers[0][count]} (removed)")
                customers[0].pop(count)
                customers[1].pop(count)
                overwrite = {"customers": customers}
                with open("customers.json", "w") as outfile:
                    json.dump(overwrite, outfile)
        await asyncio.sleep(30)

@bot.command(description="Help-Command")
async def help(ctx):
    embed = discord.Embed(title="**License-System**", description="This is the help page for the token system.",
                          color=0x001a9e)
    embed.add_field(name="Generate license",
                    value=f"`{prefix}generate " + "{number}" + "` generates the desired number of licenses (only with permissions).\n",
                    inline=False)
    embed.add_field(name="Redeem license", value=f"`{prefix}redeem `let you redeem your license.\n",
                    inline=False)
    embed.set_footer(text="Developed by Dadelx#7053")
    await ctx.respond(embed=embed)


@bot.slash_command(name="generate")
async def generate(ctx: discord.ApplicationContext, count, time: discord.Option(str, choices=['Day', 'Week', 'Month'])):
    with open('config.json') as admin_file:
        admin = json.load(admin_file)
    admin_id = admin["admin_id"]

    if ctx.user.id in admin_id:
        if int(count) <= gen_limit:
            license_result = license_generator(time, count)
            display_licenses = "```" + "``````".join(map(str, license_result)) + "```"
            embed = discord.Embed(title="**License-System**",
                                  description=f"**{count}** licenses were successfully created by **{ctx.author}**",
                                  color=0x00ff11)
            embed.add_field(name="Time:", value=time, inline=False)
            embed.add_field(name="Licenses:", value=f"{display_licenses}", inline=False)
            embed.set_footer(text="Developed by Dadelx#7053")
            await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(title="**License-System**",
                                  description=f"The limit of the licenses that can be created once has been set to **{gen_limit}**.",
                                  color=0xff0000)
            embed.set_footer(text="Developed by Dadelx#7053")
            await ctx.respond(embed=embed)
    else:
        embed = discord.Embed(title="**License-System**", description=f"Missing Permissions",
                              color=0xff0000)
        embed.set_footer(text="Developed by Dadelx#7053")
        await ctx.respond(embeds=[embed])


class license_ui(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add_item(discord.ui.InputText(label="License"))

    async def callback(self, interaction: discord.Interaction):
        author_id = interaction.user.id
        l_input = self.children[0].value

        if str(l_input) in licenses[0] or licenses[1] or licenses[2]:
            customers = customer_info()
            if author_id not in customers[0]:
                from datetime import datetime, timedelta
                for i in range(3):
                    dates = [1,7,30]
                    try:
                        future = (datetime.now() + timedelta(days=dates[i])).strftime("%Y:%m:%d %H:%M:%S")
                        licenses[i].remove(l_input)
                    except:
                        pass
                customers[1].append(future)
                overwrite = {"licenses": licenses}
                with open("licenses.json", "w") as outfile:
                    json.dump(overwrite, outfile)
                customers[0].append(author_id)
                overwrite = {"customers": customers}
                with open("customers.json", "w") as outfile:
                    json.dump(overwrite, outfile)

                embed = discord.Embed(title="**License-System**",
                                      description="The license has been redeemed successfully.",
                                      color=0x00ff11)
                embed.set_footer(text="Developed by Dadelx#7053")
                await interaction.response.send_message(embeds=[embed])
                print(f"{author_id} (added)")
            else:
                embed = discord.Embed(title="**License-System**", description=f"You are already a customer with us.",
                                      color=0x00ff11)
                embed.set_footer(text="Developed by Dadelx#7053")
                await interaction.response.send_message(embeds=[embed])
        else:
            embed = discord.Embed(title="**License-System**", description=f"Please use an existing licenses",
                                  color=0xff0000)
            embed.set_footer(text="Developed by Dadelx#7053")
            await interaction.response.send_message(embeds=[embed])

@bot.slash_command()
async def redeem(ctx: discord.ApplicationContext):
    """Licese input"""
    modal = license_ui(title="License-System")
    await ctx.send_modal(modal)

@bot.command(description="customer_command")
async def lizenz_command(ctx):
    if check(0).id(ctx.user.id):
        await ctx.respond("Msg for Customers")
    else:
        await ctx.respond("You are not in the Customer list")

bot.run(discord_token)
