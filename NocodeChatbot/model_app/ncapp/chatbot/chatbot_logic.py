import os

def load_rag_text():
    """
    Load all .txt files from default RAG folder
    """
    path = "ncapp/chatbot/rag_data"
    if not os.path.exists(path):
        return ""

    content = ""
    for file in os.listdir(path):
        if file.endswith(".txt"):
            with open(os.path.join(path, file), "r", encoding="utf-8") as f:
                content += f.read() + "\n\n"
    return content


def build_prompt(user_message, rag_text="", conversation_text="", chatbot_name="Demo Chatbot", chatbot_domain="General"):
    """
    Build a prompt including chatbot info, conversation history, optional RAG text,
    and domain restriction.
    
    The chatbot will ONLY respond to questions related to its domain.
    """
    prompt = f"""
You are an AI chatbot named "{chatbot_name}" specialized in "{chatbot_domain}".
Language: REPLACE_LANGUAGE
Tone: REPLACE_TONE
Instructions: 
- Be helpful, polite, and clear.

- If the user says "hi", "hello", or similar greetings, respond ONLY:
  "👋 Hi! I am {chatbot_name}. How can I help you today?"

- Do NOT say "good morning", "good afternoon", or similar greetings.
- Do NOT say the message lacks information when the user greets.

- If the user asks your name reply ONLY:
  "I am {chatbot_name}."

- ONLY answer knowledge questions related to "{chatbot_domain}".

- If the question is outside your domain respond:
  "Sorry, I can only answer questions about {chatbot_domain}."

- If you don't know the answer say:
  "Sorry, I don't have that information."
"""

    if rag_text:
        # rag_text = rag_text[:2000]
        prompt += f"\nKnowledge Base:\n{rag_text}\n"

    if conversation_text:
        prompt += f"\nConversation History:\n{conversation_text}\n"
        
    prompt += f"\nUser Question:\n{user_message}"

    return prompt.strip()



API_KEY = 'REPLACE_YOUR_API_KEY_HERE'
MODEL_NAME = "REPLACE_MODEL_NAME"