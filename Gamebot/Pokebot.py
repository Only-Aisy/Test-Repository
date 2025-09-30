# pokemon_full.py
import streamlit as st
import random
import copy

st.set_page_config(page_title="Mini Pokémon - Expanded", layout="wide")

# -----------------------
# GAME CONFIG
# -----------------------
MAP_ROWS = 6
MAP_COLS = 6

# Tiles (row, col)
GRASS_TILES = {(1,1), (1,2), (1,3), (2,1), (3,2), (4,3)}
POKEMON_CENTER = (0, 5)
TRAINER_TILES = {(4,0), (2,5)}  # stepping on triggers trainer battle

# Wild Pokémon pool (simple)
WILD_POOL = [
    {"name": "Pidgey", "hp": 30, "max_hp":30, "moves":[("Tackle", 4,8), ("Gust", 3,7)]},
    {"name": "Rattata", "hp": 28, "max_hp":28, "moves":[("Tackle", 4,8), ("Bite", 5,9)]},
    {"name": "Weedle", "hp": 22, "max_hp":22, "moves":[("Tackle", 2,6)]},
    {"name": "Pikachu", "hp": 32, "max_hp":32, "moves":[("Tackle", 3,6), ("Thunder Shock", 6,10)]},
]

# Trainer definitions (each trainer is a list of pokemon dicts)
TRAINERS = {
    "Youngster Joe": [
        {"name":"Rattata","hp":28,"max_hp":28,"moves":[("Tackle",4,8)]},
        {"name":"Pidgey","hp":30,"max_hp":30,"moves":[("Tackle",4,8)]},
    ],
    "Ace Trainer Mia": [
        {"name":"Pikachu","hp":32,"max_hp":32,"moves":[("Quick Attack",3,6),("Thunder Shock",6,10)]},
        {"name":"Rattata","hp":28,"max_hp":28,"moves":[("Bite",5,9)]},
    ]
}

# Starter options
STARTERS = {
    "Charmander": {"name":"Charmander","hp":39,"max_hp":39,"moves":[("Scratch",5,9),("Ember",6,10)]},
    "Squirtle": {"name":"Squirtle","hp":44,"max_hp":44,"moves":[("Tackle",5,9),("Water Gun",6,10)]},
    "Bulbasaur": {"name":"Bulbasaur","hp":45,"max_hp":45,"moves":[("Tackle",5,9),("Vine Whip",6,10)]},
}

# -----------------------
# SESSION STATE INIT
# -----------------------
if "screen" not in st.session_state:
    st.session_state.screen = "start"  # start, map, battle
if "player_pos" not in st.session_state:
    st.session_state.player_pos = [3, 3]  # row, col
if "party" not in st.session_state:
    st.session_state.party = []  # list of pokemon dicts
if "battle_type" not in st.session_state:
    st.session_state.battle_type = None  # 'wild' or 'trainer'
if "enemy_party" not in st.session_state:
    st.session_state.enemy_party = []  # list of pokemon dicts (trainer) or single wild in list
if "active_enemy_idx" not in st.session_state:
    st.session_state.active_enemy_idx = 0
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pokeballs" not in st.session_state:
    st.session_state.pokeballs = 6
if "caught_names" not in st.session_state:
    st.session_state.caught_names = set()
if "defeated_trainers" not in st.session_state:
    st.session_state.defeated_trainers = set()

# -----------------------
# HELPERS
# -----------------------
def reset_to_map():
    st.session_state.screen = "map"
    st.session_state.battle_type = None
    st.session_state.enemy_party = []
    st.session_state.active_enemy_idx = 0
    st.session_state.messages = []

def heal_party():
    for p in st.session_state.party:
        p["hp"] = p["max_hp"]

def spawn_wild():
    # return a deep copy of a random wild
    w = copy.deepcopy(random.choice(WILD_POOL))
    return w

def pick_trainer_for_tile(tile):
    # deterministically pick a trainer for a trainer tile
    # For simplicity map tile -> trainer by order
    tile_list = list(TRAINER_TILES)
    if tile in TRAINER_TILES:
        name = list(TRAINERS.keys())[list(TRAINER_TILES).index(tile) % len(TRAINERS)]
        # if trainer already defeated choose next
        # but for simplicity just pick the first trainer not defeated
        for tname, party in TRAINERS.items():
            if tname not in st.session_state.defeated_trainers:
                return tname, copy.deepcopy(party)
        # if all defeated, return last trainer
        tname = list(TRAINERS.keys())[0]
        return tname, copy.deepcopy(TRAINERS[tname])
    return None, []

def start_trainer_battle(tile):
    tname, party = pick_trainer_for_tile(tile)
    if tname is None:
        return
    st.session_state.battle_type = "trainer"
    st.session_state.enemy_party = party
    st.session_state.active_enemy_idx = 0
    st.session_state.screen = "battle"
    st.session_state.messages = [f"Trainer {tname} challenges you!"]
    st.session_state.current_trainer_name = tname

def try_start_wild_battle():
    wild = spawn_wild()
    st.session_state.battle_type = "wild"
    st.session_state.enemy_party = [wild]
    st.session_state.active_enemy_idx = 0
    st.session_state.screen = "battle"
    st.session_state.messages = [f"A wild {wild['name']} appeared!"]

def perform_attack(attacker, defender, move):
    # move is (name, min_dmg, max_dmg)
    name, lo, hi = move
    dmg = random.randint(lo, hi)
    defender['hp'] = max(0, defender['hp'] - dmg)
    return f"{attacker['name']} used {name}! It dealt {dmg} damage."

def enemy_turn_if_alive():
    enemy = st.session_state.enemy_party[st.session_state.active_enemy_idx]
    if enemy["hp"] <= 0:
        return
    # choose a move
    mv = random.choice(enemy["moves"])
    # choose current active player pokemon (first alive)
    player = None
    for p in st.session_state.party:
        if p["hp"] > 0:
            player = p
            break
    if player is None:
        return
    msg = perform_attack(enemy, player, mv)
    st.session_state.messages.append(msg)
    if player['hp'] <= 0:
        st.session_state.messages.append(f"Your {player['name']} fainted!")

def check_battle_end():
    # check if all player's pokemon fainted
    any_alive = any(p['hp'] > 0 for p in st.session_state.party)
    if not any_alive:
        st.session_state.messages.append("All your Pokémon fainted! You retreat to the Pokémon Center (if you have one).")
        # send player to map and to center if exists, heal them
        st.session_state.player_pos = [POKEMON_CENTER[0], POKEMON_CENTER[1]]
        heal_party()
        reset_to_map()
        return True

    # check enemy party exhausted
    all_enemies_down = all(e['hp'] <= 0 for e in st.session_state.enemy_party)
    if all_enemies_down:
        if st.session_state.battle_type == "wild":
            wild = st.session_state.enemy_party[st.session_state.active_enemy_idx]
            st.session_state.messages.append(f"You defeated the wild {wild['name']}!")
            reset_to_map()
            return True
        elif st.session_state.battle_type == "trainer":
            # mark trainer defeated
            tname = st.session_state.current_trainer_name
            st.session_state.defeated_trainers.add(tname)
            st.session_state.messages.append(f"You defeated Trainer {tname}!")
            reset_to_map()
            return True
    return False

def try_catch_wild():
    if st.session_state.pokeballs <= 0:
        st.session_state.messages.append("No Pokéballs left!")
        return
    st.session_state.pokeballs -= 1
    # simple catch chance: base 45% reduced by current HP% of wild
    wild = st.session_state.enemy_party[st.session_state.active_enemy_idx]
    hp_frac = wild['hp'] / wild['max_hp'] if wild['max_hp']>0 else 0
    base = 0.45
    catch_chance = base * (1.0 - hp_frac) + 0.1  # ensure some chance
    roll = random.random()
    if roll < catch_chance:
        st.session_state.messages.append(f"🎉 You caught {wild['name']}!")
        # add to party (if not already have)
        new_poke = copy.deepcopy(wild)
        new_poke['hp'] = new_poke['max_hp']  # when captured, fully healthy in party
        st.session_state.party.append(new_poke)
        st.session_state.caught_names.add(new_poke['name'])
        reset_to_map()
    else:
        st.session_state.messages.append(f"{wild['name']} broke free!")
        # enemy gets a free hit
        enemy_turn_if_alive()
        check_battle_end()

def try_run_away():
    # available only for wild, attempt run with 70% success
    if st.session_state.battle_type != "wild":
        st.session_state.messages.append("You can't run from a trainer battle!")
        return
    if random.random() < 0.7:
        st.session_state.messages.append("You successfully ran away!")
        reset_to_map()
    else:
        st.session_state.messages.append("Couldn't escape!")
        enemy_turn_if_alive()
        check_battle_end()

def switch_active_pokemon(index):
    # bring selected pokemon to front of party list (active slot)
    if index < 0 or index >= len(st.session_state.party):
        return
    selected = st.session_state.party.pop(index)
    st.session_state.party.insert(0, selected)
    st.session_state.messages.append(f"You switched to {selected['name']}.")

# -----------------------
# MAP & MOVEMENT
# -----------------------
def draw_map():
    s = ""
    for r in range(MAP_ROWS):
        row = ""
        for c in range(MAP_COLS):
            pos = (r,c)
            if [r,c] == st.session_state.player_pos:
                row += "🧍 "
            elif pos == POKEMON_CENTER:
                row += "🏥 "
            elif pos in TRAINER_TILES and list(TRAINER_TILES).index(pos) in range(len(TRAINERS)):
                # If trainer defeated, show faded icon
                trainer_name = list(TRAINERS.keys())[list(TRAINER_TILES).index(pos) % len(TRAINERS)]
                if trainer_name in st.session_state.defeated_trainers:
                    row += "✅ "  # defeated
                else:
                    row += "👤 "
            elif pos in GRASS_TILES:
                row += "🌿 "
            else:
                row += "⬜ "
        s += row + "\n"
    return s

def move_player(dr, dc):
    new_r = st.session_state.player_pos[0] + dr
    new_c = st.session_state.player_pos[1] + dc
    if 0 <= new_r < MAP_ROWS and 0 <= new_c < MAP_COLS:
        st.session_state.player_pos = [new_r, new_c]
        # After moving, check tile
        pos = tuple(st.session_state.player_pos)
        if pos == POKEMON_CENTER:
            heal_party()
            st.session_state.messages.append("You healed your party at the Pokémon Center!")
        elif pos in TRAINER_TILES:
            # only start trainer battle if trainer not defeated
            trainer_name = list(TRAINERS.keys())[list(TRAINER_TILES).index(pos) % len(TRAINERS)]
            if trainer_name in st.session_state.defeated_trainers:
                st.session_state.messages.append("This trainer has already been defeated.")
            else:
                start_trainer_battle(pos)
        elif pos in GRASS_TILES:
            # random encounter chance
            if random.random() < 0.45:
                try_start_wild_battle()
            else:
                st.session_state.messages.append("You walk through the grass... but nothing happened.")
        else:
            st.session_state.messages.append("You moved.")

# -----------------------
# STARTER SELECTION SCREEN
# -----------------------
st.title("🎮 Mini Pokémon — Expanded")

if st.session_state.screen == "start":
    st.subheader("Choose your starter Pokémon")
    cols = st.columns(len(STARTERS))
    idx = 0
    for name, data in STARTERS.items():
        with cols[idx]:
            st.write(f"### {name}")
            st.write(f"HP: {data['hp']}")
            if st.button(f"Choose {name}", key=f"starter_{name}"):
                p = copy.deepcopy(data)
                p['hp'] = p['max_hp']
                st.session_state.party = [p]
                st.session_state.screen = "map"
                st.session_state.messages = [f"You picked {name}!"]
        idx += 1
    st.write("---")
    st.write("Walk around the map, step on grass (🌿) to encounter wild Pokémon. Visit the Pokémon Center (🏥) to heal.")
    st.write("Trainers (👤) are waiting — defeat them to earn bragging rights!")

# -----------------------
# MAP SCREEN
# -----------------------
if st.session_state.screen == "map":
    map_col, ui_col = st.columns([3,2])
    with map_col:
        st.subheader("🌍 Overworld")
        st.text(draw_map())
        # Movement controls
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("⬅️ Left"):
                move_player(0, -1)
        with c2:
            if st.button("⬆️ Up"):
                move_player(-1, 0)
            if st.button("⬇️ Down"):
                move_player(1, 0)
        with c3:
            if st.button("➡️ Right"):
                move_player(0, 1)

        # show messages
        if st.session_state.messages:
            st.write("### Messages")
            for m in st.session_state.messages[-6:]:
                st.write("- " + m)

    with ui_col:
        st.subheader("Party")
        for i, p in enumerate(st.session_state.party):
            status = f"{p['name']} — HP: {p['hp']}/{p['max_hp']}"
            if p['hp'] <= 0:
                status += " (fainted)"
            st.write(status)
        st.write("---")
        st.write(f"🎒 Pokéballs: {st.session_state.pokeballs}")
        st.write(f"🏆 Defeated Trainers: {len(st.session_state.defeated_trainers)}")

# -----------------------
# BATTLE SCREEN
# -----------------------
if st.session_state.screen == "battle":
    battle_col, info_col = st.columns([3,2])
    with battle_col:
        enemy = st.session_state.enemy_party[st.session_state.active_enemy_idx]
        st.subheader(f"⚔️ Battle — {'Wild' if st.session_state.battle_type=='wild' else 'Trainer'} {enemy['name']}")
        # show enemy HP
        st.write(f"{enemy['name']} — HP: {enemy['hp']}/{enemy['max_hp']}")
        # show active player (first alive)
        active_player = None
        for p in st.session_state.party:
            if p['hp'] > 0:
                active_player = p
                break
        if active_player is None:
            st.write("All your Pokémon have fainted...")
        else:
            st.write(f"Your active Pokémon: {active_player['name']} — HP: {active_player['hp']}/{active_player['max_hp']}")

            # Moves
            st.write("### Moves")
            move_cols = st.columns(2)
            for i, mv in enumerate(active_player['moves']):
                name, lo, hi = mv
                if move_cols[i%2].button(f"{name} ({lo}-{hi})", key=f"mv_{i}"):
                    # player attacks
                    msg = perform_attack(active_player, enemy, mv)
                    st.session_state.messages.append(msg)
                    # check if enemy fainted
                    if enemy['hp'] <= 0:
                        st.session_state.messages.append(f"{enemy['name']} fainted!")
                        ended = check_battle_end()
                        if not ended:
                            # if trainer battle and enemy party still has members, move to next
                            if st.session_state.battle_type == "trainer":
                                st.session_state.active_enemy_idx += 1
                                st.session_state.messages.append(f"Trainer sends out {st.session_state.enemy_party[st.session_state.active_enemy_idx]['name']}!")
                    else:
                        # enemy turn
                        enemy_turn_if_alive()
                        check_battle_end()
                    st.rerun()  # refresh UI after each move

            # Wild-only actions
            if st.session_state.battle_type == "wild":
                st.write("---")
                b1, b2, b3 = st.columns(3)
                with b1:
                    if b1.button("🎱 Throw Pokéball"):
                        try_catch_wild()
                        st.rerun()
                with b2:
                    if b2.button("🏃 Run Away"):
                        try_run_away()
                        st.rerun()
                with b3:
                    if b3.button("Switch Pokémon"):
                        st.session_state.show_switch = True

    with info_col:
        st.subheader("Battle Info & Party")
        # messages
        st.write("### Log")
        for m in st.session_state.messages[-8:]:
            st.write("- " + m)
        st.write("---")
        # Party and switch options
        st.write("### Party")
        for i, p in enumerate(st.session_state.party):
            btn_key = f"switch_{i}"
            txt = f"{p['name']} — HP: {p['hp']}/{p['max_hp']}"
            if st.button(f"Switch to {txt}", key=btn_key):
                if p['hp'] <= 0:
                    st.session_state.messages.append(f"Can't switch to {p['name']} (fainted).")
                else:
                    switch_active_pokemon(i)
                    st.rerun()

# -----------------------
# FOOTER / DEBUG
# -----------------------
st.write("---")
st.caption("Built as a simplified Pokémon-like demo. Mechanics are simplified for clarity.")

# =============================
# EXTRA FEATURES: Pokédollars, Pokémart, Refresh Map
# =============================

import random
import streamlit as st

# --- Ensure session state variables exist ---
if "pokedollars" not in st.session_state:
    st.session_state.pokedollars = 500  # starting money
if "pokeballs" not in st.session_state:
    st.session_state.pokeballs = 5      # starting Pokéballs

# --- Function to refresh map (keeps party, money, items) ---
def refresh_map():
    rows, cols = len(st.session_state.grid), len(st.session_state.grid[0])
    new_grid = []
    for r in range(rows):
        row = []
        for c in range(cols):
            rand_val = random.random()
            if rand_val < 0.1:
                row.append("G")  # Grass
            elif rand_val < 0.15:
                row.append("C")  # Pokémon Center
            elif rand_val < 0.20:
                row.append("T")  # Trainer
            elif rand_val < 0.25:
                row.append("M")  # Pokémart
            else:
                row.append(".")  # Empty
        new_grid.append(row)
    st.session_state.grid = new_grid

# --- Reward after winning a trainer battle ---
def trainer_victory_reward():
    reward = 200
    st.session_state.pokedollars += reward
    st.success(f"You won {reward} Pokédollars!")

# --- Pokémart UI (triggered when stepping on 'M') ---
def pokemart_ui():
    st.subheader("Welcome to the Pokémart!")
    st.write(f"You have 💰 {st.session_state.pokedollars} Pokédollars.")
    st.write(f"Pokéballs in bag: {st.session_state.pokeballs}")

    if st.button("Buy Pokéball (200 Pokédollars)", key="buy_pokeball"):
        if st.session_state.pokedollars >= 200:
            st.session_state.pokedollars -= 200
            st.session_state.pokeballs += 1
            st.success("You bought a Pokéball!")
        else:
            st.error("Not enough money!")

# --- Refresh button on the map page ---
def refresh_button():
    if st.button("🔄 Refresh Map", key="refresh_map"):
        refresh_map()
        st.success("The map has been refreshed!")

import random

def generate_map(rows=10, cols=10):
    grid = []
    has_center = False
    has_mart = False

    for r in range(rows):
        row = []
        for c in range(cols):
            rand_val = random.random()
            if rand_val < 0.1:
                row.append("G")  # Grass
            elif rand_val < 0.15:
                row.append("C")  # Pokémon Center
                has_center = True
            elif rand_val < 0.20:
                row.append("T")  # Trainer
            elif rand_val < 0.25:
                row.append("M")  # Pokémart
                has_mart = True
            else:
                row.append(".")  # Empty space
        grid.append(row)

    # Guarantee at least one Pokémon Center
    if not has_center:
        rand_r, rand_c = random.randint(0, rows-1), random.randint(0, cols-1)
        grid[rand_r][rand_c] = "C"

    # Guarantee at least one Pokémart
    if not has_mart:
        rand_r, rand_c = random.randint(0, rows-1), random.randint(0, cols-1)
        grid[rand_r][rand_c] = "M"

    return grid
