import csv
from dataclasses import asdict, dataclass
from typing import Dict, List, Optional, Tuple

# Algorithm Recipe weights (see README "How The System Works")
GENRE_WEIGHT = 2.0
MOOD_WEIGHT = 1.0
ENERGY_WEIGHT = 1.0
ACOUSTIC_WEIGHT = 0.5
VALENCE_WEIGHT = 0.5


@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    target_valence: Optional[float] = None


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top k Song objects for this user, best match first."""
        prefs = _profile_to_prefs(user)
        ranked = sorted(self.songs, key=lambda s: score_song(prefs, asdict(s))[0], reverse=True)
        return ranked[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Explain in one line why this song scored the way it did for this user."""
        _, reasons = score_song(_profile_to_prefs(user), asdict(song))
        return "; ".join(reasons) if reasons else "no matching features"


def _profile_to_prefs(user: UserProfile) -> Dict:
    """Convert a UserProfile into the preference dictionary that score_song expects."""
    return {
        "genre": user.favorite_genre,
        "mood": user.favorite_mood,
        "energy": user.target_energy,
        "likes_acoustic": user.likes_acoustic,
        "valence": user.target_valence,
    }


def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    int_fields = ("id",)
    float_fields = ("energy", "tempo_bpm", "valence", "danceability", "acousticness")
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            for field in int_fields:
                row[field] = int(row[field])
            for field in float_fields:
                row[field] = float(row[field])
            songs.append(row)
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py
    Returns (score, reasons); max score is 5.0 when every preference is provided.
    """
    score = 0.0
    reasons: List[str] = []

    if song["genre"] == user_prefs.get("genre"):
        score += GENRE_WEIGHT
        reasons.append(f"genre match (+{GENRE_WEIGHT:.2f})")

    if song["mood"] == user_prefs.get("mood"):
        score += MOOD_WEIGHT
        reasons.append(f"mood match (+{MOOD_WEIGHT:.2f})")

    target_energy = user_prefs.get("energy")
    if target_energy is not None:
        points = ENERGY_WEIGHT * (1 - abs(song["energy"] - target_energy))
        score += points
        reasons.append(f"energy {song['energy']:.2f} vs target {target_energy:.2f} (+{points:.2f})")

    likes_acoustic = user_prefs.get("likes_acoustic")
    if likes_acoustic is not None:
        fit = song["acousticness"] if likes_acoustic else 1 - song["acousticness"]
        points = ACOUSTIC_WEIGHT * fit
        score += points
        label = "acoustic" if likes_acoustic else "non-acoustic"
        reasons.append(f"{label} fit, acousticness {song['acousticness']:.2f} (+{points:.2f})")

    target_valence = user_prefs.get("valence")
    if target_valence is not None:
        points = VALENCE_WEIGHT * (1 - abs(song["valence"] - target_valence))
        score += points
        reasons.append(f"valence {song['valence']:.2f} vs target {target_valence:.2f} (+{points:.2f})")

    return score, reasons


def recommend_songs(
    user_prefs: Dict, songs: List[Dict], k: int = 5, artist_penalty: float = 0.0
) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    Scores every song, sorts highest first, and returns the top k as (song, score, explanation).
    If artist_penalty > 0, each repeat of an already-picked artist loses that many points (diversity).
    """
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored.append((song, score, reasons))

    if artist_penalty <= 0:
        # sorted() returns a new list and leaves `songs` untouched; ties keep CSV order (stable sort)
        ranked = sorted(scored, key=lambda item: item[1], reverse=True)[:k]
        return [(song, score, "; ".join(reasons)) for song, score, reasons in ranked]

    # Diversity mode: pick one song at a time, charging a penalty for each earlier pick by the same artist
    remaining = list(scored)
    artist_counts: Dict[str, int] = {}
    picked: List[Tuple[Dict, float, str]] = []
    while remaining and len(picked) < k:
        def adjusted(item):
            return item[1] - artist_penalty * artist_counts.get(item[0]["artist"], 0)

        best = max(remaining, key=adjusted)  # ties keep CSV order
        remaining.remove(best)
        song, _, reasons = best
        repeats = artist_counts.get(song["artist"], 0)
        reasons = list(reasons)
        if repeats:
            reasons.append(f"artist repeat penalty (-{artist_penalty * repeats:.2f})")
        picked.append((song, adjusted(best), "; ".join(reasons)))
        artist_counts[song["artist"]] = repeats + 1
    return picked
