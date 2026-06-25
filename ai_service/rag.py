# rag.py — top of file, replace the DJANGO_API_BASE_URL line

import requests
import os
import shutil
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

DJANGO_API_BASE_URL = os.getenv("DJANGO_API_BASE_URL")

# ✅ FIX: use absolute path so it works correctly inside Docker
CHROMA_DB_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")


def get_embeddings():
   
    return HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"}
    )


def fetch_properties_from_django():
    """
    Calls your Django API and fetches all active properties.
    Converts each property into a LangChain Document object.
    """
    print("📡 Fetching properties from Django...")

    try:
        response = requests.get(
            f"{DJANGO_API_BASE_URL}/api/owner/public/properties/",
            timeout=10
        )
    except Exception as e:
        print(f"❌ Cannot reach Django: {e}")
        return []

    if response.status_code != 200:
        print(f"❌ Django API error: {response.status_code}")
        return []

    properties = response.json()
    print(f"✅ Fetched {len(properties)} properties")

    documents = []

    for prop in properties:
        amenities_text = (
            ", ".join(prop["amenities"])
            if prop["amenities"]
            else "No amenities listed"
        )

        rating_text = (
            f"Rated {prop['avg_rating']} out of 5"
            if prop.get("avg_rating")
            else "No ratings yet"
        )

        furnished_text = (
            "Fully furnished"
            if prop.get("is_furnished")
            else "Not furnished"
        )

        # Write a readable paragraph about each property
        # This is what the AI reads when searching
        text = f"""
Property Name: {prop['title']}
Type: {prop['property_type']}
Location: {prop['city']}, {prop['state']}
Address: {prop['address']}
Price: Rs.{prop['price']} per {prop['price_unit']}
Bedrooms: {prop['bedrooms']}
Bathrooms: {prop['bathrooms']}
Maximum Guests: {prop['max_guest']}
Furnishing: {furnished_text}
Ambience: {prop.get('ambience', '')}
Amenities: {amenities_text}
Nearby Facilities: {prop.get('nearby_facilities', '')}
Cancellation Policy: {prop.get('cancellation_policy', '')}
Rules: {prop.get('rules', '')}
Rating: {rating_text}
Description: {prop['description']}
        """.strip()

        doc = Document(
            page_content=text,
            metadata={
                "id": prop["id"],
                "title": prop["title"],
                "city": prop["city"],
                "state": prop["state"],
                "price": prop["price"],
                "price_unit": prop["price_unit"],
                "property_type": prop["property_type"],
                "bedrooms": prop["bedrooms"],
                "avg_rating": prop.get("avg_rating"),
            }
        )
        documents.append(doc)

    return documents


def build_vector_store():
    """
    Builds ChromaDB vector store from your properties.
    Uses FREE local HuggingFace embeddings — no API cost.
    """
    print("🔨 Building vector store...")

    documents = fetch_properties_from_django()

    if not documents:
        print("⚠️ No properties found. Add properties in Django first.")
        return None

    # Use free local embeddings
    embeddings = get_embeddings()

    # Delete old chroma_db if exists to rebuild fresh
    import shutil
    if os.path.exists(CHROMA_DB_PATH):
        shutil.rmtree(CHROMA_DB_PATH)
        print("🗑️ Cleared old index")

    # Build new vector store
    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=CHROMA_DB_PATH
    )

    print(f"✅ Successfully indexed {len(documents)} properties!")
    return vector_store


def load_vector_store():
    """
    Loads existing ChromaDB — fast, no cost.
    Call this for every search instead of rebuilding.
    """
    embeddings = get_embeddings()

    vector_store = Chroma(
        persist_directory=CHROMA_DB_PATH,
        embedding_function=embeddings
    )

    return vector_store


def search_properties(query: str, k: int = 5):
    """
    Searches ChromaDB for properties matching the query.
    Returns top k most relevant property Documents.
    
    Example:
    query = "villa in Kochi with WiFi"
    returns = 5 most similar property Documents
    """
    print(f"🔍 Searching for: {query}")

    vector_store = load_vector_store()
    results = vector_store.similarity_search(query, k=k)

    print(f"📋 Found {len(results)} relevant properties")
    return results