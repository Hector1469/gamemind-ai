import requests
import logging

logging.basicConfig(
    filename='agent_debug.log',
    level=logging.DEBUG,
    format='%(asctime)s %(message)s',
    datefmt='%H:%M:%S',
    force=True
)
logger = logging.getLogger('steam_api')

BANNED_TERMS = [
    "hentai",
    "sex",
    "waifu",
    "boobs",
    "futa",
    "nsfw",
    "porn"
]


def search_game(query):

    logger.info(f"[SEARCH] Tool llamada con input: '{query}'")

    try:

        # =========================
        # Buscar juego
        # =========================

        search_url = (
            "https://store.steampowered.com/api/storesearch/"
        )

        params = {
            "term": query,
            "l": "english",
            "cc": "US"
        }

        response = requests.get(
            search_url,
            params=params,
            timeout=20
        )

        logger.info(f"[SEARCH] Status code: {response.status_code}")

        if response.status_code != 200:
            return f"Steam search error: {response.status_code}"

        data = response.json()

        items = data.get("items", [])

        if not items:
            logger.info("[SEARCH] No se encontró ningún juego")
            return "No game found."

        game = items[0]

        appid = game["id"]

        logger.info(f"[SEARCH] Juego encontrado: {game['name']} (appid: {appid})")

        # =========================
        # Obtener detalles
        # =========================

        details_url = (
            f"https://store.steampowered.com/api/appdetails"
        )

        details_response = requests.get(
            details_url,
            params={"appids": appid},
            timeout=20
        )

        logger.info(
            f"[SEARCH] Details status: "
            f"{details_response.status_code}"
        )

        if details_response.status_code != 200:
            return "Error retrieving game details."

        details_data = details_response.json()

        game_data = details_data[str(appid)]["data"]

        # =========================
        # Extraer datos
        # =========================

        name = game_data.get("name", "Unknown")

        description = game_data.get(
            "short_description",
            "No description"
        )

        genres = []

        if "genres" in game_data:
            genres = [
                g["description"]
                for g in game_data["genres"]
            ]

        tags = get_game_tags(appid)

        if not tags:
            logger.info("[SEARCH] No tags found, using genres as fallback")
            tags = genres

        developers = game_data.get(
            "developers",
            []
        )

        release_date = game_data.get(
            "release_date",
            {}
        ).get("date", "Unknown")

        logger.info(f"[SEARCH] Devolviendo datos de: {name}")
        logger.info(f"[SEARCH] Géneros: {genres}")
        logger.info(f"[SEARCH] Developers: {developers}")

        return f"""
Name: {name}

Genres: {', '.join(genres)}

Tags: {', '.join(tags[:10])}

Developers: {', '.join(developers)}

Release Date: {release_date}

Description:
{description}
"""

    except Exception as e:
        logger.error(f"[SEARCH ERROR] {e}")
        import json
        return json.dumps({
            "status": "error",
            "source": "steam_api",
            "message": str(e),
            "data": None
        })


def recommend_similar_games(query: str):

    logger.info(f"{'='*60}")
    logger.info(f"[RECOMMEND] Tool llamada con input: '{query}'")
    logger.info(f"{'='*60}")

    try:

        # --- Paso 1: Parsear input (genres | exclude_game) ---
        exclude_game = ""
        if "|" in query:
            genres_part, exclude_game = query.rsplit("|", 1)
            exclude_game = exclude_game.strip().lower()
        else:
            genres_part = query

        all_tags = [g.strip() for g in genres_part.split(",")]
        main_tag = all_tags[0]
        secondary_tags = [t.lower() for t in all_tags[1:]] if len(all_tags) > 1 else []

        logger.info(f"[RECOMMEND] Tags parseados: {all_tags}")
        logger.info(f"[RECOMMEND] Tag principal (usado para buscar): '{main_tag}'")
        if secondary_tags:
            logger.info(f"[RECOMMEND] Tags secundarios (para filtrar): {secondary_tags}")
        if exclude_game:
            logger.info(f"[RECOMMEND] Juego excluido: '{exclude_game}'")

        # --- Paso 2: Llamada a SteamSpy API por tag ---
        steamspy_url = "https://steamspy.com/api.php"
        params = {
            "request": "tag",
            "tag": main_tag
        }
        logger.info(f"[RECOMMEND] Buscando en SteamSpy API: {steamspy_url}")
        logger.info(f"[RECOMMEND] Parámetros: {params}")

        response = requests.get(
            steamspy_url,
            params=params,
            timeout=5
        )

        logger.info(f"[RECOMMEND] Status code: {response.status_code}")

        if response.status_code != 200:
            return f"SteamSpy API error: {response.status_code}"

        data = response.json()
        total_items = len(data)
        logger.info(f"[RECOMMEND] Total resultados de SteamSpy: {total_items}")

        if not data:
            logger.info(f"[RECOMMEND] Sin resultados, devolviendo mensaje vacío")
            return "No recommendations found."

        # --- Paso 3: Filtrar y puntuar ---
        candidates = []
        for appid, info in data.items():

            name = info.get("name", "Unknown")

            lower_name = name.lower()

            # =========================
            # Filtrar NSFW
            # =========================

            if any(
                term in lower_name
                for term in BANNED_TERMS
            ):
                logger.info(
                    f"[RECOMMEND] EXCLUDED NSFW: {name}"
                )
                continue

            # =========================
            # Tags del juego
            # =========================

            game_tags = [
                t.lower()
                for t in info.get("tags", {}).keys()
            ]

            # =========================
            # SteamSpy score_rank
            # =========================

            score = info.get("score_rank", "0")

            score = (
                int(score)
                if score and str(score).isdigit()
                else 0
            )

            # =========================
            # Reviews
            # =========================

            positive = int(
                info.get("positive", 0)
            )

            negative = int(
                info.get("negative", 0)
            )

            review_score = 0

            if positive + negative > 0:
                review_score = (
                    positive /
                    (positive + negative)
                )

            # =========================
            # Matching tags
            # =========================

            matching = sum(
                1
                for st in secondary_tags
                if st.lower() in game_tags
            )

            # =========================
            # Ranking final
            # =========================

            weighted_score = (
                matching * 100
                + review_score * 50
                + score
            )

            logger.info(
                f"[RECOMMEND] {name} | "
                f"matching={matching} | "
                f"review_score={review_score:.2f} | "
                f"score_rank={score} | "
                f"weighted={weighted_score:.2f}"
            )

            candidates.append({
                "name": name,
                "score": score,
                "matching_tags": matching,
                "review_score": review_score,
                "weighted_score": weighted_score,
                "appid": appid
            })

        # Ordenar: más tags coincidentes primero, luego por score
        candidates.sort(key=lambda x: (x["matching_tags"], x["score"]), reverse=True)

        # --- Paso 4: Seleccionar top 5 ---
        top = candidates[:5]

        logger.info(f"[RECOMMEND] Top 5 seleccionados:")
        for i, c in enumerate(top):
            logger.info(f"[RECOMMEND]   [{i+1}] {c['name']} (score: {c['score']}, matching_tags: {c['matching_tags']})")
        logger.info(f"{'='*60}")

        if not top:
            return "No recommendations found after filtering."

        result_lines = [f"{c['name']}" for c in top]
        return "Games similar based on genre:\n- " + "\n- ".join(result_lines)

    except Exception as e:
        logger.error(f"[RECOMMEND ERROR] {e}")
        import json
        return json.dumps({
            "status": "error",
            "source": "steamspy",
            "message": str(e),
            "data": None
        })



def get_game_genres(appid):
    details_url = "https://store.steampowered.com/api/appdetails"

    response = requests.get(details_url, params={"appids": appid}, timeout=20)

    data = response.json()

    game_data = data[str(appid)]["data"]

    genres = []

    if "genres" in game_data:
        genres = [g["description"] for g in game_data["genres"]]

    return genres

BAD_TAGS = {
    "Action",
    "Adventure",
    "Indie",
    "Casual",
    "Singleplayer",
    "Multiplayer",
    "Atmospheric",
    "Great Soundtrack"
}

def get_game_tags(appid):

    logger.info(f"[TAGS] Getting SteamSpy tags for appid={appid}")

    url = "https://steamspy.com/api.php"

    params = {
        "request": "appdetails",
        "appid": appid
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=5
        )

        data = response.json()

        raw_tags = data.get("tags", {})

        if isinstance(raw_tags, dict):
            tags = list(raw_tags.keys())

        elif isinstance(raw_tags, list):
            tags = raw_tags

        else:
            tags = []
            
    except Exception as e:
        logger.warning(f"[TAGS] SteamSpy request failed: {e}")
        tags = []

    filtered_tags = [
        t for t in tags
        if t not in BAD_TAGS
    ]

    logger.info(f"[TAGS] Tags obtenidos: {tags}")

    return filtered_tags


def search_games_semantically(query: str, top_k: int = 5):
    import os
    import json
    from langchain_community.vectorstores import Chroma
    from langchain_huggingface import HuggingFaceEmbeddings

    logger.info(f"[GAME RAG] Query: {query}")

    db_dir = "./chroma_db_games"
    if not os.path.exists(db_dir):
        logger.error("[GAME RAG] Base de datos Chroma no encontrada.")
        return json.dumps({
            "status": "error",
            "source": "chroma_db",
            "message": "Local RAG database is missing or offline",
            "data": None
        })

    try:
        db = Chroma(
            persist_directory=db_dir,
            embedding_function=HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-mpnet-base-v2"
            )
        )

        results = db.similarity_search(query, k=top_k)

        output = ["🎮 Games ranked by player experience:\n"]

        for r in results:
            game = r.metadata.get("game", "Unknown")
            output.append(
                f"- {game}\n"
                f"  {r.page_content[:250]}\n"
            )

        return "\n".join(output)
        
    except Exception as e:
        logger.error(f"[GAME RAG ERROR] {e}")
        return json.dumps({
            "status": "error",
            "source": "chroma_db",
            "message": str(e),
            "data": None
        })