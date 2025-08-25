import json
import random
from fuzzywuzzy import fuzz

# ---------------- Load JSON files ----------------
with open("mood.json", "r", encoding="utf-8") as f:
    MOODS = json.load(f)

with open("responses.json", "r", encoding="utf-8") as f:
    RESPONSES = json.load(f)

with open("triggers.json", "r", encoding="utf-8") as f:
    TRIGGERS = json.load(f)

with open("solutions.json", "r", encoding="utf-8") as f:
    SOLUTIONS = json.load(f)

# ---------------- Greeting handling ----------------
GREETINGS = ["hi", "hello", "hey", "heyy", "hola", "yo", "sup"]

# ---------------- Negation handling ----------------
NEGATIONS = ["not", "no", "never", "n't", "dont", "don't", "isn't", "bad", "worse"]
POSITIVE_WORDS = ["good", "happy", "great", "fine", "okay", "alright"]

# ---------------- Mood detection ----------------
VALID_MOODS = list(MOODS.keys())

def detect_mood(user_input: str) -> str:
    user_input = user_input.lower()
    
    # Greeting check
    if any(word in user_input for word in GREETINGS):
        return "Greeting"

    # Negation handling
    if any(neg in user_input for neg in NEGATIONS) and any(pos in user_input for pos in POSITIVE_WORDS):
        return "Sad / Lonely"

    # Match against mood keywords in mood.json
    for mood, keywords in MOODS.items():
        for kw in keywords:
            if fuzz.partial_ratio(user_input, kw.lower()) > 85:
                return mood

    return "Unknown"

# ---------------- Trigger detection ----------------
def detect_trigger(user_input: str) -> str:
    user_input = user_input.lower()
    scores = {}

    for category, keywords in TRIGGERS.items():
        scores[category] = 0
        for kw in keywords:
            score = fuzz.partial_ratio(user_input, kw.lower())
            if score > 75:  # threshold for good match
                # Keep the highest score for this category
                scores[category] = max(scores[category], score)

    # Find top 2 categories
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    best_category, best_score = sorted_scores[0]

    if best_score < 70:
        return "General"

    # If 2 categories are very close (within 5 points), ask user to clarify
    if len(sorted_scores) > 1:
        second_category, second_score = sorted_scores[1]
        if abs(best_score - second_score) <= 5 and second_score >= 70:
            print(f"Bot: It sounds like this could be about **{best_category}** or **{second_category}**.")
            choice = input("Which one fits better? ").strip().lower()
            if choice in [best_category.lower(), second_category.lower()]:
                return choice.capitalize()

    return best_category


# ---------------- Suggest solutions ----------------
def suggest_solution(mood, intensity, trigger):
    """Suggest solutions with fallback to General if trigger not found."""
    if mood not in SOLUTIONS:
        print("Bot: I don’t have specific advice for this mood, but I’m here to listen 💙")
        return

    if intensity not in SOLUTIONS[mood]:
        print("Bot: I don’t have specific advice for this intensity, but I’m here to listen 💙")
        return

    mood_solutions = SOLUTIONS[mood][intensity]

    # Normalize trigger
    trigger = trigger.capitalize()

    # Fallback to General
    if trigger not in mood_solutions:
        if "General" in mood_solutions:
            trigger = "General"
        else:
            print("Bot: I don’t have specific advice for this, but I’m here to listen 💙")
            return

    used = set()
    while True:
        available = [s for s in mood_solutions[trigger] if s not in used]
        if not available:
            print("Bot: I’ve shared everything I had for this. Maybe we can just talk more 💙")
            break

        suggestion = random.choice(available)
        used.add(suggestion)
        print("Bot:", suggestion)

        feedback = input("Bot: Does this help? (yes/no): ").strip().lower()
        if feedback == "yes":
            better = input("Bot: Glad to hear that! Are you feeling better? (yes/no): ").strip().lower()
            if better == "yes":
                exit_choice = input("Bot: That’s wonderful 💙 Do you want to end our chat here? (yes/no): ").strip().lower()
                if exit_choice == "yes":
                    print("Bot: Take care! I’ll be here whenever you need me 🌸")
                    exit()
                else:
                    print("Bot: Alright, let’s continue 💙 Tell me, how are you feeling now?")
                    break
            else:
                print("Bot: That’s okay, let’s try something else...")
        else:
            print("Bot: Okay, let me suggest something else...")

# ---------------- Main Conversation Loop ----------------
print("Bot: Hi, I’m your companion.")

while True:
    user_input = input("You: ").strip()
    mood = detect_mood(user_input)

    # Greeting
    if mood == "Greeting":
        print("Bot:", random.choice([
            "Hey there! 😊 What’s on your mind?",
            "Hello friend 💙 How’s your day going?",
            "Hi! I’m here to listen — what’s up?"
        ]))
        continue

    # Unknown
    if mood == "Unknown":
        print("Bot:", random.choice(RESPONSES["Unknown"]))
        continue

    # Confirm mood
    print(f"Bot: I sense you might be feeling **{mood}**. Is that right? (yes/no)")
    confirm = input("You: ").strip().lower()
    if confirm != "yes":
        print("Bot: Thanks for clarifying 💙 Tell me more about how you’re feeling.")
        continue

    # Ask intensity
    intensity_val = input(f"Bot: On a scale of 1–10, how {mood} do you feel right now? ")
    try:
        intensity_val = int(intensity_val)
    except ValueError:
        intensity_val = 5
    if intensity_val <= 3:
        intensity = "Low"
    elif intensity_val <= 7:
        intensity = "Medium"
    else:
        intensity = "High"

    # Ask trigger
    print("Bot: What do you think is triggering this? (work, study, relationships, health, etc.)")
    trigger_input = input("You: ").strip()
    user_trigger = detect_trigger(trigger_input)

    print(f"Bot: Got it. You’re feeling {mood} at {intensity} intensity, triggered by {user_trigger.lower()}.")

    # Suggest solution
    suggest_solution(mood, intensity, user_trigger)
