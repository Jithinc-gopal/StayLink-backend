import os
import time
from dotenv import load_dotenv
from openai import OpenAI
from rag import search_properties

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)

# openrouter/auto = OpenRouter picks the best available free model automatically
# This is the most reliable option — it never goes 404
# Fallbacks are tried in order if auto also fails
MODELS = [
    "openrouter/auto",                           # auto-picks best free model
    "meta-llama/llama-3.3-70b-instruct:free",    # strong, usually available
    "meta-llama/llama-4-scout:free",             # good fallback
    "qwen/qwen-2.5-7b-instruct:free",            # lightweight, rarely rate-limited
    "mistralai/mistral-small-24b-instruct-2501:free",  # stable fallback
]

SYSTEM_PROMPT = """
You are StayLink Assistant, a helpful AI for the StayLink property booking platform in India.

Help travelers find properties using ONLY the provided StayLink database context.
Be friendly, helpful, and concise.

STRICT RULES:
- ONLY suggest properties that match EXACTLY what the user asked (location AND type).
- If user asks for a villa in Kochi, only show villas in Kochi — not apartments, not other cities.
- If no exact match exists, say clearly: "I couldn't find [type] in [city] in our listings right now."
- Mention: name, location, price, amenities, and rating when suggesting.
- Never invent or guess properties. Only use what is given in the context.
- If user wants to book, say: click the property card to view details and book.
"""


def call_model(model: str, messages: list) -> str | None:
    """Try one model. Returns reply string, or None if it fails."""
    try:
        print(f"💬 Trying: {model}")
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=500,
            temperature=0.5,
            extra_headers={
                "HTTP-Referer": "http://localhost:5173",
                "X-Title": "StayLink AI Assistant",
            },
        )
        if response and response.choices:
            content = response.choices[0].message.content
            if content and content.strip():
                return content.strip()
    except Exception as e:
        err = str(e)
        print(f"❌ {model} failed: {type(e).__name__}: {err[:120]}")

        # If rate limited, wait the suggested time then let next model try
        # Don't retry same model — move to next in list
        if "429" in err and "retry_after_seconds" in err:
            print("⏳ Rate limited — skipping to next model")

    return None


def smart_fallback(user_message: str, relevant_docs: list) -> str:
    """
    Last resort when ALL models fail.
    Filters ChromaDB results by what the user actually asked for.
    """
    if not relevant_docs:
        return "Sorry, I couldn't find any matching properties right now. Please try again in a moment."

    query_lower = user_message.lower()

    # Common property types and cities to check against
    asked_types = [t for t in ["villa", "apartment", "house", "studio", "room", "cottage"]
                   if t in query_lower]
    asked_cities = [c for c in ["kochi", "calicut", "kozhikode", "thrissur",
                                 "trivandrum", "thiruvananthapuram", "bangalore",
                                 "mumbai", "delhi", "goa"]
                    if c in query_lower]

    filtered = []
    for doc in relevant_docs:
        meta = doc.metadata
        city = (meta.get("city") or "").lower()
        prop_type = (meta.get("property_type") or "").lower()

        city_ok = not asked_cities or any(c in city for c in asked_cities)
        type_ok = not asked_types or any(t in prop_type for t in asked_types)

        if city_ok and type_ok:
            filtered.append(doc)

    results = filtered[:3] if filtered else []

    if not results:
        location = asked_cities[0].title() if asked_cities else "that area"
        ptype = asked_types[0] if asked_types else "property"
        return (
            f"I couldn't find a {ptype} in {location} in our current listings. "
            f"Try searching a different location or property type!"
        )

    reply = "Here are the closest matching properties I found:\n\n"
    for i, doc in enumerate(results, 1):
        meta = doc.metadata
        reply += (
            f"{i}. **{meta.get('title')}** — "
            f"{meta.get('city')}, {meta.get('state')} — "
            f"Rs.{meta.get('price')}/{meta.get('price_unit')}\n"
        )
    reply += "\nClick a property card to view full details and book."
    return reply


def run_agent(user_message: str, chat_history: list | None = None):
    if chat_history is None:
        chat_history = []

    print(f"\n🤖 User: {user_message}")

    relevant_docs = search_properties(user_message, k=5)

    if relevant_docs:
        context = "\n\n---\n\n".join(
            [f"Property {i}:\n{doc.page_content}"
             for i, doc in enumerate(relevant_docs, 1)]
        )
        context_message = (
            "Use ONLY these StayLink properties. Only suggest ones that "
            "exactly match the user's location and property type request.\n\n"
            + context
        )
    else:
        context_message = "No matching properties found in StayLink database."

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": context_message},
    ]

    valid_history = [
        msg for msg in chat_history
        if msg.get("role") in ["user", "assistant"] and msg.get("content")
    ]
    messages.extend(valid_history[-6:])
    messages.append({"role": "user", "content": user_message})

    # Try each model in order, stop at first success
    for model in MODELS:
        reply = call_model(model, messages)
        if reply:
            print(f"✅ Success with {model}: {reply[:80]}...")
            return reply

    # All models failed
    print("⚠️ All models failed — using smart fallback")
    return smart_fallback(user_message, relevant_docs)