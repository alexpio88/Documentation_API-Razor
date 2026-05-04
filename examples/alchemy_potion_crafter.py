"""
Razor Enhanced - Alchemy potion crafter

How to use:
1. Put a mortar and pestle, empty bottles, and reagents in your backpack.
2. Set POTION_TO_CRAFT and AMOUNT_TO_CRAFT below.
3. Open the Alchemy crafting gump once and craft the potion manually, or fill
   the category/item button ids in POTIONS to let the script select the recipe.
4. Run this script from Razor Enhanced.

The default mode uses the crafting gump "Make Last" button. This is usually the
most stable option because crafting gump button ids can differ between shards.
If MAKE_LAST_BUTTON is wrong for your shard, use Razor Enhanced's Inspect Gumps
or Record tool to capture the correct button id and update the value below.
"""

# ----------------------------- User settings ------------------------------

POTION_TO_CRAFT = 'greater heal'
AMOUNT_TO_CRAFT = 25

MORTAR_AND_PESTLE_ID = 0x0E9B
EMPTY_BOTTLE_ID = 0x0F0E

# 0 means "wait for any gump". Set a fixed gump id if your shard needs it.
CRAFT_GUMP_ID = 0

# Common RunUO/ServUO crafting gumps use 21 for "Make Last"; verify on yours.
MAKE_LAST_BUTTON = 21

# If True and button ids are configured for the selected potion, the script
# selects the recipe once, then uses Make Last for the remaining crafts.
SELECT_RECIPE_FIRST = False

GUMP_TIMEOUT_MS = 5000
CRAFT_RESULT_TIMEOUT_MS = 9000
ACTION_PAUSE_MS = 700
OPEN_GUMP_PAUSE_MS = 400

# Stop before becoming overloaded.
MAX_WEIGHT_BUFFER = 10

# Set to True to print checks without pressing craft buttons.
DRY_RUN = False

# ------------------------------ Item tables --------------------------------

REAGENTS = {
    'black pearl': 0x0F7A,
    'blood moss': 0x0F7B,
    'garlic': 0x0F84,
    'ginseng': 0x0F85,
    'mandrake root': 0x0F86,
    'nightshade': 0x0F88,
    'spider silk': 0x0F8D,
    'sulfurous ash': 0x0F8C,
}

POTIONS = {
    'refresh': {
        'reagents': {'black pearl': 1},
        'category_button': 0,
        'item_button': 0,
    },
    'total refresh': {
        'reagents': {'black pearl': 1},
        'category_button': 0,
        'item_button': 0,
    },
    'agility': {
        'reagents': {'blood moss': 1},
        'category_button': 0,
        'item_button': 0,
    },
    'greater agility': {
        'reagents': {'blood moss': 1},
        'category_button': 0,
        'item_button': 0,
    },
    'cure': {
        'reagents': {'garlic': 1},
        'category_button': 0,
        'item_button': 0,
    },
    'greater cure': {
        'reagents': {'garlic': 1},
        'category_button': 0,
        'item_button': 0,
    },
    'heal': {
        'reagents': {'ginseng': 1},
        'category_button': 0,
        'item_button': 0,
    },
    'greater heal': {
        'reagents': {'ginseng': 1},
        'category_button': 0,
        'item_button': 0,
    },
    'strength': {
        'reagents': {'mandrake root': 1},
        'category_button': 0,
        'item_button': 0,
    },
    'greater strength': {
        'reagents': {'mandrake root': 1},
        'category_button': 0,
        'item_button': 0,
    },
    'poison': {
        'reagents': {'nightshade': 1},
        'category_button': 0,
        'item_button': 0,
    },
    'greater poison': {
        'reagents': {'nightshade': 1},
        'category_button': 0,
        'item_button': 0,
    },
    'deadly poison': {
        'reagents': {'nightshade': 1},
        'category_button': 0,
        'item_button': 0,
    },
    'night sight': {
        'reagents': {'spider silk': 1},
        'category_button': 0,
        'item_button': 0,
    },
    'explosion': {
        'reagents': {'sulfurous ash': 1},
        'category_button': 0,
        'item_button': 0,
    },
    'greater explosion': {
        'reagents': {'sulfurous ash': 1},
        'category_button': 0,
        'item_button': 0,
    },
}

SUCCESS_MESSAGES = [
    'You pour the potion',
    'You create',
    'You put the',
    'successfully',
]

STOP_MESSAGES = [
    'You do not have sufficient',
    'You lack the',
    'You have worn out your tool',
    'You must have',
    'You cannot make',
    'You are too far away',
    'You are already doing',
]


def say(message, hue=68):
    Misc.SendMessage('[Alchemy] ' + message, hue, False)


def normalize(name):
    return name.strip().lower()


def backpack_count(item_id):
    return Items.BackpackCount(item_id, -1)


def backpack_serial():
    return Player.Backpack.Serial


def find_tool():
    return Items.FindByID(MORTAR_AND_PESTLE_ID, -1, backpack_serial(), True, False)


def has_weight_room():
    if MAX_WEIGHT_BUFFER <= 0:
        return True
    return Player.Weight < (Player.MaxWeight - MAX_WEIGHT_BUFFER)


def missing_resources(recipe):
    missing = []

    bottles = backpack_count(EMPTY_BOTTLE_ID)
    if bottles < 1:
        missing.append('empty bottles')

    for reagent_name in recipe['reagents']:
        item_id = REAGENTS[reagent_name]
        needed = recipe['reagents'][reagent_name]
        if backpack_count(item_id) < needed:
            missing.append(reagent_name)

    return missing


def possible_crafts(recipe):
    possible = backpack_count(EMPTY_BOTTLE_ID)

    for reagent_name in recipe['reagents']:
        item_id = REAGENTS[reagent_name]
        needed = recipe['reagents'][reagent_name]
        amount = backpack_count(item_id) / needed
        if amount < possible:
            possible = amount

    return int(possible)


def wait_for_craft_gump():
    Gumps.WaitForGump(CRAFT_GUMP_ID, GUMP_TIMEOUT_MS)
    if not Gumps.HasGump():
        return 0
    return Gumps.CurrentGump()


def open_craft_gump():
    tool = find_tool()
    if tool is None:
        say('Mortar and pestle non trovato nello zaino.', 33)
        return 0

    Gumps.ResetGump()
    Items.UseItem(tool, None, False)
    Misc.Pause(OPEN_GUMP_PAUSE_MS)
    return wait_for_craft_gump()


def send_gump_button(gump_id, button_id):
    if DRY_RUN:
        say('DRY RUN: premerei il bottone gump {0}.'.format(button_id), 88)
        return True

    Journal.Clear()
    Gumps.SendAction(gump_id, button_id)
    Misc.Pause(ACTION_PAUSE_MS)
    return True


def select_recipe(recipe):
    category_button = recipe['category_button']
    item_button = recipe['item_button']

    if category_button <= 0 or item_button <= 0:
        say('Button id ricetta non configurati: uso Make Last.', 53)
        return 'skip'

    gump_id = open_craft_gump()
    if gump_id == 0:
        say('Crafting gump non aperto.', 33)
        return 'stop'

    say('Seleziono categoria e ricetta dal gump.')
    send_gump_button(gump_id, category_button)
    gump_id = wait_for_craft_gump()
    if gump_id == 0:
        say('Gump chiuso dopo la categoria.', 33)
        return 'stop'

    send_gump_button(gump_id, item_button)
    result = Journal.WaitJournal(SUCCESS_MESSAGES + STOP_MESSAGES, CRAFT_RESULT_TIMEOUT_MS)
    if result:
        result_lower = result.lower()
        for stop_message in STOP_MESSAGES:
            if stop_message.lower() in result_lower:
                say('Stop dal journal: {0}'.format(result), 33)
                return 'stop'
        return 'success'

    return 'unknown'


def craft_once():
    gump_id = open_craft_gump()
    if gump_id == 0:
        say('Crafting gump non trovato.', 33)
        return 'stop'

    send_gump_button(gump_id, MAKE_LAST_BUTTON)

    result = Journal.WaitJournal(SUCCESS_MESSAGES + STOP_MESSAGES, CRAFT_RESULT_TIMEOUT_MS)
    if result:
        result_lower = result.lower()
        for stop_message in STOP_MESSAGES:
            if stop_message.lower() in result_lower:
                say('Stop dal journal: {0}'.format(result), 33)
                return 'stop'

        return 'success'

    # Some shards do not emit a journal line for successful crafting.
    return 'unknown'


def main():
    potion_name = normalize(POTION_TO_CRAFT)
    if potion_name not in POTIONS:
        say('Pozione non configurata: {0}'.format(POTION_TO_CRAFT), 33)
        say('Disponibili: {0}'.format(', '.join(sorted(POTIONS.keys()))), 33)
        return

    if MAKE_LAST_BUTTON <= 0:
        say('MAKE_LAST_BUTTON deve essere configurato.', 33)
        return

    recipe = POTIONS[potion_name]
    missing = missing_resources(recipe)
    if missing:
        say('Risorse mancanti: {0}.'.format(', '.join(missing)), 33)
        return

    tool = find_tool()
    if tool is None:
        say('Mortar and pestle non trovato nello zaino.', 33)
        return

    max_by_resources = possible_crafts(recipe)
    target_amount = AMOUNT_TO_CRAFT
    if target_amount <= 0 or target_amount > max_by_resources:
        target_amount = max_by_resources

    if target_amount <= 0:
        say('Nessun craft possibile con le risorse attuali.', 33)
        return

    say('Avvio craft: {0} x {1}.'.format(target_amount, potion_name))

    crafted = 0
    attempts = 0
    max_attempts = target_amount + 10

    if SELECT_RECIPE_FIRST:
        first_outcome = select_recipe(recipe)
        if first_outcome == 'stop':
            return
        if first_outcome != 'skip':
            crafted += 1
            say('Craft {0}/{1} ({2}).'.format(crafted, target_amount, first_outcome), 68)

    while crafted < target_amount and attempts < max_attempts:
        attempts += 1

        if not has_weight_room():
            say('Peso quasi al massimo: {0}/{1}.'.format(Player.Weight, Player.MaxWeight), 33)
            break

        missing = missing_resources(recipe)
        if missing:
            say('Risorse finite: {0}.'.format(', '.join(missing)), 33)
            break

        outcome = craft_once()
        if outcome == 'stop':
            break

        crafted += 1
        say('Craft {0}/{1} ({2}).'.format(crafted, target_amount, outcome), 68)
        Misc.Pause(ACTION_PAUSE_MS)

    say('Finito. Tentativi: {0}, craft conteggiati: {1}.'.format(attempts, crafted), 68)


main()
