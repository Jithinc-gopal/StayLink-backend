import os
from dotenv import load_dotenv
from openai import OpenAI
from rag import search_properties

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)

MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "meta-llama/llama-3.1-8b-instruct:free"
)

SYSTEM_PROMPT = """
You are StayLink Assistant, a helpful AI for the StayLink property booking platform in India.

Help travelers find properties using ONLY the provided StayLink database context.
Be friendly, helpful, and concise.
When suggesting properties, mention name, location, price, amenities, and rating.
If user wants to book, tell them to click the property card.
You cannot make bookings directly.
"""


def run_agent(user_message: str, chat_history: list | None = None):

    if chat_history is None:
        chat_history = []

    print(f"\n🤖 User: {user_message}")

    relevant_docs = search_properties(user_message, k=5)

    if relevant_docs:
        context = "\n\n---\n\n".join(
            [
                f"Property {i}:\n{doc.page_content}"
                for i, doc in enumerate(relevant_docs, 1)
            ]
        )

        context_message = (
            "Use ONLY these StayLink properties while answering:\n\n"
            + context
        )
    else:
        context_message = (
            "No matching properties were found in StayLink database."
        )

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "system",
            "content": context_message,
        },
    ]

    valid_history = [
        msg for msg in chat_history
        if msg.get("role") in ["user", "assistant"]
        and msg.get("content")
    ]

    messages.extend(valid_history[-6:])

    messages.append({
        "role": "user",
        "content": user_message,
    })

    print(f"💬 Calling {MODEL} via OpenRouter...")

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=500,
            temperature=0.5,
            extra_headers={
                "HTTP-Referer": "http://localhost:5173",
                "X-Title": "StayLink AI Assistant",
            },
        )

        if not response:
            return "Sorry, I could not get a response from the AI model."

        if not response.choices:
            return "Sorry, the AI model returned no answer. Please try again."

        message = response.choices[0].message

        if not message or not message.content:
            return "Sorry, the AI response was empty. Please try again."

        reply = message.content.strip()

        print(f"✅ Reply: {reply[:80]}...")

        return reply

    except Exception as e:
        print(f"❌ OpenRouter error: {type(e).__name__}: {e}")

        if relevant_docs:
            fallback = "I found these matching properties:\n\n"

            for i, doc in enumerate(relevant_docs[:3], 1):
                fallback += f"{i}. {doc.metadata.get('title')} - {doc.metadata.get('city')}, {doc.metadata.get('state')} - Rs.{doc.metadata.get('price')}/{doc.metadata.get('price_unit')}\n"

            fallback += "\nPlease click a property card to view details or book."

            return fallback

        return "Sorry, the AI service is temporarily unavailable. Please try again."