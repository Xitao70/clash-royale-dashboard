from card_roles import ROLE_LABELS, roles_da_carta


# Regras heurísticas iniciais de interação entre funções.
# Não representam resultado garantido de uma partida; apenas "respostas naturais".
ROLE_RESPONSES = [
    {
        "defender_role": "anti_air",
        "attacker_role": "air",
        "label": "Anti-aéreo responde a unidade aérea",
        "weight": 3,
    },
    {
        "defender_role": "small_spell",
        "attacker_role": "swarm",
        "label": "Feitiço leve responde a enxame",
        "weight": 3,
    },
    {
        "defender_role": "splash",
        "attacker_role": "swarm",
        "label": "Dano em área responde a enxame",
        "weight": 3,
    },
    {
        "defender_role": "tank_killer",
        "attacker_role": "tank",
        "label": "Mata-tanque responde a tanque",
        "weight": 3,
    },
    {
        "defender_role": "building",
        "attacker_role": "building_target",
        "label": "Construção pode puxar condição focada em construções",
        "weight": 2,
    },
    {
        "defender_role": "reset",
        "attacker_role": "inferno",
        "label": "Reset interfere na mecânica Inferno",
        "weight": 3,
    },
    {
        "defender_role": "big_spell",
        "attacker_role": "ranged",
        "label": "Feitiço pesado pode punir suporte de longo alcance",
        "weight": 1,
    },
    {
        "defender_role": "control",
        "attacker_role": "building_target",
        "label": "Controle pode atrasar unidade focada em construções",
        "weight": 1,
    },
]


def respostas_naturais(deck_defensor, deck_atacante):
    """
    Retorna possíveis respostas naturais do deck defensor contra o deck atacante.
    Cada resultado é uma interação carta x carta baseada em funções táticas.
    """

    respostas = []

    for atacante in deck_atacante or []:
        nome_atacante = atacante.get("name", "Carta")
        roles_atacante = roles_da_carta(nome_atacante)

        if not roles_atacante:
            continue

        for defensor in deck_defensor or []:
            nome_defensor = defensor.get("name", "Carta")
            roles_defensor = roles_da_carta(nome_defensor)

            if not roles_defensor:
                continue

            for regra in ROLE_RESPONSES:
                if (
                    regra["defender_role"] in roles_defensor
                    and regra["attacker_role"] in roles_atacante
                ):
                    respostas.append(
                        {
                            "defender": nome_defensor,
                            "attacker": nome_atacante,
                            "defender_role": regra["defender_role"],
                            "attacker_role": regra["attacker_role"],
                            "label": regra["label"],
                            "weight": regra["weight"],
                        }
                    )

    return respostas


def resumir_respostas(respostas):
    """
    Agrupa as interações por carta atacante para evitar uma lista excessiva.
    """

    por_ameaca = {}

    for item in respostas:
        ameaca = item["attacker"]

        if ameaca not in por_ameaca:
            por_ameaca[ameaca] = []

        por_ameaca[ameaca].append(item)

    resumo = []

    for ameaca, itens in por_ameaca.items():
        melhores = sorted(
            itens,
            key=lambda item: (-item["weight"], item["defender"])
        )

        vistos = set()
        unicos = []

        for item in melhores:
            chave = (item["defender"], item["label"])

            if chave in vistos:
                continue

            vistos.add(chave)
            unicos.append(item)

        resumo.append(
            {
                "attacker": ameaca,
                "responses": unicos[:5],
                "score": sum(item["weight"] for item in unicos[:5]),
            }
        )

    return sorted(
        resumo,
        key=lambda item: (-item["score"], item["attacker"])
    )


def cobertura_respostas(deck_defensor, deck_atacante):
    """
    Mede quantas cartas do deck atacante têm ao menos uma resposta natural
    mapeada no deck defensor.
    """

    nomes_atacantes = {
        carta.get("name")
        for carta in deck_atacante or []
        if carta.get("name")
    }

    respostas = respostas_naturais(deck_defensor, deck_atacante)

    ameacas_cobertas = {
        item["attacker"]
        for item in respostas
    }

    total = len(nomes_atacantes)
    cobertas = len(ameacas_cobertas)

    percentual = (cobertas / total * 100) if total else 0

    return {
        "cobertas": cobertas,
        "total": total,
        "percentual": percentual,
        "detalhes": resumir_respostas(respostas),
    }


def explicar_role(role):
    return ROLE_LABELS.get(role, role)
