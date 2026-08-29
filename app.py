import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from groq import Groq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Load environment ──────────────────────────────────────────────────────────
load_dotenv()
api_key = os.getenv('ARON_API_KEY')
if not api_key:
    raise RuntimeError("Missing 'ARON_API_KEY' in .env")
client = Groq(api_key=api_key)

# ── Rate Limiter ──────────────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address)

# ── Create FastAPI app ────────────────────────────────────────────────────────
app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"reply": "Too many messages! Please wait a moment."}
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["ngrok-skip-browser-warning"] = "true"
    return response

# ── Serve static files ────────────────────────────────────────────────────────
app.mount("/assets", StaticFiles(directory="assets"), name="assets")
if os.path.exists("components"):
    app.mount("/components", StaticFiles(directory="components"), name="components")

# ── ARON Knowledge Base ───────────────────────────────────────────────────────
# NOTE: Add Rehan's proprietary recipes and methods here for ARON Premium content.
ARON_KNOWLEDGE = """
ARON — ASIAN RESTAURANT OWNERS NETWORK

=== OVERALL VISION ===
ARON is a professional, modern and confident platform that helps
hospitality businesses grow, improve and become more profitable.
Working with ARON or Rehan means taking your business to the next level.
Professional. Modern. Confident. Welcoming.

=== ABOUT REHAN ===
Rehan Uddin is a hospitality business consultant with deep expertise in
restaurant operations, kitchen systems, leadership and profitability.
He works with individual restaurants and multi-site hospitality groups
to improve their systems, teams and bottom line.
He is also a Rational UK Ambassador.
His focus is always the same: Better systems. Better teams. Better profit.
Contact: info@rehanuddin.com
Phone: +44 7795 161230

=== CONSULTANCY ===
Service: Building Better Hospitality Businesses
Rehan helps hospitality businesses become more profitable by improving
their systems, kitchens, leadership and operations.
Whether it is one restaurant or a multi-site group, the focus is always:
Better systems. Better teams. Better profit.
CTA: Work With Me — contact page
Email: info@rehanuddin.com

=== ARON COMMUNITY ===
Full name: Asian Restaurant Owners Network
A community bringing together restaurant owners to share knowledge,
solve problems and improve hospitality businesses.
Members get access to shared knowledge, peer support, and resources
to help grow and improve their restaurants.
Facebook group: 2,900+ members (2.9k members)
CTA: Learn More — aron page

=== ARON INSIGHT ===
Tagline: Better Questions. Better Businesses.
A podcast with conversations that challenge hospitality thinking and
help restaurant owners build stronger, more profitable businesses.
Topics: operations, leadership, profitability, systems, kitchen
efficiency, food safety, restaurant management.
CTA: Watch ARON Insight — insight page

=== ARON ENERGY ===
Tagline: Smarter Energy for Hospitality
ARON Energy connects hospitality businesses with specialist utility
support through Consultiv Utilities.
External link: https://consultivutilities.com/
How it works:
1. Complete a short form
2. Receive a free, no-obligation energy review
3. Review based on your business, energy usage and contract
4. Where suitable, benefit from collective purchasing opportunities
CTA: Get My Free Quote — https://consultivutilities.com/

=== LIVE DEMONSTRATIONS ===
EVENT: Luton — Live Kitchen Demonstration

Location:
RATIONAL HQ, Luton, UK

Date:
16 September 2025

Time:
10:30–12:30 OR 14:30–16:30

Event Type:
Live Kitchen Demonstration

Description:
A live demonstration for chefs, restaurateurs and caterers focused on producing high volumes of authentic Asian food without compromising quality, flavour or consistency.

Technology:
RATIONAL cooking systems

Featured Dishes:
- Chicken Curry
- Paneer Karahi
- Tandoori Wings
- Hyderabadi Lamb Chops
- Peas Pilau
- Moong Dal

Key Topics:
- Kitchen efficiency
- Consistency
- Labour reduction
- High-volume Asian food production
- Modern cooking systems
- RATIONAL technology

Event Link:
[your Luton event/details link]

EVENT: Wolverhampton — Asian Expert Chef Session

Location:
Wolverhampton, UK

Date:
2025

Event Type:
Asian Expert Chef / Live Kitchen Demonstration

Description:
A live Asian Expert Chef session demonstrating how RATIONAL iVario Pro and iCombi Pro can modernise Asian kitchen operations while maintaining authenticity, flavour and presentation.

Technology:
- RATIONAL iVario Pro
- RATIONAL iCombi Pro
- Bespoke cooking settings for Asian kitchens

Featured Dishes:
- Chicken Tikka
- Paneer Tikka
- Salmon Tikka
- Lamb Chops
- Sheekh Kebab
- Peas Pilau
- Bone-in Chicken Curry
- Moong Dal
- Paneer Karahi
- Fresh Naan

Key Topics:
- Improved moisture and yield
- Better colouration and finishing
- Reduced labour dependency
- Faster service
- Improved consistency
- Scalable Asian cooking systems

Highlights:
The latest bespoke tikka settings produced strong results during the demonstration and generated significant interest from attending operators.
PREVIOUS ARON LIVE KITCHEN DEMONSTRATIONS

ARON has previously hosted live kitchen demonstrations and Asian Expert Chef sessions across the UK, helping restaurant owners, chefs and hospitality operators explore modern cooking systems, improve kitchen efficiency and maintain authentic Asian flavours.

1. WOLVERHAMPTON — ASIAN EXPERT CHEF SESSION

Location:
Wolverhampton, UK

Year:
2025

Technology:
- RATIONAL iVario Pro
- RATIONAL iCombi Pro

Description:
A high-energy Asian Expert Chef session focused on modernising Asian kitchen operations without compromising authenticity, flavour or presentation. Operators saw how intelligent cooking systems, bespoke presets and production workflows can improve consistency, moisture retention, colour development, yield and overall efficiency.

Featured dishes included:
- Chicken Tikka
- Paneer Tikka
- Salmon Tikka
- Lamb Chops
- Sheekh Kebab
- Peas Pilau
- Bone-in Chicken Curry
- Moong Dal
- Paneer Karahi
- Fresh Naan

Key takeaways:
- Improved product moisture and yield
- Stronger colouration and finishing
- Reduced labour dependency
- Faster and more consistent service
- Scalable cooking methods for Asian kitchens

The latest bespoke tikka settings produced exceptional results and generated strong interest from attending operators.


2. SALFORD / MANCHESTER — iVario Pro LIVE

Location:
CorpAcq Stadium, Salford, Manchester, UK

Date:
9 June 2025

Time:
10:30–12:30 and 14:00–16:00

Technology:
RATIONAL iVario Pro

Description:
An exclusive live cooking experience demonstrating how the RATIONAL iVario Pro can transform Indian and Asian cooking by delivering improved speed, consistency and efficiency in high-volume kitchen environments.

Menu highlights:
- Chicken Curry
- Paneer Karahi
- Hyderabadi Lamb Chops
- Additional dishes demonstrated during the event

The demonstration showed how modern cooking technology can support high-volume Asian food production while maintaining flavour, quality and consistency.


3. LUTON — LIVE KITCHEN DEMONSTRATION

Location:
RATIONAL HQ, Luton, UK

Date:
16 September 2025

Time:
10:30–12:30 or 14:30–16:30

Technology:
RATIONAL cooking systems

Description:
A live demonstration designed for chefs, restaurateurs and caterers looking to produce high volumes of authentic Asian food without compromising on quality, flavour or consistency.

Featured dishes:
- Chicken Curry
- Paneer Karahi
- Tandoori Wings
- Hyderabadi Lamb Chops
- Peas Pilau
- Moong Dal

The event demonstrated how leading operators can use RATIONAL cooking technology to increase efficiency, improve consistency and maximise kitchen performance.


GENERAL PREVIOUS EVENT INFORMATION:

ARON's live demonstrations focus on:
- Modernising Asian kitchen operations
- Improving food consistency
- Reducing labour dependency
- Improving yield and moisture retention
- Increasing kitchen speed and efficiency
- Supporting high-volume production
- Using intelligent cooking systems and bespoke presets
- Maintaining authentic Asian flavour and presentation

The demonstrations are aimed at:
- Restaurant owners
- Chefs
- Caterers
- Asian hospitality operators
- Commercial kitchen professionals
=== TRUSTED PARTNERS ===
1. Goldstar Chefs
   Specialist recruitment for hospitality businesses.
   Looking for chefs or kitchen staff — Goldstar Chefs can help.

2. Euro Foods
   Specialist food supplier for Asian and hospitality businesses.
   Need food supplies, ingredients or catering products — Euro Foods.

3. Rational
   World-leading manufacturer of cooking systems for professional kitchens.
   Rehan is a Rational UK Ambassador.
   Need modern kitchen equipment — Rational is the trusted choice.
   Live demonstrations available to see iCombi and iVario in action.

4. Consultiv Utilities
   Specialist utility broker for hospitality businesses.
   Helps businesses save money on energy through expert advice
   and collective purchasing.
   Website: https://consultivutilities.com/

=== UK FOOD SAFETY & HYGIENE ===
EHO (Environmental Health Officer) Preparation:
- Ensure food storage temperatures correct (0-8C fridge, -18C freezer)
- Maintain cleaning schedules and records
- Keep staff allergen training up to date
- Have pest control records available
- Ensure food handlers have food hygiene certificates

HACCP (Hazard Analysis Critical Control Points):
- Identify food safety hazards at each stage of food preparation
- Set critical control points (CCPs)
- Monitor temperatures at CCPs
- Keep accurate HACCP records
- Review HACCP plan regularly

Food Hygiene Ratings:
- UK businesses rated 0-5 by local authority
- Rating 5 = Very Good (target for all businesses)
- Regular EHO inspections check hygiene, structure and management

Allergen Management:
- 14 major allergens must be declared
- Staff must be trained on allergen awareness
- Written allergen information must be available

=== RESTAURANT SYSTEMS ===
Key systems for profitable restaurants:
- Stock management and ordering systems
- Kitchen display systems (KDS)
- POS (Point of Sale) systems
- Reservation and booking systems
- Staff scheduling and rota systems
- Food waste tracking systems
- Recipe costing and menu engineering

=== PROFIT IMPROVEMENT ===
Profit usually hides in four places:
- Menu engineering and dish costing
- Food cost control and waste reduction
- Labour scheduling and efficiency
- Kitchen systems and consistency
Rehan maps top-selling dishes against true plate cost, then fixes
the systems that keep GP stable when the kitchen is busy.

=== CULINARY INSPIRATION ===
For culinary questions, the assistant provides ONLY short 2-4 line high-level operational guidance.
STRICT RULE: Never list ingredients, measurements, or step-by-step cooking instructions in chat.
Always direct users to contact Rehan for full recipe standardisation, dish costing, and proprietary methods.
Always frame culinary advice in the context of running a profitable hospitality business.

=== CONTACT ===
Website enquiry form available on the Contact page.
AI chatbot available 24/7 for questions and enquiries.
Rehan replies personally to all enquiries.
Email: info@rehanuddin.com
Phone: +44 7795 161230
"""

# ── Build RAG Vector Store ────────────────────────────────────────────────────
print("Building ARON knowledge base...")
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.create_documents([ARON_KNOWLEDGE])
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vector_store = FAISS.from_documents(chunks, embeddings)
retriever = vector_store.as_retriever(search_kwargs={"k": 4})
print("ARON knowledge base ready!")

# ── System Prompt (Strict UK English + Hybrid Knowledge Logic) ────────────────
SYSTEM_PROMPT = """You are an AI assistant for ARON — Asian Restaurant Owners Network.
You represent Rehan Uddin and ARON professionally on their website.
You MUST use strict UK English spelling and vocabulary throughout ALL responses.
UK English examples: optimise, specialise, organisation, colour, flavour, labour,
centre, programme, behaviour, recognise, prioritise, maximise, analyse.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HYBRID KNOWLEDGE LOGIC — FOLLOW IN ORDER:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PRIORITY 1 — PRIVATE DATABASE (Always check FIRST):
- Search the provided CONTEXT (ARON Knowledge Base) for the answer.
- If the answer exists in CONTEXT → answer ONLY from the context.
- If the answer is a proprietary recipe or method from context → label it as:
  "🏆 ARON Premium Recipe" at the start of your response.
- Never mix general knowledge with context-based answers.

PRIORITY 2 — GENERAL CULINARY INSPIRATION (Only if NOT in context):
- If the user asks for a recipe or culinary guidance AND it is NOT in CONTEXT:
- Start with: "💡 General culinary inspiration — contact us for Rehan's proprietary recipes."
- STRICT LIMIT: 2 to 4 lines maximum. Conversational tone.
- ABSOLUTELY NO INGREDIENT LISTS (e.g. 1 kg chicken, 2 onions, 1 tsp cumin).
- ABSOLUTELY NO STEP-BY-STEP COOKING INSTRUCTIONS (e.g. 1. Heat oil, 2. Add garlic).
- Give ONLY a brief operational overview, then ask if they want Rehan's full recipe standardisation.
- Example format:
  "A classic chicken curry works well in high-volume kitchens when you
  standardise your spice blend and batch-cook the base sauce. Want Rehan's
  full approach to recipe standardisation?
  📞 +44 7795 161230
  ✉ info@rehanuddin.com"

PRIORITY 3 — CANNOT ANSWER:
- If the question is completely outside ARON's scope and not culinary →
  reply: "Please contact us directly:
  📞 +44 7795 161230
  ✉ info@rehanuddin.com"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LANGUAGE RULES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Detect the user's language automatically from their message.
- Always reply in the SAME language the user writes in.
- Supported languages:
  * English   → reply in strict UK English
  * Urdu      → reply in proper Urdu script (اردو)
  * Hindi     → reply in proper Hindi script (हिंदी)
  * Bengali   → reply in proper Bengali script (বাংলা)
  * Arabic    → reply in proper Arabic script (العربية)
  * French    → reply in proper French (Français)
  * German    → reply in proper German (Deutsch)
  * Spanish   → reply in proper Spanish (Español)
- Never mix languages in one reply.
- If language is unclear → default to UK English.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BEHAVIOUR RULES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Professional, confident, welcoming and helpful.
- Keep answers concise and clear.
- For consultancy enquiries → encourage visiting the contact page.
- For chef needs → introduce Goldstar Chefs.
- For food supplies → introduce Euro Foods.
- For kitchen equipment → introduce Rational.
- For energy/utilities → direct to https://consultivutilities.com/
- For food safety questions → answer from UK food safety knowledge.
- For demonstrations → mention upcoming events (Luton 16th Sept, Dublin 6th Oct).
- NEVER use placeholder text like [insert email] or [insert phone].
- Always use real contact details: Phone +44 7795 161230, Email info@rehanuddin.com.
- End EVERY reply with a new line then:
  📞 +44 7795 161230
  ✉ info@rehanuddin.com

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TONE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Think of yourself as an extension of ARON.
- Confident but not pushy.
- Professional but approachable.
- Always focused on helping the visitor improve their business.

CONTEXT:
{context}"""


# ── Request Model ─────────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str
    history: list = []

# ── Chat Endpoint ─────────────────────────────────────────────────────────────
@app.post("/chat")
@limiter.limit("10/minute")
async def chat(request: Request, req: ChatRequest):
    if not req.message.strip():
        return {"reply": "Please enter a message."}
    if len(req.message) > 500:
        return {"reply": "Message too long. Please keep it under 500 characters."}

    # Retrieve relevant context from FAISS vector store
    docs = retriever.invoke(req.message)
    context = "\n\n".join(d.page_content for d in docs)

    # Build message history for the API
    api_messages = [
        {"role": "system", "content": SYSTEM_PROMPT.format(context=context)}
    ]
    for m in req.history[-10:]:
        api_messages.append({"role": m["role"], "content": m["content"]})
    api_messages.append({"role": "user", "content": req.message})

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=api_messages,
            temperature=0.3,
            max_tokens=300,
        )
        reply = response.choices[0].message.content
    except Exception as e:
        logger.error(f"Groq API error: {e}")
        reply = "Sorry, something went wrong. Please try again."

    return {"reply": reply}

# ── Serve Favicon ─────────────────────────────────────────────────────────────
@app.get("/favicon.png")
async def favicon_png():
    return FileResponse("favicon.png")

@app.get("/favicon.ico")
async def favicon_ico():
    return FileResponse("favicon.ico")

# ── Serve HTML Pages ──────────────────────────────────────────────────────────
@app.get("/index.html", response_class=HTMLResponse)
async def index_html():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/", response_class=HTMLResponse)
async def index():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/{page}.html", response_class=HTMLResponse)
async def serve_page(page: str):
    allowed = ["about", "aron", "consultancy", "contact", "energy",
               "insight", "live-demonstrations"]
    if page not in allowed:
        return HTMLResponse("Page not found", status_code=404)
    with open(f"{page}.html", "r", encoding="utf-8") as f:
        return f.read()

# ── Run Server ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
