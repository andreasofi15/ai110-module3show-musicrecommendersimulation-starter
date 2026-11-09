"""
Command line runner for the Music Recommender Simulation.

Run from the project root with:  python -m src.main
"""

from pathlib import Path

from src.recommender import load_songs, recommend_songs

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "songs.csv"


def print_recommendations(
    profile_name: str, user_prefs: dict, songs: list, k: int = 5, artist_penalty: float = 0.0
) -> None:
    """Print a readable ranked list with each song's score and scoring reasons."""
    recommendations = recommend_songs(user_prefs, songs, k=k, artist_penalty=artist_penalty)

    print("=" * 60)
    print(f"Profile: {profile_name}")
    print(f"Preferences: {user_prefs}")
    print("=" * 60)
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"{rank}. {song['title']} by {song['artist']}  [{song['genre']} / {song['mood']}]")
        print(f"   Score: {score:.2f} / 5.00")
        for reason in explanation.split("; "):
            print(f"   - {reason}")
        print()


PROFILES = {
    # Default profile from Phase 2: high-energy pop fan
    "High-Energy Pop": {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
        "likes_acoustic": False,
        "valence": 0.8,
    },
    # Low-energy end of the catalog, where lofi has 3 songs
    "Chill Lofi": {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.4,
        "likes_acoustic": True,
        "valence": 0.6,
    },
    # Adversarial: energy and acousticness are inversely related in this catalog
    "Acoustic + High Energy (adversarial)": {
        "genre": "country",
        "mood": "nostalgic",
        "energy": 0.85,
        "likes_acoustic": True,
        "valence": 0.7,
    },
}


def main() -> None:
    songs = load_songs(str(DATA_PATH))
    print(f"Loaded songs: {len(songs)}\n")

    for name, user_prefs in PROFILES.items():
        print_recommendations(name, user_prefs, songs, k=5)

    # Stretch feature: diversity. Same Chill Lofi profile, but repeat artists lose 1.5 points per repeat.
    print_recommendations(
        "Chill Lofi + artist penalty 1.5 (diversity demo)",
        PROFILES["Chill Lofi"],
        songs,
        k=5,
        artist_penalty=1.5,
    )


if __name__ == "__main__":
    main()
