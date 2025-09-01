import streamlit as st
import json
import random
from fuzzywuzzy import fuzz
import time

# ---------------- Load JSON files ----------------
@st.cache_data
def load_data():
    with open("mood.json", "r", encoding="utf-8") as f:
        moods = json.load(f)
    with open("responses.json", "r", encoding="utf-8") as f:
        responses = json.load(f)
    with open("triggers.json", "r", encoding="utf-8") as f:
        triggers = json.load(f)
    with open("solutions.json", "r", encoding="utf-8") as f:
        solutions = json.load(f)
    return moods, responses, triggers, solutions

MOODS, RESPONSES, TRIGGERS, SOLUTIONS = load_data()

# ---------------- Constants ----------------
GREETINGS = ["hi", "hello", "hey", "heyy", "hola", "yo", "sup"]
NEGATIONS = ["not", "no", "never", "n't", "dont", "don't", "isn't", "bad", "worse"]
POSITIVE_WORDS = ["good", "happy", "great", "fine", "okay", "alright"]
VALID_MOODS = list(MOODS.keys())

# ---------------- Helper Functions (No changes in this section) ----------------
def detect_mood(user_input: str) -> str:
    user_input = user_input.lower()
    if any(word in user_input.split() for word in GREETINGS):
        return "Greeting"
    if any(neg in user_input for neg in NEGATIONS) and any(pos in user_input for pos in POSITIVE_WORDS):
        return "Sad / Lonely"
    for mood, keywords in MOODS.items():
        for kw in keywords:
            if fuzz.partial_ratio(user_input, kw.lower()) > 85:
                return mood
    return "Unknown"

def detect_trigger(user_input: str) -> tuple:
    user_input = user_input.lower()
    scores = {}
    for category, keywords in TRIGGERS.items():
        scores[category] = 0
        for kw in keywords:
            score = fuzz.partial_ratio(user_input, kw.lower())
            if score > 75:
                scores[category] = max(scores[category], score)
    
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    best_category, best_score = sorted_scores[0]

    if best_score < 70:
        return "General", None

    if len(sorted_scores) > 1:
        second_category, second_score = sorted_scores[1]
        if abs(best_score - second_score) <= 5 and second_score >= 70:
            return best_category, second_category
            
    return best_category, None

def get_solution(mood, intensity, trigger):
    if mood not in SOLUTIONS or intensity not in SOLUTIONS[mood]:
        return "I don’t have specific advice for this, but I’m here to listen 💙", False
    mood_solutions = SOLUTIONS[mood][intensity]
    trigger = trigger.capitalize()
    if trigger not in mood_solutions and "General" in mood_solutions:
        trigger = "General"
    elif trigger not in mood_solutions:
        return "I don’t have specific advice for this, but I’m here to listen 💙", False
    available = [s for s in mood_solutions[trigger] if s not in st.session_state.used_solutions]
    if not available:
        return "I’ve shared everything I had for this. Maybe we can just talk more 💙", False
    suggestion = random.choice(available)
    st.session_state.used_solutions.add(suggestion)
    return suggestion, True

def generate_summary_and_solution():
    mood, intensity, trigger = st.session_state.detected_mood, st.session_state.intensity, st.session_state.user_trigger
    summary = (f"Got it. You're feeling **{mood}** at a **{intensity}** intensity, "
               f"and it seems to be triggered by **{trigger.lower()}**.")
    suggestion, success = get_solution(mood, intensity, trigger)
    if success:
        response = f"{summary}\n\nHere is a suggestion for you:\n\n> {suggestion}\n\nDoes this help at all? (yes/no)"
        st.session_state.stage = "AWAITING_SOLUTION_FEEDBACK"
    else:
        response = f"{summary}\n\nUnfortunately, I don't have a specific suggestion for this right now, but I'm here to listen. 💙"
        st.session_state.stage = "CONVERSATION_END"
    return response

def format_chat_history(messages):
    chat_string = "Your Conversation with Companion Bot\n" + "="*40 + "\n\n"
    for message in messages:
        if message == st.session_state.messages[0]: continue
        role = "You" if message["role"] == "user" else "Bot"
        content = message['content'].replace('**', '')
        chat_string += f"{role}: {content}\n\n"
    return chat_string

# ---------------- Streamlit App UI and Logic ----------------

st.title("Your Companion Bot 🌸")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "I'm here to listen and help you navigate your feelings. What's on your mind?"}]
if "stage" not in st.session_state: st.session_state.stage = "AWAITING_INITIAL_INPUT"
if "detected_mood" not in st.session_state: st.session_state.detected_mood = ""
if "intensity" not in st.session_state: st.session_state.intensity = ""
if "user_trigger" not in st.session_state: st.session_state.user_trigger = ""
if "used_solutions" not in st.session_state: st.session_state.used_solutions = set()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- MODIFIED: Both buttons are now inside this single block ---
# This block runs only when the conversation is flagged as "END"
if st.session_state.stage == "CONVERSATION_END":
    # Use columns to place buttons side-by-side
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Start New Chat"):
            st.session_state.messages = [{"role": "assistant", "content": "Of course. Let's talk. How are you feeling?"}]
            st.session_state.stage = "AWAITING_INITIAL_INPUT"
            st.session_state.detected_mood = ""
            st.session_state.intensity = ""
            st.session_state.user_trigger = ""
            st.session_state.used_solutions = set()
            st.rerun()
    
    with col2:
        chat_text = format_chat_history(st.session_state.messages)
        st.download_button(
            label="📥 Save Chat as Text File",
            data=chat_text,
            file_name="companion_bot_chat.txt",
            mime="text/plain"
        )

# --- REMOVED: The old download button location was removed from here ---

if prompt := st.chat_input("How are you feeling?", disabled=(st.session_state.stage == "CONVERSATION_END")):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Thinking..."):
        time.sleep(random.uniform(0.8, 1.5))
        
        # (The entire stage-based response logic remains the same)
        if st.session_state.stage == "AWAITING_INITIAL_INPUT":
            mood = detect_mood(prompt)
            if mood == "Greeting":
                response = random.choice(["Hey there! 😊 What’s on your mind?", "Hello friend 💙 How’s your day going?"])
                st.session_state.stage = "AWAITING_INITIAL_INPUT"
            elif mood == "Unknown":
                response = random.choice(RESPONSES["Unknown"])
                st.session_state.stage = "AWAITING_INITIAL_INPUT"
            else:
                st.session_state.detected_mood = mood
                response = f"I sense you might be feeling **{mood}**. Is that right? (yes/no)"
                st.session_state.stage = "AWAITING_MOOD_CONFIRMATION"
        
        elif st.session_state.stage == "AWAITING_MOOD_CONFIRMATION":
            if "yes" in prompt.lower():
                response = f"On a scale of 1–10, how **{st.session_state.detected_mood}** do you feel right now?"
                st.session_state.stage = "AWAITING_INTENSITY"
            else:
                response = "Thanks for clarifying 💙 Tell me more about how you’re feeling."
                st.session_state.stage = "AWAITING_INITIAL_INPUT"

        elif st.session_state.stage == "AWAITING_INTENSITY":
            try:
                intensity_val = int(prompt)
                if 1 <= intensity_val <= 10:
                    if intensity_val <= 3: st.session_state.intensity = "Low"
                    elif intensity_val <= 7: st.session_state.intensity = "Medium"
                    else: st.session_state.intensity = "High"
                    response = "What do you think is triggering this? (e.g., work, study, relationships, health)"
                    st.session_state.stage = "AWAITING_TRIGGER"
                else:
                    response = "Please provide a number between 1 and 10."
            except ValueError:
                response = "Please provide a number between 1 and 10."

        elif st.session_state.stage == "AWAITING_TRIGGER":
            trigger1, trigger2 = detect_trigger(prompt)
            if trigger2:
                 st.session_state.user_trigger = (trigger1, trigger2)
                 response = f"It sounds like this could be about **{trigger1}** or **{trigger2}**. Which one fits better?"
                 st.session_state.stage = "AWAITING_TRIGGER_CLARIFICATION"
            else:
                st.session_state.user_trigger = trigger1
                response = generate_summary_and_solution()

        elif st.session_state.stage == "AWAITING_TRIGGER_CLARIFICATION":
            t1, t2 = st.session_state.user_trigger
            if t1.lower() in prompt.lower(): st.session_state.user_trigger = t1
            elif t2.lower() in prompt.lower(): st.session_state.user_trigger = t2
            else: st.session_state.user_trigger = "General"
            response = generate_summary_and_solution()

        elif st.session_state.stage == "AWAITING_SOLUTION_FEEDBACK":
            if "yes" in prompt.lower():
                response = "I'm glad to hear that! Would you like to try another suggestion or end our chat for now? (type 'another' or 'end')"
                st.session_state.stage = "AWAITING_NEXT_STEP"
            else:
                suggestion, success = get_solution(st.session_state.detected_mood, st.session_state.intensity, st.session_state.user_trigger)
                if success:
                    response = f"Okay, let's try something else.\n\n> {suggestion}\n\nHow about this one? Does this help? (yes/no)"
                    st.session_state.stage = "AWAITING_SOLUTION_FEEDBACK"
                else:
                    response = "I’ve shared everything I had for this. We can end here, or just talk more if you like. 💙"
                    st.session_state.stage = "CONVERSATION_END"

        elif st.session_state.stage == "AWAITING_NEXT_STEP":
            if "another" in prompt.lower():
                suggestion, success = get_solution(st.session_state.detected_mood, st.session_state.intensity, st.session_state.user_trigger)
                if success:
                    response = f"Here you go:\n\n> {suggestion}\n\nDoes this help at all? (yes/no)"
                    st.session_state.stage = "AWAITING_SOLUTION_FEEDBACK"
                else:
                    response = "I’m out of new suggestions for this topic. I hope what we’ve discussed was helpful. Take care. 💙"
                    st.session_state.stage = "CONVERSATION_END"
            else:
                response = "Take care! I’ll be here whenever you need me 🌸"
                st.session_state.stage = "CONVERSATION_END"
    
    if 'response' in locals():
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
