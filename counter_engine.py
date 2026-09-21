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


THREAT_ROLES = {
    "win_condition": 5,
    "tank": 4,
    "building_target": 4,
    "tank_killer": 3,
    "swarm": 2,
    "air": 2,
    "ranged": 1,
    "pressure": 3,
}


def classificar_ameacas(deck):
    """
    Pontua cartas por relevância ofensiva/estratégica com base em suas funções.
    A pontuação é heurística e serve apenas para priorização visual.
    """

    ameacas = []

    for carta in deck or []:
        nome = carta.get("name", "Carta")
        roles = roles_da_carta(nome)

        if not roles:
            continue

        score = sum(
            peso
            for role, peso in THREAT_ROLES.items()
            if role in roles
        )

        if score <= 0:
            continue

        ameacas.append(
            {
                "name": nome,
                "roles": roles,
                "score": score,
                "elixir": carta.get("elixirCost"),
            }
        )

    return sorted(
        ameacas,
        key=lambda item: (-item["score"], item["name"])
    )


def respostas_para_ameaca(deck_defensor, nome_ameaca):
    """
    Retorna respostas naturais do deck defensor contra uma carta específica.
    """

    respostas = []

    for defensor in deck_defensor or []:
        nome_defensor = defensor.get("name", "Carta")
        roles_defensor = roles_da_carta(nome_defensor)
        roles_ameaca = roles_da_carta(nome_ameaca)

        if not roles_defensor or not roles_ameaca:
            continue

        for regra in ROLE_RESPONSES:
            if (
                regra["defender_role"] in roles_defensor
                and regra["attacker_role"] in roles_ameaca
            ):
                respostas.append(
                    {
                        "defender": nome_defensor,
                        "label": regra["label"],
                        "weight": regra["weight"],
                    }
                )

    # Remove duplicações e prioriza regras mais fortes.
    respostas_ordenadas = sorted(
        respostas,
        key=lambda item: (-item["weight"], item["defender"])
    )

    vistos = set()
    unicos = []

    for item in respostas_ordenadas:
        chave = (item["defender"], item["label"])

        if chave in vistos:
            continue

        vistos.add(chave)
        unicos.append(item)

    return unicos


def identificar_vulnerabilidades(deck_defensor, deck_atacante, limite_ameacas=5):
    """
    Identifica ameaças ofensivas do adversário para as quais o deck defensor
    tem poucas ou nenhuma resposta natural mapeada.

    Retorna uma lista ordenada por gravidade heurística:
    - 0 respostas: vulnerabilidade alta
    - 1 resposta: vulnerabilidade moderada
    - 2+ respostas: não entra na lista principal
    """

    ameacas = classificar_ameacas(deck_atacante)[:limite_ameacas]
    vulnerabilidades = []

    for ameaca in ameacas:
        respostas = respostas_para_ameaca(
            deck_defensor,
            ameaca["name"]
        )

        qtd = len(respostas)

        if qtd >= 2:
            continue

        if qtd == 0:
            nivel = "alta"
            gravidade = 2
        else:
            nivel = "moderada"
            gravidade = 1

        vulnerabilidades.append(
            {
                "threat": ameaca["name"],
                "threat_score": ameaca["score"],
                "responses": respostas,
                "response_count": qtd,
                "level": nivel,
                "severity": gravidade,
            }
        )

    return sorted(
        vulnerabilidades,
        key=lambda item: (
            -item["severity"],
            -item["threat_score"],
            item["threat"]
        )
    )
