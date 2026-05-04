"""
Razor Enhanced - Alchemy potion crafter

How to use:
1. Put a mortar and pestle, empty bottles, and reagents in your backpack or in
   the resource chest selected when the script starts.
   If you want the script to craft the mortar and pestle when missing, also put
   tinker tools and ingots in your backpack or resource chest.
2. Use the startup window to select potions/apples and quantities. If the
   window is disabled or unavailable, POTION_TO_CRAFT and AMOUNT_TO_CRAFT are
   used as fallback.
3. Open the Alchemy crafting gump once and craft the potion manually, or fill
   the category/item button ids in POTIONS to let the script select the recipe.
4. Run this script from Razor Enhanced.

The default mode uses the crafting gump "Make Last" button. This is usually the
most stable option because crafting gump button ids can differ between shards.
If MAKE_LAST_BUTTON is wrong for your shard, use Razor Enhanced's Inspect Gumps
or Record tool to capture the correct button id and update the value below.
"""

import re

# ----------------------------- User settings ------------------------------

USE_SELECTION_WINDOW = True
POTION_TO_CRAFT = 'greater heal'
AMOUNT_TO_CRAFT = 25

MORTAR_AND_PESTLE_ID = 0x0E9B
EMPTY_BOTTLE_ID = 0x0F0E
TINKER_TOOLS_ID = 0x1EB8
INGOT_ID = 0x1BF2
APPLE_ID = 0x09D0

# Ask for the resource chest at script start. The script restocks reagents,
# bottles, ingots, and tinker tools from this chest when needed.
PROMPT_RESOURCE_CHEST = True
RESOURCE_CHEST_SERIAL = 0
RESTOCK_FROM_RESOURCE_CHEST = True

# 0 means "wait for any gump". Set a fixed gump id if your shard needs it.
CRAFT_GUMP_ID = 0

# Common RunUO/ServUO crafting gumps use 21 for "Make Last"; verify on yours.
MAKE_LAST_BUTTON = 21

# If True and button ids are configured for the selected potion, the script
# selects the recipe once, then uses Make Last for the remaining crafts.
SELECT_RECIPE_FIRST = False

# If no mortar and pestle is found, try to craft one with Tinkering.
AUTO_CRAFT_MORTAR_AND_PESTLE = True

# Keep a spare tinker tool ready before the current one gets too low.
TINKER_TOOLS_MIN_USES = 20
TINKER_TOOLS_REQUIRED_INGOTS = 2

# 0 means "wait for any gump". Set a fixed Tinkering gump id if needed.
MORTAR_CRAFT_GUMP_ID = 0

# Common RunUO/ServUO crafting gumps use 21 for "Make Last"; verify on yours.
MORTAR_MAKE_LAST_BUTTON = 21

# Optional Tinkering button ids for the mortar and pestle recipe. If left as 0,
# the script uses MORTAR_MAKE_LAST_BUTTON, so your last Tinkering recipe must be
# mortar and pestle.
MORTAR_CATEGORY_BUTTON = 0
MORTAR_ITEM_BUTTON = 0
MORTAR_REQUIRED_INGOTS = 3

# Optional Tinkering button ids for the tinker tools recipe. If left as 0, the
# script uses MORTAR_MAKE_LAST_BUTTON, so your last Tinkering recipe must be
# tinker tools when this reserve craft is needed.
TINKER_TOOLS_CATEGORY_BUTTON = 0
TINKER_TOOLS_ITEM_BUTTON = 0

GUMP_TIMEOUT_MS = 5000
CRAFT_RESULT_TIMEOUT_MS = 9000
ACTION_PAUSE_MS = 700
OPEN_GUMP_PAUSE_MS = 400
MOVE_PAUSE_MS = 650

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

MATERIALS = dict(REAGENTS)
MATERIALS['apple'] = APPLE_ID

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

APPLE_CRAFTS = {
    'enchanted apple': {
        'display': 'mele incantate',
        'materials': {'apple': 1},
        'uses_bottle': False,
        'category_button': 0,
        'item_button': 0,
        'make_last_button': MAKE_LAST_BUTTON,
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


def resource_chest():
    if RESOURCE_CHEST_SERIAL <= 0:
        return None
    return Items.FindBySerial(RESOURCE_CHEST_SERIAL)


def select_resource_chest():
    global RESOURCE_CHEST_SERIAL

    if not PROMPT_RESOURCE_CHEST and RESOURCE_CHEST_SERIAL > 0:
        return open_resource_chest()

    if not PROMPT_RESOURCE_CHEST:
        return True

    serial = Target.PromptTarget('Seleziona la cassa risorse per alchemy.', 68)
    if serial <= 0:
        say('Nessuna cassa risorse selezionata.', 33)
        return False

    RESOURCE_CHEST_SERIAL = serial
    return open_resource_chest()


def open_resource_chest():
    chest = resource_chest()
    if chest is None:
        say('Cassa risorse non trovata.', 33)
        return False

    Items.UseItem(chest, None, False)
    Items.WaitForContents(chest, GUMP_TIMEOUT_MS)
    Misc.Pause(OPEN_GUMP_PAUSE_MS)
    return True


def find_tool():
    return Items.FindByID(MORTAR_AND_PESTLE_ID, -1, backpack_serial(), True, False)


def find_tinker_tools():
    return Items.FindByID(TINKER_TOOLS_ID, -1, backpack_serial(), True, False)


def extract_first_number(text):
    match = re.search(r'\d+', text)
    if match:
        return int(match.group(0))
    return None


def tinker_tool_uses_remaining(tool):
    props = Items.GetPropStringList(tool)
    for prop in props:
        prop_lower = prop.lower()
        if 'uses remaining' in prop_lower or 'usi rimasti' in prop_lower:
            return extract_first_number(prop)
    return None


def chest_count(item_id):
    if RESOURCE_CHEST_SERIAL <= 0:
        return 0
    return Items.ContainerCount(RESOURCE_CHEST_SERIAL, item_id, -1, True)


def available_count(item_id, include_chest):
    total = backpack_count(item_id)
    if include_chest and RESTOCK_FROM_RESOURCE_CHEST:
        total += chest_count(item_id)
    return total


def restock_item(item_id, amount, label):
    if amount <= 0:
        return True

    if not RESTOCK_FROM_RESOURCE_CHEST or RESOURCE_CHEST_SERIAL <= 0:
        return False

    if not open_resource_chest():
        return False

    available = chest_count(item_id)
    if available < amount:
        say('Cassa risorse: mancano {0} x {1}.'.format(amount - available, label), 33)
        return False

    item = Items.FindByID(item_id, -1, RESOURCE_CHEST_SERIAL, True, False)
    if item is None:
        say('Cassa risorse: {0} non trovato.'.format(label), 33)
        return False

    if DRY_RUN:
        say('DRY RUN: prenderei {0} x {1} dalla cassa.'.format(amount, label), 88)
        return True

    remaining = amount
    while remaining > 0:
        item = Items.FindByID(item_id, -1, RESOURCE_CHEST_SERIAL, True, False)
        if item is None:
            break

        stack_amount = item.Amount
        if stack_amount <= 0:
            stack_amount = 1

        move_amount = remaining
        if stack_amount < move_amount:
            move_amount = stack_amount

        Items.Move(item, Player.Backpack, move_amount)
        Misc.Pause(MOVE_PAUSE_MS)
        remaining -= move_amount

    if remaining > 0:
        say('Non sono riuscito a prendere tutti: {0} x {1} mancanti.'.format(remaining, label), 33)
        return False

    return True


def restock_stack_to_backpack(item_id, desired_amount, label):
    current = backpack_count(item_id)
    if current >= desired_amount:
        return True
    return restock_item(item_id, desired_amount - current, label)


def ensure_item_in_backpack(item_id, label):
    if Items.FindByID(item_id, -1, backpack_serial(), True, False) is not None:
        return True
    return restock_item(item_id, 1, label)


def recipe_materials(recipe):
    if 'materials' in recipe:
        return recipe['materials']
    return recipe['reagents']


def recipe_uses_bottle(recipe):
    if 'uses_bottle' in recipe:
        return recipe['uses_bottle']
    return True


def restock_recipe_resources(recipe, target_amount):
    if recipe_uses_bottle(recipe):
        if not restock_stack_to_backpack(EMPTY_BOTTLE_ID, target_amount, 'empty bottles'):
            return False

    for material_name in recipe_materials(recipe):
        item_id = MATERIALS[material_name]
        needed = recipe_materials(recipe)[material_name] * target_amount
        if not restock_stack_to_backpack(item_id, needed, material_name):
            return False

    return True


def has_weight_room():
    if MAX_WEIGHT_BUFFER <= 0:
        return True
    return Player.Weight < (Player.MaxWeight - MAX_WEIGHT_BUFFER)


def missing_recipe_resources(recipe):
    missing = []

    if recipe_uses_bottle(recipe) and backpack_count(EMPTY_BOTTLE_ID) < 1:
        missing.append('empty bottles')

    for material_name in recipe_materials(recipe):
        item_id = MATERIALS[material_name]
        needed = recipe_materials(recipe)[material_name]
        if backpack_count(item_id) < needed:
            missing.append(material_name)

    return missing


def possible_recipe_crafts(recipe, include_chest=False):
    possible = 999999

    if recipe_uses_bottle(recipe):
        possible = available_count(EMPTY_BOTTLE_ID, include_chest)

    for material_name in recipe_materials(recipe):
        item_id = MATERIALS[material_name]
        needed = recipe_materials(recipe)[material_name]
        amount = available_count(item_id, include_chest) / needed
        if amount < possible:
            possible = amount

    if possible == 999999:
        return 0

    return int(possible)


def wait_for_gump(gump_id):
    Gumps.WaitForGump(gump_id, GUMP_TIMEOUT_MS)
    if not Gumps.HasGump():
        return 0
    return Gumps.CurrentGump()


def wait_for_craft_gump():
    return wait_for_gump(CRAFT_GUMP_ID)


def wait_for_result():
    result = Journal.WaitJournal(SUCCESS_MESSAGES + STOP_MESSAGES, CRAFT_RESULT_TIMEOUT_MS)
    if not result:
        return 'unknown'

    result_text = str(result)
    result_lower = result_text.lower()
    for stop_message in STOP_MESSAGES:
        if stop_message.lower() in result_lower:
            say('Stop dal journal: {0}'.format(result_text), 33)
            return 'stop'

    return 'success'


def open_tinkering_gump(tinker_tools):
    Gumps.ResetGump()
    Journal.Clear()
    Items.UseItem(tinker_tools, None, False)
    Misc.Pause(OPEN_GUMP_PAUSE_MS)

    gump_id = wait_for_gump(MORTAR_CRAFT_GUMP_ID)
    if gump_id == 0:
        say('Gump Tinkering non trovato.', 33)
    return gump_id


def send_tinkering_recipe(category_button, item_button, make_last_button, make_last_label):
    tinker_tools = find_tinker_tools()
    if tinker_tools is None:
        say('Tinker tools non trovati nello zaino.', 33)
        return False

    if DRY_RUN:
        say('DRY RUN: aprirei il gump Tinkering.', 88)
        return True

    gump_id = open_tinkering_gump(tinker_tools)
    if gump_id == 0:
        return False

    if category_button > 0 and item_button > 0:
        send_gump_button(gump_id, category_button)
        gump_id = wait_for_gump(MORTAR_CRAFT_GUMP_ID)
        if gump_id == 0:
            say('Gump Tinkering chiuso dopo la categoria.', 33)
            return False
        send_gump_button(gump_id, item_button)
    else:
        say('Uso Make Last di Tinkering: deve essere impostato su {0}.'.format(make_last_label), 53)
        send_gump_button(gump_id, make_last_button)

    return wait_for_result() != 'stop'


def craft_tinker_tools():
    ensure_item_in_backpack(TINKER_TOOLS_ID, 'tinker tools')
    restock_stack_to_backpack(INGOT_ID, TINKER_TOOLS_REQUIRED_INGOTS, 'ingots')

    if backpack_count(INGOT_ID) < TINKER_TOOLS_REQUIRED_INGOTS:
        say('Lingotti insufficienti per craftare tinker tools di riserva.', 33)
        return False

    if find_tinker_tools() is None:
        say('Tinker tools non trovati per craftarne uno nuovo.', 33)
        return False

    if DRY_RUN:
        say('DRY RUN: crafterei tinker tools di riserva.', 88)
        return True

    before_count = backpack_count(TINKER_TOOLS_ID)
    say('Tinker tools sotto soglia: provo a craftarne uno di riserva.', 53)
    if not send_tinkering_recipe(
        TINKER_TOOLS_CATEGORY_BUTTON,
        TINKER_TOOLS_ITEM_BUTTON,
        MORTAR_MAKE_LAST_BUTTON,
        'tinker tools',
    ):
        return False

    Misc.Pause(ACTION_PAUSE_MS)
    if backpack_count(TINKER_TOOLS_ID) <= before_count:
        say('Craft tinker tools non verificato: controlla button id o Make Last Tinkering.', 33)
        return False

    say('Tinker tools di riserva craftati.', 68)
    return True


def ensure_tinker_tools_reserve(required):
    if not ensure_item_in_backpack(TINKER_TOOLS_ID, 'tinker tools'):
        if required:
            say('Tinker tools non trovati nello zaino o nella cassa.', 33)
            return False
        return True

    tinker_tools = find_tinker_tools()
    uses = tinker_tool_uses_remaining(tinker_tools)
    if uses is None:
        say('Usi rimasti dei tinker tools non leggibili: continuo.', 53)
        return True

    if uses >= TINKER_TOOLS_MIN_USES:
        return True

    say('Tinker tools a {0} usi: soglia {1}.'.format(uses, TINKER_TOOLS_MIN_USES), 53)
    return craft_tinker_tools()


def craft_mortar_and_pestle():
    if not AUTO_CRAFT_MORTAR_AND_PESTLE:
        say('Mortar and pestle non trovato nello zaino.', 33)
        return False

    if not ensure_tinker_tools_reserve(True):
        return False

    restock_stack_to_backpack(INGOT_ID, MORTAR_REQUIRED_INGOTS, 'ingots')

    if backpack_count(INGOT_ID) < MORTAR_REQUIRED_INGOTS:
        say('Mortaio mancante e lingotti insufficienti per craftarlo.', 33)
        return False

    if DRY_RUN:
        say('DRY RUN: crafterei un mortar and pestle con Tinkering.', 88)
        return True

    say('Mortar and pestle mancante: provo a craftarlo con Tinkering.', 53)
    if not send_tinkering_recipe(
        MORTAR_CATEGORY_BUTTON,
        MORTAR_ITEM_BUTTON,
        MORTAR_MAKE_LAST_BUTTON,
        'mortar and pestle',
    ):
        return False

    Misc.Pause(ACTION_PAUSE_MS)
    if find_tool() is None:
        say('Craft mortaio non verificato: controlla button id o Make Last Tinkering.', 33)
        return False

    say('Mortar and pestle craftato.', 68)
    return True


def ensure_mortar_and_pestle():
    if find_tool() is not None:
        return True
    if ensure_item_in_backpack(MORTAR_AND_PESTLE_ID, 'mortar and pestle'):
        return True
    return craft_mortar_and_pestle()


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


def select_recipe_for_job(recipe):
    category_button = recipe['category_button']
    item_button = recipe['item_button']

    if category_button <= 0 or item_button <= 0:
        say('Button id ricetta non configurati: uso Make Last.', 53)
        return 'skip'

    gump_id = open_craft_gump()
    if gump_id == 0:
        say('Crafting gump non aperto.', 33)
        return 'stop'

    say('Seleziono ricetta dal gump.')
    send_gump_button(gump_id, category_button)
    gump_id = wait_for_craft_gump()
    if gump_id == 0:
        say('Gump chiuso dopo la categoria.', 33)
        return 'stop'

    send_gump_button(gump_id, item_button)
    return wait_for_result()


def craft_once(make_last_button):
    gump_id = open_craft_gump()
    if gump_id == 0:
        say('Crafting gump non trovato.', 33)
        return 'stop'

    send_gump_button(gump_id, make_last_button)

    # Some shards do not emit a journal line for successful crafting.
    return wait_for_result()


def get_recipe(recipe_type, recipe_name):
    if recipe_type == 'potion':
        return POTIONS[recipe_name]
    return APPLE_CRAFTS[recipe_name]


def get_recipe_display(recipe_type, recipe_name):
    recipe = get_recipe(recipe_type, recipe_name)
    if 'display' in recipe:
        return recipe['display']
    return recipe_name


def craft_job(recipe_type, recipe_name, target_amount):
    if not ensure_mortar_and_pestle():
        return False

    recipe = get_recipe(recipe_type, recipe_name)
    display = get_recipe_display(recipe_type, recipe_name)

    if target_amount <= 0:
        target_amount = possible_recipe_crafts(recipe, True)

    if target_amount > 0 and not restock_recipe_resources(recipe, target_amount):
        return False

    missing = missing_recipe_resources(recipe)
    if missing:
        say('Risorse mancanti per {0}: {1}.'.format(display, ', '.join(missing)), 33)
        return False

    max_by_resources = possible_recipe_crafts(recipe)
    if target_amount <= 0 or target_amount > max_by_resources:
        target_amount = max_by_resources

    if target_amount <= 0:
        say('Nessun craft possibile per {0}.'.format(display), 33)
        return False

    say('Avvio craft: {0} x {1}.'.format(target_amount, display))

    crafted = 0
    attempts = 0
    max_attempts = target_amount + 10

    first_outcome = select_recipe_for_job(recipe)
    if first_outcome == 'stop':
        return False
    if first_outcome != 'skip':
        crafted += 1
        say('Craft {0}/{1} ({2}).'.format(crafted, target_amount, first_outcome), 68)

    make_last_button = recipe.get('make_last_button', MAKE_LAST_BUTTON)
    while crafted < target_amount and attempts < max_attempts:
        attempts += 1

        if not has_weight_room():
            say('Peso quasi al massimo: {0}/{1}.'.format(Player.Weight, Player.MaxWeight), 33)
            return False

        missing = missing_recipe_resources(recipe)
        if missing:
            say('Risorse finite per {0}: {1}.'.format(display, ', '.join(missing)), 33)
            return False

        outcome = craft_once(make_last_button)
        if outcome == 'stop':
            return False

        crafted += 1
        say('Craft {0}/{1} ({2}).'.format(crafted, target_amount, outcome), 68)
        Misc.Pause(ACTION_PAUSE_MS)

    say('Finito {0}. Tentativi: {1}, craft conteggiati: {2}.'.format(display, attempts, crafted), 68)
    return True


def fallback_jobs():
    potion_name = normalize(POTION_TO_CRAFT)
    if potion_name not in POTIONS:
        say('Pozione non configurata: {0}'.format(POTION_TO_CRAFT), 33)
        say('Disponibili: {0}'.format(', '.join(sorted(POTIONS.keys()))), 33)
        return []
    return [('potion', potion_name, AMOUNT_TO_CRAFT)]


def prompt_craft_jobs():
    if not USE_SELECTION_WINDOW:
        return fallback_jobs()

    try:
        import clr
        clr.AddReference('System.Windows.Forms')
        clr.AddReference('System.Drawing')
        from System.Drawing import Point, Size
        from System.Windows.Forms import Button, CheckBox, DialogResult, Form, FormBorderStyle, Label, NumericUpDown
    except Exception as error:
        say('Finestra selezione non disponibile: uso fallback. {0}'.format(error), 53)
        return fallback_jobs()

    form = Form()
    form.Text = 'Alchemy craft'
    form.Size = Size(430, 620)
    form.FormBorderStyle = FormBorderStyle.FixedDialog
    form.MaximizeBox = False
    form.MinimizeBox = False
    form.AutoScroll = True
    form.AutoScrollMinSize = Size(400, 520)

    title = Label()
    title.Text = 'Seleziona cosa craftare e la quantita:'
    title.Location = Point(12, 12)
    title.Size = Size(360, 22)
    form.Controls.Add(title)

    controls = []
    y_pos = [42]

    def add_recipe_row(recipe_type, recipe_name):
        checkbox = CheckBox()
        checkbox.Text = get_recipe_display(recipe_type, recipe_name)
        checkbox.Location = Point(18, y_pos[0])
        checkbox.Size = Size(250, 24)
        form.Controls.Add(checkbox)

        amount = NumericUpDown()
        amount.Location = Point(285, y_pos[0])
        amount.Size = Size(80, 24)
        amount.Minimum = 0
        amount.Maximum = 999
        amount.Value = 0
        form.Controls.Add(amount)

        controls.append((recipe_type, recipe_name, checkbox, amount))
        y_pos[0] += 30

    section = Label()
    section.Text = 'Pozioni'
    section.Location = Point(12, y_pos[0])
    section.Size = Size(360, 22)
    form.Controls.Add(section)
    y_pos[0] += 24

    for potion_name in sorted(POTIONS.keys()):
        add_recipe_row('potion', potion_name)

    y_pos[0] += 8
    section = Label()
    section.Text = 'Mele'
    section.Location = Point(12, y_pos[0])
    section.Size = Size(360, 22)
    form.Controls.Add(section)
    y_pos[0] += 24

    for apple_name in sorted(APPLE_CRAFTS.keys()):
        add_recipe_row('apple', apple_name)

    ok_button = Button()
    ok_button.Text = 'Avvia'
    ok_button.Location = Point(210, y_pos[0] + 14)
    ok_button.DialogResult = DialogResult.OK
    form.Controls.Add(ok_button)

    cancel_button = Button()
    cancel_button.Text = 'Annulla'
    cancel_button.Location = Point(300, y_pos[0] + 14)
    cancel_button.DialogResult = DialogResult.Cancel
    form.Controls.Add(cancel_button)

    form.AcceptButton = ok_button
    form.CancelButton = cancel_button

    result = form.ShowDialog()
    if result != DialogResult.OK:
        say('Craft annullato dalla finestra.', 33)
        return []

    jobs = []
    for recipe_type, recipe_name, checkbox, amount in controls:
        quantity = int(amount.Value)
        if checkbox.Checked and quantity > 0:
            jobs.append((recipe_type, recipe_name, quantity))

    if not jobs:
        say('Nessun craft selezionato.', 33)

    return jobs


def main():
    if not select_resource_chest():
        return

    if not ensure_tinker_tools_reserve(False):
        return

    if MAKE_LAST_BUTTON <= 0:
        say('MAKE_LAST_BUTTON deve essere configurato.', 33)
        return

    jobs = prompt_craft_jobs()
    if not jobs:
        return

    for recipe_type, recipe_name, amount in jobs:
        if not craft_job(recipe_type, recipe_name, amount):
            break

    say('Coda craft terminata.', 68)


main()
