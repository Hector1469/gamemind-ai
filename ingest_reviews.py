import requests
import os
from collections import defaultdict
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

GAMES = {
    "268500": "XCOM 2",
    "367520": "Hollow Knight",
    "413150": "Stardew Valley",
    "1086940": "Baldur's Gate 3",
    "292030": "The Witcher 3",
    "289070": "Civilization VI",
    "8930": "Civilization V",
    "105600": "Terraria"
}

def get_reviews(appid):
    url = f"https://store.steampowered.com/appreviews/{appid}"
    params = {"json": 1, "language": "english", "num_per_page": 100}

    try:
        r = requests.get(url, params=params, timeout=20)
        return r.json().get("reviews", [])
    except:
        return []


def build_game_profile(game_name, reviews):

    positives = []
    negatives = []

    for r in reviews:

        text = r.get("review", "").strip()
        if len(text) < 80:
            continue

        if r.get("voted_up"):
            positives.append(text)
        else:
            negatives.append(text)

    positives = positives[:20]
    negatives = negatives[:20]

    profile = f"""
GAME: {game_name}

PLAYER EXPERIENCE SUMMARY:

Positive player feedback:
{". ".join(positives)}

Negative player feedback:
{". ".join(negatives)}

TASK:
Summarize this game as a gameplay experience in 3-5 sentences.
Focus on:
- gameplay loop
- pacing
- difficulty
- emotional experience
- comparisons implied by players
"""

    return profile


def main():

    embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-mpnet-base-v2"
)

    documents = []

    for appid, game in GAMES.items():

        print(f"Processing {game}...")

        reviews = get_reviews(appid)

        if not reviews:
            continue

        profile_text = build_game_profile(game, reviews)

        doc = Document(
            page_content=profile_text,
            metadata={
                "game": game,
                "appid": appid
            }
        )

        documents.append(doc)

    print(f"Game profiles created: {len(documents)}")

    db = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory="./chroma_db_games"
    )

    print("DONE - Game-level RAG ready")


if __name__ == "__main__":
    main()