import discord
import json
import os
import datetime
from bot.Pokemon import pokemon_names, alolan_names, alolan_shortforms, castform_names, castform_shortforms
from config import Config

extreme_data_path = Config.EXTREME_PATH
stats_data_path = Config.STATS_PATH
plots_data_path = Config.PLOTS_PATH
watchlists_data_path = Config.WATCHLISTS_PATH
search_evos = True

# msg = 'Hello {0.author.mention}'.format(message)

client = discord.Client()

def get_client():
    return client


@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    message.content = message.content.lower()


    if message.channel.name == "size":
        params = message.content.split()
        msg = "{0.author.mention},\n".format(message)
        extra = False
        for i in range(0, len(params)):
            print(i)
            if extra:
                continue
            print(i)
            names, extra = pokemon_search(params, i)
            if extra:
                i = i + 1
            if len(names) == 0:
                msg += "I don't recognize {0} as a Pokemon name.\n".format(params[i])
            else:
                for name in names:
                    msg += get_formatted_data(name)
    elif message.content.startswith('!s') or message.content.startswith('s '):
        params = message.content.split()[1:]
        if len(params) < 1:
            msg = "{0.author.mention}, please include a Pokemon name in your query.".format(message)
        else:
            msg = "{0.author.mention},\n".format(message)
            for i in range(0, len(params)):
                names, extra = pokemon_search(params, i)
                if len(names) == 0:
                    msg += "I don't recognize {0} as a Pokemon name.\n".format(params[i])
                else:
                    for name in names:
                        msg += get_formatted_data(name)
    elif message.content.startswith('!u') or message.content.startswith('u '):
        msg = process_upgrade(message)




    elif message.content.startswith('!d') or message.content.startswith('d '):
        msg = process_delete_upgrade(message)


    elif message.content.startswith('!p') or message.content.startswith('p '):
        params = message.content.split()[1:]
        if len(params) < 1:
            msg = "{0.author.mention}, please type a Pokemon name for this command.".format(message)
        else:
            names, extra = pokemon_search(params, 0)
            name = ""
            if len(names) > 0:
                name = names[0]
            else:
                msg = "{0.author.mention}, please check your Pokemon name.".format(message)

            if name != "":
                plot = create_plot(name)
                await client.send_file(message.channel, plot)
    elif message.content.startswith('!w') or message.content.startswith('w'):
        msg = process_watchlist(message)

    print(msg)

    message_max_length = 1800
    while(len(msg) > message_max_length):
        last_break = msg[:message_max_length].rfind('\n\n')
        cur_message = msg[:last_break]
        await client.send_message(message.channel, "\n\n" + cur_message )
        msg = msg[last_break:]

    await client.send_message(message.channel, "\n\n" + msg )


def pokemon_search(params, index):
    search = params[index].capitalize()
    ret = []
    extra = False
    if search in pokemon_names:
        if search == "Castform":
            ret.append("Castform Normal")
            ret.append("Castform Fire")
            ret.append("Castform Ice")
            ret.append("Castform Water")
        else:
            ret.append(search)
        return ret, extra
    elif search in ["Alola","Alolan"]:
        try:
            search_two = params[index+1].capitalize()
            extra = True
            for name in alolan_names:
                if search_two in name:
                    ret.append("Alolan " + name)
        except:
            extra = False
            return ret, extra

    for name in pokemon_names:
        if search in name:
            if name == "Castform":
                ret.append("Castform Normal")
                ret.append("Castform Fire")
                ret.append("Castform Ice")
                ret.append("Castform Water")
            else:
                ret.append(name)
    for i in range(0, len(alolan_shortforms)):
        if search in alolan_shortforms[i] or search in alolan_names[i]:
            ret.append("Alolan " + alolan_names[i])
    for i in range(0, len(castform_shortforms)):
        if search == castform_shortforms[i]:
            ret.append(castform_names[i])

    return ret, extra


def process_delete_upgrade(message):
    params = message.content.split()[1:]
    if len(params) < 1:
        msg = "{0.author.mention}, please type a Pokemon name for this command.".format(message)
    else:
        names = pokemon_search(params[0])
        name = ""
        if len(names) == 1:
            name = names[0]
        else:
            msg = "{0.author.mention}, please be more specific in your Pokemon name".format(message)

        if name != "":
            delete_upgrades(name, message.author.id)
            msg = "{0.author.mention}, I've deleted your upgrade data for {1}".format(message, name.capitalize())

    return msg


def process_upgrade(message):
    params = message.content.split()[1:]
    if len(params) < 2:
        if len(params) > 0:
            names = pokemon_search(params[0])
            msg = "{0.author.mention}: \n".format(message)
            for name in names:
                msg += "{0}:\n".format(name) + get_formatted_upgrades(name)
        else:
            msg = "{0.author.mention}, you're missing some parameters\.  The command is \'!u pokemon_name size\', with kg or m after the size.".format(
                message)
            return msg
    else:
        names = pokemon_search(params[0])
        name = ""
        if len(names) == 1:
            name = names[0]
        else:
            msg = "{0.author.mention}, please be more specific in your Pokemon name.".format(message)
            return msg

        suffix = ""
        if params[1].lower().endswith('kg') or params[1].lower().endswith('k'):
            params[1] = params[1][:-2]
            suffix = 'kg'
        elif params[1].lower().endswith('m'):
            params[1] = params[1][:-1]
            suffix = 'm'

        if name != "":
            size = ""
            if suffix == "":
                if len(params) > 2:
                    suffix = params[2]
            if suffix != "kg" and suffix != "m":
                msg = "{0.author.mention}, please let me know if your size is in kg or m".format(message)
            else:
                try:
                    size = float(params[1])
                except ValueError:
                    msg = "{0.author.mention}, {1} is not a valid number.  Please try again.".format(message, params[1])
                    return msg

                author = message.author.name
                author_id = message.author.id
                write_upgrade(name, size, suffix, author, author_id)
                msg = "{0.author.mention}, upgrades for this Pokemon are: \n".format(message)
                msg = msg + get_formatted_upgrades(name)

        return msg


def create_plot(name):
    import matplotlib.pyplot
    plt = matplotlib.pyplot
    fig = plt.figure()
    fig.suptitle(name.lower(),fontsize=14,fontweight='bold')

    ax=fig.add_subplot(111)
    fig.subplots_adjust(top=0.85)

    filename = stats_data_path + os.sep + name.lower() + ".json"
    if os.path.exists(filename):
        with open(filename) as json_file:
            data = json.load(json_file)
        points = data['data']
        count = data['count']
        x = []
        y = []
        ax.set_title('count: ' + str(count))
        ax.set_xlabel('weight (kg)')
        ax.set_ylabel('height (m)')
        for point in points:
            x.append(point[0])
            y.append(point[1])
        ax.plot(x, y, '.')
        extreme_file = extreme_data_path + os.sep + name.lower() + "_extremes.json"
        if os.path.exists(extreme_file):
            with open(extreme_file) as x_file:
                xtreme_json = json.load(x_file)
            light = xtreme_json['min_weight']
            heavy = xtreme_json['max_weight']
            small = xtreme_json['min_height']
            tall = xtreme_json['max_height']
            ax.axvline(x=light, color='r')
            ax.axvline(x=heavy, color='r')
            ax.axhline(y=small, color='r')
            ax.axhline(y=tall, color='r')

        outfile = plots_data_path + os.sep + name.lower() + ".png"
        if os.path.exists(outfile):
            os.remove(outfile)
        fig.savefig(outfile)
        plt.clf()
        plt.cla()
        plt.close()
        return outfile


def get_formatted_data(name):
    filename = extreme_data_path + os.sep + name.lower() + "_extremes.json"
    print(name)
    if os.path.exists(filename):
        with open(filename) as json_file:
            data = json.load(json_file)
        small = data["min_height"]
        light = data["min_weight"]
        heavy = data["max_weight"]
        tall = data["max_height"]
        try:
            timestamp = data["last_updated_ts"]
        except KeyError:
            timestamp = ""
        if not timestamp == "":
            formatted_timestamp = datetime.datetime.strftime(datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S'),
                                                             '%m-%d-%Y')
            print(formatted_timestamp)
        else:
            formatted_timestamp = ""
        msg = "{0: <16} - Light: **{1: >7}** kg    Small: **{2: >5}** m    Heavy: **{3: >7}** kg    Tall: **{4: >5}** m".format(name,
                                                                                                                light,
                                                                                                                small,
                                                                                                                heavy,
                                                                                                                tall)
        if not formatted_timestamp == "":
            msg = msg + "  :::  {0: <11}".format(formatted_timestamp)
        if search_evos == True:
            msg = msg + "\n" + get_formatted_evos(name)
        msg = msg + "\n\n"
        return msg
    else:
        return "{0} - Cannot find data.\n\n".format(name)


def get_formatted_evos(name):
    print(name)
    filename = stats_data_path + os.sep + name.lower() + ".json"
    if os.path.exists(filename):
        with open(filename) as jsonfile:
            data = json.load(jsonfile)
    else:
        return ""

    try:
        evos = data['evolves_into']
    except KeyError:
        return ""

    weight_mean = data['gm_weight_mean']
    height_mean = data['gm_height_mean']
    weight_stdev = data['gm_weight_stdev']
    height_stdev = data['gm_height_stdev']

    light_stdev = 1000
    small_stdev = 1000
    heavy_stdev = 1000
    tall_stdev = 1000

    for evo in evos:
        cur_light, cur_small, cur_heavy, cur_tall, cur_evos = get_extremes_as_stdevs(evo)
        evos.extend(cur_evos)
        if cur_light < light_stdev:
            light_stdev = cur_light
        if cur_small < small_stdev:
            small_stdev = cur_small
        if cur_heavy < heavy_stdev:
            heavy_stdev = cur_heavy
        if cur_tall < tall_stdev:
            tall_stdev = cur_tall

    light = weight_mean - (weight_stdev * light_stdev) + .01
    small = height_mean - (height_stdev * small_stdev) + .01
    heavy = weight_mean + (weight_stdev * heavy_stdev) - .01
    tall = height_mean + (height_stdev * tall_stdev) - .01

    return "{0: <16} - Light: **{1: >7}** kg    Small: **{2: >5}** m    Heavy: **{3: >7}** kg    Tall: **{4: >5}** m".format(
        "     Evos", format(light, '.2f'), format(small,'.2f'), format(heavy,'.2f'), format(tall,'.2f'))


def get_extremes_as_stdevs(name):
    extreme_file = extreme_data_path + os.sep + name.lower() + "_extremes.json"
    if not os.path.exists(extreme_file):
        return 110, 110, 110, 110, []

    stats_file = stats_data_path + os.sep + name.lower() + ".json"

    if not os.path.exists(stats_file):
        return 220, 220, 220, 220, []

    with open(extreme_file) as jsonfile:
        extreme_data = json.load(jsonfile)

    with open(stats_file) as jsonfile:
        stats_data = json.load(jsonfile)

    try:
        weight_stdev = stats_data['gm_weight_stdev']
        weight_mean = stats_data['gm_weight_mean']
        height_stdev = stats_data['gm_height_stdev']
        height_mean = stats_data['gm_height_mean']

        light = extreme_data['min_weight']
        small = extreme_data['min_height']
        heavy = extreme_data['max_weight']
        tall = extreme_data['max_height']

        light_stdev = (weight_mean - light) / weight_stdev
        small_stdev = (height_mean - small) / height_stdev
        heavy_stdev = (heavy - weight_mean) / weight_stdev
        tall_stdev = (tall - height_mean) / height_stdev

    except KeyError as e:
        print(e)
        return 440, 440, 440, 440, []

    try:
        evos = stats_data['evolves_into']
    except KeyError:
        evos = []

    return light_stdev, small_stdev, heavy_stdev, tall_stdev, evos


def get_formatted_upgrades(name):
    filename = extreme_data_path + os.sep + name.lower() + "_extremes.json"
    ret = ""
    if os.path.exists(filename):
        with open(filename) as json_file:
            data = json.load(json_file)
        if 'upgrades' in data:
            upgrades = data['upgrades']
            for upgrade in upgrades:
                ret += "{0: >8} {1: >2}  from {2: <20} \n\n".format(str(upgrade[1]), upgrade[2], upgrade[3])

    return ret


def write_upgrade(name: str, number: str, suffix: str, author: str, author_id: str):
    filename = extreme_data_path + os.sep + name.lower() + "_extremes.json"
    data = {}
    if os.path.exists(filename):
        with open(filename) as json_file:
            data = json.load(json_file)

    if not 'upgrades' in data:
        data['upgrades'] = []

    data['upgrades'].append([name, number, suffix, author, author_id])

    with open(filename, "w") as json_file:
        json.dump(data, json_file)


def delete_upgrades(name: str, author_id: str):
    filename = extreme_data_path + os.sep + name.lower() + "_extremes.json"
    if not os.path.exists(filename):
        return

    with open(filename) as json_file:
        data = json.load(json_file)

    if not 'upgrades' in data:
        return

    new_upgrades = []
    for upgrade_set in data['upgrades']:
        if upgrade_set[4] != author_id:
            new_upgrades.append(upgrade_set)

    data['upgrades'] = new_upgrades

    with open(filename, "w") as json_file:
        json.dump(data, json_file)


def process_watchlist(message):
    params = []
    if message.content.startswith('!'):
        message.content = message.content[1:]
    if message.content.startswith('wa'):
        params.append('a')
        params.append(message.content.split()[1:])
    elif message.content.startswith('wd'):
        params.append('d')
        params.append(message.content.split()[1:])
    elif message.content.startswith('ws'):
        params.append('s')
        params.append(message.content.split()[1:])
    elif message.content.startswith('we'):
        params.append('e')
        params.append(message.content.split()[1:])
    else:
        pre_params = message.content.split()[1:]
        if len(pre_params) == 0:
            params.append('s')
        elif pre_params[0] not in ['a', 's', 'd', 'e']:
            params.append('s')
        params.append(pre_params)

    if params[0] == 'a':
        return add_to_watchlist(message, params[1])
    elif params[0] == 'd':
        return delete_from_watchlist(message, params[1])
    elif params[0] == 's':
        return search_watchlist(message)
    elif params[0] == 'e':
        return search_eventlist(message)


def add_to_watchlist(message, params):
    author_id = message.author.id
    filename = watchlists_data_path + os.sep + author_id + ".json"
    if not os.path.exists(filename):
        data = {}
        data['watchlist'] = []
        with open(filename, 'w') as outfile:
            json.dump(data, outfile)
    with open(filename, 'r') as infile:
        data = json.load(infile)
    success = []
    for search_term in params:
        for name in pokemon_search(search_term):
            if not name in data['watchlist']:
                data['watchlist'].append(name)
                success.append(name)

    with open(filename, 'w') as outfile:
        json.dump(data, outfile)

    return "{0.author.mention}, the following pokemon were added to your watchlist: {1}.".format(message,
                                                                                                 ", ".join(success))


def delete_from_watchlist(message, params):
    author_id = message.author.id
    filename = watchlists_data_path + os.sep + author_id + ".json"
    if not os.path.exists(filename):
        return "{0.author.mention}, you don't seem to have a watchlist.".format(message)
    with open(filename, 'r') as infile:
        data = json.load(infile)
    try:
        data['watchlist']
    except KeyError:
        return "{0.author.mention}, you don't seem to have a watchlist.".format(message)
    if not data['watchlist']:
        return "{0.author.mention}, you don't seem to have a watchlist.".format(message)
    success = []
    for search_term in params:
        for name in pokemon_search(search_term):
            try:
                data['watchlist'].remove(name)
                success.append(name)
            except:
                print(name)

    with open(filename, 'w') as outfile:
        json.dump(data, outfile)

    return "{0.author.mention}, successfully removed the following pokemon from your watchlist: {1}".format(message,
                                                                                                            ", ".join(
                                                                                                                success))


def search_watchlist(message):
    author_id = message.author.id
    filename = watchlists_data_path + os.sep + author_id + ".json"
    if not os.path.exists(filename):
        return "{0.author.mention}, you don't seem to have a watchlist.".format(message)
    with open(filename, 'r') as infile:
        data = json.load(infile)
    try:
        data['watchlist']
    except KeyError:
        return "{0.author.mention}, you don't seem to have a watchlist.".format(message)

    if not data['watchlist']:
        return "{0.author.mention}, you don't seem to have a watchlist.".format(message)

    msg = "{0.author.mention},\n".format(message)
    for search_term in data['watchlist']:
        try:
            msg += get_formatted_data(search_term)
        except:
            pass

    return msg


def search_eventlist(message):
    filename = watchlists_data_path + os.sep + "event.json"
    with open(filename, 'r') as infile:
        data = json.load(infile)
    try:
        data['watchlist']
    except KeyError:
        return "{0.author.mention}, there isn't an event watchlist set right now.".format(message)

    if not data['watchlist']:
        return "{0.author.mention}, there isn't an event watchlist set right now.".format(message)

    msg = "\n"
    for search_term in data['watchlist']:
        try:
            msg += get_formatted_data(search_term)
        except:
            pass

    return msg


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
