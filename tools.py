from langchain_core.tools import tool

from steam_api import (search_game, recommend_similar_games, search_games_semantically)

@tool
def search_game_tool(query: str) -> str:
    """Search Steam games and return info"""
    return search_game(query)

@tool
def recommend_games_tool(query: str) -> str:
    """Recommend games by genre tags.
    Input MUST be comma-separated genre/tag names, NOT a game name.
    Optionally append '|game_name' to exclude the original game from results.
    Example input: 'Action, Adventure, Indie|Hollow Knight'"""
    return recommend_similar_games(query)


@tool
def game_profile_rag_tool(query: str) -> str:
    """
    Semantic game search using aggregated Steam review profiles.
    Use this when the user asks:
    - 'games like X'
    - 'spiritual successor'
    - 'similar to ...'
    - or subjective experience-based recommendations
    """
    return search_games_semantically(query)