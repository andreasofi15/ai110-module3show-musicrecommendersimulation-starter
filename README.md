# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

**VibeMatch 1.0** is a content-based music recommender that runs in the terminal. It loads a 20-song catalog from a CSV, scores every song against a listener's taste profile (genre, mood, energy, acoustic preference and tone), and prints the top 5 songs with the reasons behind each score. I tested it with three profiles, ran a weight-shift experiment, and added an optional artist penalty so one artist can't fill the whole list.

---

## How The System Works

### Real-world recommenders vs. this simulation

Real platforms like Spotify and TikTok mostly combine two ideas. **Collaborative filtering** predicts what you'll like from the behavior of other users (likes, skips, replays, playlist adds), so it can surface a song nobody has described to the system. **Content-based filtering** predicts it from the song's own attributes, such as tempo, energy, mood and genre, compared against what you already enjoy. At scale they use millions of users and learned audio features. My version is purely content-based: it has no other users, no listening history and a tiny catalog. It prioritizes **closeness to the user's stated vibe**, meaning the right energy level, the right emotional tone and the right texture (acoustic vs. electronic), with genre and mood labels as strong bonuses.

### Features

**`Song` features** (from `data/songs.csv`):

- Used in scoring: `genre`, `mood`, `energy`, `valence`, `acousticness`
- Stored but not scored: `id`, `title`, `artist`, `tempo_bpm`, `danceability` (tempo mostly duplicates energy, so scoring both would double-count it)

**`UserProfile` features:**

- `favorite_genre` (string, e.g. "pop")
- `favorite_mood` (string, e.g. "happy")
- `target_energy` (float 0.0-1.0)
- `likes_acoustic` (bool)
- `target_valence` (float 0.0-1.0, optional; if it is not set, the valence component is skipped)

In `main.py` the same preferences are passed as a dictionary: `{"genre": ..., "mood": ..., "energy": ..., "likes_acoustic": ..., "valence": ...}`.

### Dataset

The catalog (`data/songs.csv`) was expanded from 10 to **20 songs**. The 10 new songs add genres (country, blues, hip-hop, r&b, metal, edm, classical, reggae, latin) and moods (nostalgic, sad, confident, romantic, angry, euphoric, melancholic, laid-back, festive) that were missing. Four of them were designed as edge cases for Phase 4:

- **Dusty Porch Anthem** (country): high energy *and* high acousticness, so it tests the "high-energy + acoustic" listener.
- **Rainy Window Blues** (blues): low energy but *sad* (valence 0.18), unlike the calm low-energy songs in the starter set.
- **Smiling in the Rain** (pop, happy): the labels say happy but the valence is only 0.30, so it tests whether labels or numbers win.
- **Iron Cathedral** (metal): extreme energy with very low valence.

### Main taste profile

```python
user_prefs = {
    "genre": "pop",
    "mood": "happy",
    "energy": 0.8,
    "likes_acoustic": False,
    "valence": 0.8,
}
```

**Critique:** this profile can separate "intense rock" from "chill lofi" because every field pulls in a different direction (Storm Runner: wrong genre, wrong mood, energy gap 0.11; Library Rain: wrong genre, wrong mood, energy gap 0.45, and very acoustic). It is narrow in two ways: it names only one genre and one mood, so a listener who likes "pop *or* indie pop" cannot say so, and "indie pop" gets no genre credit at all.

**Predicted top results** (by hand, using the recipe below): Sunrise City 4.87, Smiling in the Rain 4.50, Gym Hero 3.83, Rooftop Lights 2.78. I expect Gym Hero to rank above Rooftop Lights only because of the exact-match genre bonus, even though its mood is wrong.

### Algorithm Recipe

**Scoring Rule** (judges one song). Each song gets points from five components, for a maximum of **5.0**:

| Component | Rule | Max points |
|---|---|---|
| Genre | +2.0 if `song.genre == favorite_genre`, else 0 | 2.0 |
| Mood | +1.0 if `song.mood == favorite_mood`, else 0 | 1.0 |
| Energy | `1.0 x (1 - abs(song.energy - target_energy))` | 1.0 |
| Acousticness | if `likes_acoustic`: `0.5 x acousticness`, else `0.5 x (1 - acousticness)` | 0.5 |
| Valence | `0.5 x (1 - abs(song.valence - target_valence))` | 0.5 |

`score_song` returns `(score, reasons)`, where `reasons` is a list such as `"genre match (+2.0)"`, `"energy close to target (+0.96)"`, so every recommendation can be explained.

**Why closeness instead of "higher is better":** a user who wants energy 0.4 should not be handed a 0.93 workout track just because its number is bigger. Using `1 - |gap|` gives full credit for a perfect match and loses credit steadily as the song moves away in either direction.

**Why genre (+2.0) outweighs mood (+1.0):** genre is the stronger, more stable signal of taste (a metal fan rarely wants jazz), while mood shifts with the moment. This is a deliberate choice that I will test in Phase 4.

**Ranking Rule** (orders the whole catalog). Run `score_song` on every song, sort by score from highest to lowest, and return the top `k`.

**Why both rules are needed:** the scoring rule answers "how good is *this* song for *this* user?" on its own, with no knowledge of other songs. The ranking rule answers "which songs should I show?" by comparing all of those scores. Scoring alone gives 10 unrelated numbers. Ranking alone has nothing to rank by. Keeping them separate also lets me change the weights without touching the sorting code.

### Data flow

```
Input (user prefs)  ->  Process (loop over every song in songs.csv, call score_song)  ->  Output (sort by score, return top k with reasons)
```

### Expected biases

- **Genre dominance:** with +2.0 for genre, a song with the right genre but the wrong mood (for example, Gym Hero for a "pop / happy" user) can outrank songs that match the mood and energy better.
- **Exact-match labels:** "pop" does not match "indie pop", and "chill", "relaxed" and "focused" count as different moods even though they feel similar.
- **Tiny, uneven catalog:** lofi is 3 of 10 songs, so lofi-leaning users get more choice than anyone else.
- **Energy and acousticness are inversely related** in this data, so a "high energy + acoustic" user has no truly good match.
- **No history or other users:** the system can't learn from skips or discover surprising songs, so it can create a filter bubble around the stated profile.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows
   ```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Output of `python -m src.main` for the default "High-Energy Pop" profile (20-song catalog). It matches the hand-calculated predictions from Phase 2 exactly.

```
Loaded songs: 20

============================================================
Profile: High-Energy Pop
Preferences: {'genre': 'pop', 'mood': 'happy', 'energy': 0.8, 'likes_acoustic': False, 'valence': 0.8}
============================================================
1. Sunrise City by Neon Echo  [pop / happy]
   Score: 4.87 / 5.00
   - genre match (+2.00)
   - mood match (+1.00)
   - energy 0.82 vs target 0.80 (+0.98)
   - non-acoustic fit, acousticness 0.18 (+0.41)
   - valence 0.84 vs target 0.80 (+0.48)

2. Smiling in the Rain by Pale Harbor  [pop / happy]
   Score: 4.50 / 5.00
   - genre match (+2.00)
   - mood match (+1.00)
   - energy 0.70 vs target 0.80 (+0.90)
   - non-acoustic fit, acousticness 0.30 (+0.35)
   - valence 0.30 vs target 0.80 (+0.25)

3. Gym Hero by Max Pulse  [pop / intense]
   Score: 3.83 / 5.00
   - genre match (+2.00)
   - energy 0.93 vs target 0.80 (+0.87)
   - non-acoustic fit, acousticness 0.05 (+0.47)
   - valence 0.77 vs target 0.80 (+0.48)

4. Rooftop Lights by Indigo Parade  [indie pop / happy]
   Score: 2.78 / 5.00
   - mood match (+1.00)
   - energy 0.76 vs target 0.80 (+0.96)
   - non-acoustic fit, acousticness 0.35 (+0.33)
   - valence 0.81 vs target 0.80 (+0.49)

5. Concrete Crown by Verse Kingdom  [hip-hop / confident]
   Score: 1.87 / 5.00
   - energy 0.80 vs target 0.80 (+1.00)
   - non-acoustic fit, acousticness 0.08 (+0.46)
   - valence 0.62 vs target 0.80 (+0.41)
```

Gym Hero lands third even though its mood is "intense", not "happy": the +2.00 genre bonus alone puts it ahead of Rooftop Lights, which matches the mood and energy better.

---

## Stress Test: Other Profiles

The High-Energy Pop output is shown above. Terminal output for the other two profiles (top 5 each):

**Chill Lofi** (`genre=lofi, mood=chill, energy=0.4, likes_acoustic=True, valence=0.6`)

```
1. Library Rain by Paper Lanterns  [lofi / chill]
   Score: 4.88 / 5.00
   - genre match (+2.00)
   - mood match (+1.00)
   - energy 0.35 vs target 0.40 (+0.95)
   - acoustic fit, acousticness 0.86 (+0.43)
   - valence 0.60 vs target 0.60 (+0.50)

2. Midnight Coding by LoRoom  [lofi / chill]
   Score: 4.82 / 5.00
   - genre match (+2.00)
   - mood match (+1.00)
   - energy 0.42 vs target 0.40 (+0.98)
   - acoustic fit, acousticness 0.71 (+0.35)
   - valence 0.56 vs target 0.60 (+0.48)

3. Focus Flow by LoRoom  [lofi / focused]
   Score: 3.89 / 5.00
   - genre match (+2.00)
   - energy 0.40 vs target 0.40 (+1.00)
   - acoustic fit, acousticness 0.78 (+0.39)
   - valence 0.59 vs target 0.60 (+0.49)

4. Spacewalk Thoughts by Orbit Bloom  [ambient / chill]
   Score: 2.81 / 5.00
   - mood match (+1.00)
   - energy 0.28 vs target 0.40 (+0.88)
   - acoustic fit, acousticness 0.92 (+0.46)
   - valence 0.65 vs target 0.60 (+0.47)

5. Coffee Shop Stories by Slow Stereo  [jazz / relaxed]
   Score: 1.86 / 5.00
   - energy 0.37 vs target 0.40 (+0.97)
   - acoustic fit, acousticness 0.89 (+0.45)
   - valence 0.71 vs target 0.60 (+0.45)
```

**Acoustic + High Energy, adversarial** (`genre=country, mood=nostalgic, energy=0.85, likes_acoustic=True, valence=0.7`)

```
1. Dusty Porch Anthem by Hollow Creek  [country / nostalgic]
   Score: 4.85 / 5.00
   - genre match (+2.00)
   - mood match (+1.00)
   - energy 0.78 vs target 0.85 (+0.93)
   - acoustic fit, acousticness 0.85 (+0.42)
   - valence 0.72 vs target 0.70 (+0.49)

2. Rooftop Lights by Indigo Parade  [indie pop / happy]
   Score: 1.53 / 5.00
   - energy 0.76 vs target 0.85 (+0.91)
   - acoustic fit, acousticness 0.35 (+0.17)
   - valence 0.81 vs target 0.70 (+0.44)

3. Fiesta Sin Fin by Luna Roja  [latin / festive]
   Score: 1.49 / 5.00
   - energy 0.88 vs target 0.85 (+0.97)
   - acoustic fit, acousticness 0.25 (+0.12)
   - valence 0.90 vs target 0.70 (+0.40)

4. Sunrise City by Neon Echo  [pop / happy]
   Score: 1.49 / 5.00
   - energy 0.82 vs target 0.85 (+0.97)
   - acoustic fit, acousticness 0.18 (+0.09)
   - valence 0.84 vs target 0.70 (+0.43)

5. Coffee Shop Stories by Slow Stereo  [jazz / relaxed]
   Score: 1.46 / 5.00
   - energy 0.37 vs target 0.85 (+0.52)
   - acoustic fit, acousticness 0.89 (+0.45)
   - valence 0.71 vs target 0.70 (+0.49)
```

---

## Experiments You Tried

**Weight shift: genre 2.0 to 1.0, energy 1.0 to 2.0.** The maximum score stays at 5.0 (1.0 + 1.0 + 2.0 + 0.5 + 0.5), and I checked that every score for every song and profile stayed between 0 and 5.0 (observed range 0.99 to 4.85). I ran this by temporarily overriding the weight constants in a scratch script, so `recommender.py` still has the original weights.

| Profile | Baseline top 5 | After weight shift |
|---|---|---|
| High-Energy Pop | Sunrise City 4.87, Smiling in the Rain 4.50, **Gym Hero 3.83**, **Rooftop Lights 2.78**, Concrete Crown 1.87 | Sunrise City 4.85, Smiling in the Rain 4.40, **Rooftop Lights 3.74**, **Gym Hero 3.70**, Concrete Crown 2.87 |
| Chill Lofi | Library Rain, Midnight Coding, Focus Flow, Spacewalk Thoughts, Coffee Shop Stories | Same order; scores for ranks 4 and 5 rise (2.81 to 3.69, 1.86 to 2.83) |
| Acoustic + High Energy | Dusty Porch Anthem 4.85, then Rooftop Lights 1.53, Fiesta Sin Fin 1.49, Sunrise City 1.49, Coffee Shop Stories 1.46 | Dusty Porch Anthem 4.78, then Fiesta Sin Fin 2.46, Sunrise City 2.46, Rooftop Lights 2.44, Concrete Crown 2.40 |

**Result:** the change made the pop list slightly *more* accurate (Rooftop Lights, which has the right mood and nearly the right energy, now beats Gym Hero) but only by 0.04 points, so it is barely a real shift. For the adversarial profile it was just *different*: Coffee Shop Stories, whose energy is 0.48 away from the target, dropped out, but slots 2 to 5 are still separated by only 0.06 points, so their order is close to arbitrary.

---

## Stretch: Diversity (Artist Penalty)

`recommend_songs(..., artist_penalty=1.5)` picks songs one at a time and subtracts 1.5 points for each song by an artist that is already in the list. It is off by default (`artist_penalty=0`), so every other output in this README is unchanged. Here is the Chill Lofi profile with the penalty on. In the normal run, LoRoom has two songs in the top 3 (Midnight Coding and Focus Flow). With the penalty, Focus Flow drops to 4th and Spacewalk Thoughts moves up to 3rd. More detail on how this helps fairness is in [model_card.md](model_card.md).

```
1. Library Rain by Paper Lanterns  [lofi / chill]
   Score: 4.88 / 5.00

2. Midnight Coding by LoRoom  [lofi / chill]
   Score: 4.82 / 5.00

3. Spacewalk Thoughts by Orbit Bloom  [ambient / chill]
   Score: 2.81 / 5.00

4. Focus Flow by LoRoom  [lofi / focused]
   Score: 2.39 / 5.00
   - genre match (+2.00)
   - energy 0.40 vs target 0.40 (+1.00)
   - acoustic fit, acousticness 0.78 (+0.39)
   - valence 0.59 vs target 0.60 (+0.49)
   - artist repeat penalty (-1.50)

5. Coffee Shop Stories by Slow Stereo  [jazz / relaxed]
   Score: 1.86 / 5.00
```

(Reasons for songs 1, 2, 3 and 5 are the same as in the normal run and are left out here for length. Run `python -m src.main` to see everything.)

---

## Limitations and Risks

- **Tiny catalog:** with 20 songs, a listener whose genre has one song gets one strong match and then four near-tied weak ones.
- **Exact-match labels:** "pop" does not match "indie pop", and "chill", "relaxed" and "focused" count as different moods.
- **Labels beat numbers:** Smiling in the Rain ranks second for a pop/happy listener even though its valence (0.30) is far from the 0.80 target.
- **No lyrics, language or listening history:** the system only sees the numbers and labels in the CSV.

More detail is in [model_card.md](model_card.md).

---

## Reflection

The full model card, including my personal reflection, is here: [**Model Card**](model_card.md)

**How data becomes predictions.** My recommender turns each song into five numbers and two labels, compares them with the listener's preferences, and adds up points. Everything it "knows" comes from that scoring recipe, so the recipe's weights decide the results. Genre was worth twice as much as mood, which is why a workout song (Gym Hero) can rank above a happy song (Rooftop Lights) for a "happy pop" listener.

**Where bias shows up.** The system works best for listeners whose taste is common in the catalog. Someone who likes a genre with only one song gets one good pick and then a flat list of unrelated songs. Exact-match labels, a tiny catalog and made-up data also tilt the results, and the artist penalty only partly helps. Real systems have the same problems at a much larger scale.
