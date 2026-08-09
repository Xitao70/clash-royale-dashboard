import os
import json
import logging
from typing import Any, Dict, Optional
from urllib.parse import quote
from dotenv import load_dotenv
import requests
from requests.adapters import HTTPAdapter, Retry

# ----------------- Setup -----------------
load_dotenv()
API_KEY = os.getenv("CLASH_ROYALE_API_KEY")
if not API_KEY:
    raise SystemExit("Erro: defina CLASH_ROYALE_API_KEY no .env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

BASE_URL = "https://api.clashroyale.com/v1"

def make_session(api_key: str) -> requests.Session:
    s = requests.Session()
    retries = Retry(
        total=3,
        connect=3,
        read=3,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET"])
    )
    s.headers.update({
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}"
    })
    s.mount("https://", HTTPAdapter(max_retries=retries))
    return s

def encode_tag(tag: str) -> str:
    """Remove '#' e espaços e retorna tag segura para path da URL."""
    clean = tag.strip().lstrip("#").upper()
    # Clash Royale espera %23<tag> no path (o %23 representa '#')
    return "%23" + quote(clean, safe="")

def fetch_player(session: requests.Session, player_tag: str, timeout: int = 10) -> Dict[str, Any]:
    url = f"{BASE_URL}/players/{encode_tag(player_tag)}"
    resp = session.get(url, timeout=timeout)

    # Mensagens específicas por status
    if resp.status_code == 403:
        raise PermissionError("403 Forbidden: verifique se o IP do seu servidor está na allowlist do portal da Supercell/CR API e se a chave é válida.")
    if resp.status_code == 404:
        raise LookupError("404 Not Found: tag de jogador inexistente ou privado.")
    if resp.status_code == 429:
        reset = resp.headers.get("X-RateLimit-Reset")
        raise RuntimeError(f"429 Too Many Requests: aguarde o reset (X-RateLimit-Reset={reset}).")
    resp.raise_for_status()

    # Opcional: log de rate limit
    remaining = resp.headers.get("X-RateLimit-Remaining")
    limit = resp.headers.get("X-RateLimit-Limit")
    if remaining and limit:
        logging.info("Rate limit: %s/%s restantes", remaining, limit)

    return resp.json()

def print_player(player: Dict[str, Any]) -> None:
    print("--- Dados do Jogador ---")
    print(f"Nome: {player.get('name')}")
    print(f"Nível: {player.get('expLevel')}")
    print(f"Troféus: {player.get('trophies')}")
    clan = player.get("clan") or {}
    print(f"Clã: {clan.get('name', 'Sem clã')}")

    # Cartas (pode não existir em alguns contextos)
    cards = player.get("cards") or []
    if cards:
        print("\n--- Cartas do Jogador ---")
        for c in cards:
            nome = c.get("name", "Desconhecida")
            nivel = c.get("level", "?")
            print(f"  - {nome} (Nível: {nivel})")
    else:
        print("\n(Sem lista de cartas disponível.)")

def main() -> None:
    # Pode vir de env, CLI, etc.
    player_tag = os.getenv("CR_PLAYER_TAG", "P9RV222GG")
    logging.info("Buscando informações para o jogador: %s", player_tag)

    try:
        session = make_session(API_KEY)
        data = fetch_player(session, player_tag)
        print_player(data)

        # Debug opcional:
        # print(json.dumps(data, indent=2, ensure_ascii=False))

    except (requests.exceptions.RequestException) as e:
        logging.error("Erro de rede/HTTP: %s", e)
    except PermissionError as e:
        logging.error("%s", e)
    except LookupError as e:
        logging.error("%s", e)
    except RuntimeError as e:
        logging.error("%s", e)
    except Exception as e:
        logging.exception("Erro inesperado: %s", e)

if __name__ == "__main__":
    main()
