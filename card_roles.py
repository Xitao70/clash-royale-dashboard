# Base inicial de funções táticas das cartas do Clash Royale.
# As chaves usam os nomes em inglês retornados pela API oficial.
# Cartas não cadastradas devem ser tratadas como "não classificadas".

CARD_ROLES = {
    # Win conditions / pressure
    "Hog Rider": {"win_condition", "building_target"},
    "Royal Hogs": {"win_condition", "building_target"},
    "Ram Rider": {"win_condition", "building_target", "control"},
    "Battle Ram": {"win_condition", "building_target"},
    "Balloon": {"win_condition", "air"},
    "Goblin Barrel": {"win_condition", "bait"},
    "Skeleton Barrel": {"win_condition", "bait", "air"},
    "Miner": {"win_condition", "chip"},
    "Graveyard": {"win_condition", "swarm"},
    "X-Bow": {"win_condition", "building", "ranged"},
    "Mortar": {"win_condition", "building", "ranged"},
    "Goblin Drill": {"win_condition", "building"},
    "Royal Giant": {"win_condition", "tank", "ranged", "building_target"},
    "Giant": {"win_condition", "tank", "building_target"},
    "Goblin Giant": {"win_condition", "tank", "building_target"},
    "Electro Giant": {"win_condition", "tank", "building_target", "reset"},
    "Golem": {"win_condition", "tank", "building_target"},
    "Lava Hound": {"win_condition", "tank", "air", "building_target"},
    "Elixir Golem": {"win_condition", "tank", "building_target"},
    "Wall Breakers": {"win_condition", "building_target"},
    "Three Musketeers": {"win_condition", "ranged", "anti_air"},

    # Tanks / mini tanks / melee defense
    "P.E.K.K.A": {"tank_killer", "mini_tank"},
    "Mini P.E.K.K.A": {"tank_killer", "mini_tank"},
    "Mega Knight": {"tank", "splash", "control"},
    "Knight": {"mini_tank"},
    "Golden Knight": {"mini_tank", "control"},
    "Valkyrie": {"mini_tank", "splash"},
    "Dark Prince": {"mini_tank", "splash"},
    "Prince": {"mini_tank", "tank_killer"},
    "Giant Skeleton": {"tank", "splash"},
    "Skeleton King": {"mini_tank", "swarm"},
    "Mighty Miner": {"tank_killer", "mini_tank"},
    "Monk": {"mini_tank", "control"},

    # Anti-air / ranged support
    "Musketeer": {"ranged", "anti_air"},
    "Electro Wizard": {"ranged", "anti_air", "reset"},
    "Ice Wizard": {"ranged", "anti_air", "splash", "control"},
    "Wizard": {"ranged", "anti_air", "splash"},
    "Executioner": {"ranged", "anti_air", "splash"},
    "Hunter": {"ranged", "anti_air", "tank_killer"},
    "Magic Archer": {"ranged", "anti_air", "splash"},
    "Firecracker": {"ranged", "anti_air", "splash"},
    "Princess": {"ranged", "anti_air", "splash", "bait"},
    "Dart Goblin": {"ranged", "anti_air", "bait"},
    "Archers": {"ranged", "anti_air"},
    "Little Prince": {"ranged", "anti_air"},
    "Flying Machine": {"ranged", "anti_air", "air"},
    "Mother Witch": {"ranged", "anti_air", "control"},
    "Witch": {"ranged", "anti_air", "splash", "swarm"},
    "Night Witch": {"support", "air_support"},
    "Bowler": {"ranged", "splash", "control"},
    "Sparky": {"ranged", "tank_killer", "splash"},
    "Zappies": {"ranged", "anti_air", "reset", "control"},

    # Air troops
    "Baby Dragon": {"air", "anti_air", "splash"},
    "Inferno Dragon": {"air", "anti_air", "tank_killer", "inferno"},
    "Mega Minion": {"air", "anti_air"},
    "Minions": {"air", "anti_air", "swarm"},
    "Minion Horde": {"air", "anti_air", "swarm"},
    "Bats": {"air", "anti_air", "swarm", "cycle"},
    "Phoenix": {"air", "anti_air"},
    "Skeleton Dragons": {"air", "anti_air", "splash"},

    # Swarms / cycle
    "Skeletons": {"swarm", "cycle"},
    "Skeleton Army": {"swarm", "tank_killer"},
    "Goblin Gang": {"swarm", "bait"},
    "Goblins": {"swarm", "cycle"},
    "Spear Goblins": {"swarm", "anti_air", "cycle"},
    "Guards": {"swarm"},
    "Barbarians": {"swarm", "tank_killer"},
    "Elite Barbarians": {"tank_killer"},
    "Royal Recruits": {"swarm", "control"},
    "Rascals": {"swarm", "ranged"},
    "Ice Spirit": {"cycle", "control", "anti_air"},
    "Fire Spirit": {"cycle", "splash", "anti_air"},
    "Electro Spirit": {"cycle", "reset", "splash", "anti_air"},
    "Heal Spirit": {"cycle", "support"},

    # Buildings
    "Cannon": {"building", "defense"},
    "Tesla": {"building", "defense", "anti_air"},
    "Bomb Tower": {"building", "defense", "splash"},
    "Inferno Tower": {"building", "defense", "tank_killer", "anti_air", "inferno"},
    "Goblin Cage": {"building", "defense"},
    "Tombstone": {"building", "defense", "swarm"},
    "Furnace": {"building", "defense", "splash"},
    "Goblin Hut": {"building", "defense", "swarm"},
    "Barbarian Hut": {"building", "defense", "swarm"},
    "Elixir Collector": {"building", "economy"},

    # Small / utility spells
    "Zap": {"small_spell", "reset", "splash"},
    "The Log": {"small_spell", "splash", "control"},
    "Arrows": {"small_spell", "splash", "anti_air"},
    "Giant Snowball": {"small_spell", "splash", "control", "anti_air"},
    "Barbarian Barrel": {"small_spell", "splash"},
    "Royal Delivery": {"small_spell", "splash", "defense"},
    "Tornado": {"utility_spell", "control", "splash"},
    "Freeze": {"utility_spell", "control"},
    "Rage": {"utility_spell", "support"},
    "Clone": {"utility_spell", "support"},
    "Mirror": {"utility_spell"},
    "Earthquake": {"utility_spell", "building_pressure"},

    # Big spells
    "Fireball": {"big_spell", "splash", "anti_air"},
    "Poison": {"big_spell", "splash", "anti_air", "control"},
    "Lightning": {"big_spell", "anti_air", "reset"},
    "Rocket": {"big_spell", "splash", "anti_air"},
    "Void": {"big_spell", "tank_killer"},

    # Other support/control
    "Bandit": {"mini_tank", "pressure"},
    "Fisherman": {"control", "tank_killer"},
    "Lumberjack": {"mini_tank", "support"},
    "Goblin Demolisher": {"splash", "pressure"},
}

ROLE_LABELS = {
    "win_condition": "🏁 Condição de vitória",
    "building_target": "🎯 Foco em construções",
    "tank": "🛡️ Tanque",
    "mini_tank": "🛡️ Mini-tanque",
    "tank_killer": "💥 Mata-tanque",
    "ranged": "🏹 Alcance",
    "anti_air": "☁️ Anti-aéreo",
    "air": "🪽 Unidade aérea",
    "air_support": "🪽 Suporte aéreo",
    "splash": "💫 Dano em área",
    "building": "🏰 Construção",
    "defense": "🧱 Defesa",
    "reset": "⚡ Reset",
    "small_spell": "✨ Feitiço leve",
    "big_spell": "🔥 Feitiço pesado",
    "utility_spell": "🌀 Feitiço utilitário",
    "swarm": "🐝 Enxame",
    "bait": "🎣 Bait",
    "cycle": "🔄 Ciclo",
    "control": "🧲 Controle",
    "support": "🤝 Suporte",
    "chip": "🪙 Dano de chip",
    "pressure": "🚨 Pressão",
    "building_pressure": "🏚️ Pressão em construções",
    "economy": "💧 Economia de elixir",
    "inferno": "🔥 Mecânica Inferno",
}


def roles_da_carta(nome):
    return CARD_ROLES.get(nome, set())


def resumo_de_roles(deck):
    contagem = {}
    classificadas = 0
    nao_classificadas = []

    for carta in deck or []:
        nome = carta.get("name", "")
        roles = roles_da_carta(nome)

        if roles:
            classificadas += 1
        else:
            nao_classificadas.append(nome or "Carta sem nome")

        for role in roles:
            contagem[role] = contagem.get(role, 0) + 1

    total = len(deck or [])
    cobertura = (classificadas / total * 100) if total else 0

    return {
        "contagem": contagem,
        "classificadas": classificadas,
        "total": total,
        "cobertura": cobertura,
        "nao_classificadas": nao_classificadas,
    }
