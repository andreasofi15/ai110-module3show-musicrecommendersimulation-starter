# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**VibeMatch 1.0**

---

## 2. Intended Use  

**Goal / Task:** VibeMatch tries to predict which songs from a small catalog a listener will enjoy. The listener gives five preferences: a favorite genre, a favorite mood, a target energy level, whether they like acoustic music, and a target "happiness" (valence). The system gives every song a score out of 5 and returns the top 5 with reasons.

**Intended use:** classroom exploration. It is a simple, readable example of how data turns into recommendations. It assumes the listener can describe their taste with one genre, one mood and a few numbers.

**Not intended for:**

- A real music app or real users. The catalog is tiny and the song numbers are made up.
- Judging how good or popular a song or an artist is.
- Making any decision about a person. It only matches labels and numbers.
- Listeners whose taste is mixed, changing or hard to describe in five settings.

---

## 3. How the Model Works  

Imagine a judge who listens to every song in a small catalog and gives each one a score out of 5 for one listener. The listener tells the judge five things: the genre they like, the mood they want, how energetic they want the music to feel, whether they like acoustic sounds, and how happy or dark they want it to sound.

For each song, the judge adds up points:

- **Genre:** 2 points if the song's genre is exactly the one the listener likes. Otherwise 0.
- **Mood:** 1 point if the song's mood is exactly the one the listener wants. Otherwise 0.
- **Energy:** up to 1 point. A song gets full points if its energy is exactly what the listener wants, and fewer points the further away it is, whether it is too calm or too intense. So the song does not need the *highest* energy, just the *closest*.
- **Acoustic feel:** up to half a point. If the listener likes acoustic music, more acoustic songs earn more. If not, more electronic songs earn more.
- **Happy or dark tone:** up to half a point, again for being close to what the listener wants.

The judge also writes down *why* each song got its points, such as "genre match (+2.00)", so the listener can see the reasons. Once every song has a score, the system sorts them from highest to lowest and shows the top few.

**What changed from the starter code:** the starter had empty placeholders. I added loading songs from the CSV, the scoring rule above (genre and mood bonuses, closeness scoring for the numbers, and a list of reasons), a sorting step that returns the top results, and an optional artist penalty (see Section 6).

---

## 4. Data  

- **Size:** 20 songs in `data/songs.csv`. The starter had 10. I added 10 more to cover genres and moods that were missing.
- **Columns:** id, title, artist, genre, mood, energy, tempo_bpm, valence, danceability, acousticness. The score uses genre, mood, energy, acousticness and valence. Tempo and danceability are stored but not scored.
- **Variety:** 16 genres and 15 moods. Pop and lofi have 3 songs each. The other 14 genres have just 1 song each.
- **Limits:** the 10 added songs are made up, so their numbers are not measured from real music. There is no lyrics data, no language data, no popularity and no listening history. Whole styles of taste are missing, such as K-pop, regional music, or anything tied to a decade.

---

## 5. Strengths  

- **Good when the listener's taste is common in the catalog.** For pop and lofi listeners, the top songs matched my intuition: Sunrise City for Pop and Library Rain for Chill Lofi.
- **"Closest" works better than "highest".** Energy is scored by distance, so a calm listener is not given a loud song just because its number is bigger.
- **Every pick comes with reasons, and the reasons add up exactly.** Three examples in plain words:
  - *Sunrise City (Pop, 4.87):* it is pop (+2.00) and happy (+1.00), its energy is within 0.02 of the target (+0.98), it is not very acoustic (+0.41), and its tone is almost exactly right (+0.48).
  - *Library Rain (Chill Lofi, 4.88):* it is lofi (+2.00) and chill (+1.00), its energy is within 0.05 of the target (+0.95), it is very acoustic (+0.43), and its tone matches exactly (+0.50).
  - *Dusty Porch Anthem (Acoustic + High Energy, 4.85):* it is the only country song (+2.00) and it is nostalgic (+1.00). Its energy is within 0.07 of the target (+0.93), it is very acoustic (+0.42), and its tone is close (+0.49).
- **The code is easy to check.** The scores I predicted by hand in Phase 2 matched the program's output exactly, and the unit tests pass.

---

## 6. Limitations and Bias 

**Main weakness: a rare genre gives one good pick and then a nearly random list.** In my adversarial test (country, nostalgic, high energy, likes acoustic), only one song in the catalog is country, so Dusty Porch Anthem scored 4.85 out of 5 and the next four songs scored between 1.46 and 1.53, a spread of just 0.07 points. Those four are different genres and moods, and one of them (Sunrise City, which is very electronic) is the opposite of what an acoustic fan asked for, so their order is close to a coin flip. This happens because genre and mood are all-or-nothing bonuses worth 3 of the 5 points, so once a listener runs out of songs that match them, the leftover points come from tiny differences in energy, acousticness and tone. Listeners whose taste is common in the catalog (pop and lofi have three songs each) get a smooth, sensible list, while listeners with rarer taste get a cliff.

Other limits I noticed:

- **Labels can beat the numbers.** Smiling in the Rain ranks second for a pop/happy listener even though its tone is gloomy (valence 0.30 vs. a 0.80 target), because the genre and mood bonuses are worth much more than the tone points it loses.
- **Exact matching is strict.** "Pop" earns nothing for "indie pop", and "chill", "relaxed" and "focused" count as completely different moods.
- **Features it ignores:** lyrics, language, tempo, danceability and anything about listening history.
- **Energy scoring helps some listeners more than others (from the math, not tested).** Energy is scored by distance, so a listener who wants mid-level energy (about 0.5) can lose at most about 0.5 points on energy for any song, while a listener who wants 0.95 can lose up to 0.77. Energy therefore separates songs more for extreme-energy listeners.

**Diversity feature (stretch): artist penalty.** When this is turned on, the system picks songs one at a time. If an artist already has a song in the list, each later song from that artist loses 1.5 points (the number can be changed). The reason appears in the explanation, for example "artist repeat penalty (-1.50)".

- **Example:** in the Chill Lofi test, the artist LoRoom had two songs in the top 3. With the penalty, Focus Flow dropped from 3rd to 4th (3.89 to 2.39) and Spacewalk Thoughts by a different artist moved up to 3rd. The full output is in the README.
- **How it helps fairness:** one artist cannot fill the whole list, so other artists get a chance to be heard, and the listener sees more variety. It also helps a little against a "filter bubble" of the same sound.
- **Limits:** only two artists in this catalog (Neon Echo and LoRoom) have more than one song, so the effect here is small. The penalty is off by default, so the other results in this card do not use it. The 1.5 is a guess, not a tuned value.

---

## 7. Evaluation  

**Profiles tested:** High-Energy Pop (pop, happy, energy 0.8, not acoustic), Chill Lofi (lofi, chill, energy 0.4, acoustic), and an adversarial Acoustic + High Energy profile (country, nostalgic, energy 0.85, acoustic). The adversarial one is built around a catalog quirk: loud songs here are almost never acoustic. Full terminal output for all three is in the README.

**What I looked for:** whether the top song felt right, whether the order of songs 2 to 5 made sense, and whether the scores explained the order.

**Does it feel right?** For Pop and Chill Lofi, yes. Sunrise City and Library Rain are the songs I would pick first. Surprises: (1) Smiling in the Rain placed second for Pop even though it sounds gloomy by its numbers; (2) Sunrise City, a very electronic song, showed up in the acoustic fan's top 5; (3) the adversarial profile had a huge drop after the first song (4.85 to 1.53), unlike the other two profiles.

**Why does Gym Hero keep showing up for "Happy Pop" fans?** Gym Hero is a pop song, and the system gives 2 points just for being the right genre. It is also loud like the listener asked for and not acoustic, so it gets 3.83 out of 5 and only misses the "happy" point. Rooftop Lights is actually happy and has nearly the right energy, but its genre is "indie pop", not "pop", so it gets zero genre points and scores only 2.78. In plain terms: the system cares twice as much about the genre name as about the mood, so a workout song that says "pop" beats a happy song that says "indie pop".

**Pair comparisons:**

- **Pop vs. Chill Lofi:** no song appears in both top 5s. Pop picks loud, electronic songs (energy 0.70 to 0.93); Lofi picks quiet, acoustic ones (energy 0.28 to 0.42). That is what the two profiles ask for, so it makes sense.
- **Pop vs. Acoustic + High Energy:** both want high energy, so Rooftop Lights and Sunrise City appear in both top 5s. Pop users see them near the top because of genre and mood matches, but the acoustic user gets them at only about 1.5 points, since only their energy fits. This is the part I find invalid: an acoustic fan was given mostly electronic songs, because the acousticness preference is worth only 0.5 points and cannot outweigh energy.
- **Chill Lofi vs. Acoustic + High Energy:** Lofi's scores fall smoothly (4.88, 4.82, 3.89, 2.81, 1.86), with three lofi songs in a row, then an ambient and a jazz song that feel close. The adversarial list is one strong song and then a flat, unrelated tail. The difference comes from how many songs in the catalog share the listener's genre: three lofi versus one country.

**Experiment: weight shift (genre 2.0 to 1.0, energy 1.0 to 2.0).** The maximum score stayed at 5.0 and every score stayed within 0 to 5. For Pop, Rooftop Lights moved above Gym Hero (3.74 vs. 3.70), which matches my intuition better, but the margin is tiny. For Chill Lofi the order did not change. For the adversarial profile, slots 2 to 5 changed but stayed within 0.06 points of each other. So the change made results somewhat more sensible for pop and otherwise just different.

**Second experiment: artist penalty (see Section 6).** It reordered only the Chill Lofi list, where two LoRoom songs were close together.

**Simple tests:** three unit tests pass (the two starter tests plus one I added to check that the artist penalty separates repeat artists). The scores I predicted by hand in Phase 2 matched the program's output exactly.

---

## 8. Future Work  

1. **Let listeners pick more than one genre or mood, and score genre by similarity.** "Indie pop" should earn most of the points for a "pop" fan, and "relaxed" should be close to "chill". This would fix the Gym Hero and Rooftop Lights problem.
2. **Use a bigger, real catalog.** With only one song in most genres, rare tastes get a one-song list. A bigger catalog would also let me test the artist penalty properly.
3. **Learn from feedback.** Add skips and likes so the system can adjust its weights per listener, like real recommenders do, instead of using weights I picked by hand.

---

## 9. Personal Reflection  

**Biggest learning moment.** It was the Gym Hero result. I started with genre worth +2.0 and mood +1.0 because that looked like a reasonable recipe. It seemed fine until a workout song showed up third for a "happy pop" listener. I thought halving the genre weight would fix it, but the weight-shift experiment only moved Gym Hero below Rooftop Lights by 0.04 points. I learned that weights are not neutral math. They are opinions about what matters, and the ranking is only as good as those opinions.

**How AI helped, and where I had to double-check it.** The AI assistant helped me analyze the data, design the scoring recipe, write the functions, run the profiles and draft the write-ups. It was fastest at turning the recipe into code. I still had to check it in a few places:

- The starter `main.py` imported `from recommender import ...`, which fails when you run `python -m src.main`, so it had to be changed to `from src.recommender import ...`.
- The scores I predicted in Phase 2 matched the program's output exactly, so I trusted the scoring more after that.
- The numbers for the 10 songs I added were written by the AI, not measured from real music. I treat them as test data, not facts.
- Some claims in my write-up are reasoning, not tests (the energy-gap point in Section 6), and I labeled them that way.

**What surprised me.** It surprised me how little it takes to feel like a recommendation. Five numbers and two labels produced lists that mostly felt right for pop and lofi, and the list of reasons made it feel smarter than it is, even though it is only addition. The adversarial profile showed the illusion breaking: one great pick, then four unrelated songs within 0.07 points of each other.

**What I would try next.** I would let listeners choose several genres and moods and score genre by similarity, try a much bigger catalog, and add a feedback signal such as skips so the weights can change per listener. I would also tune the artist penalty on a catalog where more artists have several songs.
