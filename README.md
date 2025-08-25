MindSoothe Console Edition 💙

MindSoothe is a **console-based emotional support companion**.  
It helps users explore their moods, identify triggers, and receive practical, in-the-moment coping strategies in a conversational way.

---

**Features**
- **Greeting handling** – recognizes friendly starts like "hi", "hello", "hey".
- **Mood detection** – maps user input to one of 15 moods using fuzzy matching + Empath + mood.json.
- **Negation handling** – prevents false positives (e.g., "not good" ≠ cheerful).
- **Mood intensity** – asks the user to rate feelings on a scale of 1–10.
- **Trigger detection** – identifies root causes (work, study, relationships, health, etc.) via triggers.json.
- **Solutions engine** – pulls tailored, practical solutions from solutions.json.
- **Feedback loop** – suggests new strategies until user feels satisfied.
- **Supportive responses** – leverages responses.json for empathetic conversation.

---

**Project Structure**
mindsoothe-console/
│── console.py # Main console chatbot
│── mood.json # Mood categories + keywords
│── triggers.json # Trigger categories + keywords
│── responses.json # Conversational responses
│── solutions.json # Mood + intensity + trigger-based solutions



 **How to Run**
1. Clone the repo:
   ```bash
   git clone https://github.com/your-username/mindsoothe-console.git
   cd mindsoothe-console
   
Install requirements:
   ```bash
   pip install fuzzywuzzy empath

Run the console bot:
   ```bash
   python console.py

**Example Conversation**

Bot: Hi, I’m your companion.
You: hey
Bot: Hey there! 😊 What’s on your mind?
You: I feel panicked
Bot: I sense you might be feeling **Anxious / Nervous**. Is that right? (yes/no)
You: yes
Bot: On a scale of 1–10, how Anxious / Nervous do you feel right now?
You: 7
Bot: What do you think is triggering this? (work, study, relationships, health, etc.)
You: exams
Bot: Got it. You’re feeling Anxious / Nervous at Medium intensity, triggered by Study.
Bot: Try this: *“Break your study into a 25-minute focus session, then take a 5-minute pause.”*
Bot: Does this help? (yes/no)


**Notes**
This is not a replacement for therapy, but a supportive conversational tool.

JSON files make the system scalable and customizable — you can add new moods, triggers, and solutions anytime.

**Contributing**
Pull requests are welcome! If you'd like to add new moods, triggers, or coping strategies, just edit the corresponding JSON files and submit a PR.
