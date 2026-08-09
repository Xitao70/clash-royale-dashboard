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
    """Cria e configura uma sessão HTTP com autenticação e retentativas."""
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
    return "%23" + quote(clean, safe="")

def fetch_player(session: requests.Session, player_tag: str, timeout: int = 10) -> Dict[str, Any]:
    """Busca dados de um jogador pela API e trata erros HTTP específicos."""
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
    """Imprime dados de jogador no terminal de forma formatada."""
    print("--- Dados do Jogador ---")
    print(f"Nome: {player.get('name')}")
    print(f"Nível: {player.get('expLevel')}")
    print(f"Troféus: {player.get('trophies')}")
    clan = player.get("clan") or {}
    print(f"Clã: {clan.get('name', 'Sem clã')}")

    cards = player.get("cards") or []
    if cards:
        print("\n--- Cartas do Jogador ---")
        for c in cards:
            nome = c.get("name", "Desconhecida")
            nivel = c.get("level", "?")
            print(f"   - {nome} (Nível: {nivel})")
    else:
        print("\n(Sem lista de cartas disponível.)")

def save_to_file(data: Dict[str, Any], filename: str) -> None:
    """Salva um dicionário em um arquivo JSON com formatação legível."""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        logging.info("Dados salvos com sucesso em: %s", filename)
    except Exception as e:
        logging.error("Erro ao salvar arquivo %s: %s", filename, e)

def main() -> None:
    """Função principal que coordena a busca e exibição/salvamento dos dados."""
    player_tag = os.getenv("CR_PLAYER_TAG", "RJ8CGQYCV")
    output_file = os.getenv("CR_OUTPUT_FILE3") # Novo: variável de ambiente para o arquivo de saída
    
    logging.info("Buscando informações para o jogador: %s", player_tag)

    try:
        session = make_session(API_KEY)
        data = fetch_player(session, player_tag)
        
        # Salva o arquivo antes de imprimir, se a variável estiver definida
        if output_file:
            save_to_file(data, output_file)
        
        # Sempre imprime no terminal
        print_player(data)

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