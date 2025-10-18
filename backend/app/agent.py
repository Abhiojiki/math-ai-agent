from typing import Dict, List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from app.config import settings  # ← Add app.
from app.web_search import get_web_search_client
# from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.config import settings

def basic_input_guardrails(text: str) -> bool:
    t = text.lower()
    for bad in ["politics","religion","weapon","nsfw","hack","adult"]:
        if bad in t: return False
    return True

class QdrantRetriever:
    def __init__(self):
        settings.validate()
        self.client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
            timeout=120
        )
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.collection = settings.QDRANT_COLLECTION_NAME
        
        try:
            info = self.client.get_collection(self.collection)
            if hasattr(info, "points_count"):
                print(f"✓ Qdrant '{self.collection}' has {info.points_count} points")
        except Exception as e:
            raise RuntimeError(f"Cannot access Qdrant collection: {e}")
    
    def search(self, query: str, top_k: int, threshold: float) -> List[Dict]:
        vec = self.model.encode(query).tolist()
        results = self.client.search(
            collection_name=self.collection,
            query_vector=vec,
            limit=top_k
        )
        
        # Filter with threshold
        filtered = []
        for r in results:
            score = float(r.score or 0.0)
            if score >= threshold:
                filtered.append(r)
        
        return [
            {
                "problem": r.payload.get("problem",""),
                "solution": r.payload.get("solution",""),
                "level": r.payload.get("level",""),
                "type": r.payload.get("type",""),
                "score": float(r.score or 0.0)
            }
            for r in filtered
        ]



class MathAgent:
    def __init__(self):
        self.retriever = QdrantRetriever()
        self.llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            api_key=settings.GOOGLE_API_KEY,
            temperature=0.2
        )
        # FIX: Initialize web search client
        self.web_search_client = get_web_search_client()
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system",
             "You are a math professor explaining step-by-step to a student.\n\n"
             "CRITICAL FORMATTING RULES:\n"
             "- Do NOT use LaTeX ($$, $, \\(...\\), \\[...\\], etc.)\n"
             "- Write math using plain text and Unicode symbols (√, ², ³, ∫, ∑, π, etc.)\n"
             "- For fractions: use '/' or Unicode fraction characters like ½, ¾\n"
             "- For exponents: use superscript Unicode (x², x³) or write x^2, x^3\n"
             "- For square roots: use √ symbol or write sqrt(...)\n"
             "- For equations: write them on separate lines with clear labels\n"
             "- End with a boxed final answer using text formatting (e.g., 'FINAL ANSWER: x = 3')\n"
             "- Include a brief tip at the end.\n\n"
             "Example output format:\n"
             "Step 1: Identify the formula\n"
             "For a quadratic equation ax² + bx + c = 0, the quadratic formula is:\n"
             "x = (-b ± √(b² - 4ac)) / (2a)\n\n"
             "FINAL ANSWER: x = (-b ± √(b² - 4ac)) / (2a)\n\n"
             "TIP: Remember the discriminant b² - 4ac determines the number of solutions."
            ),
            ("user",
             "Question:\n{question}\n\nContext:\n{context}\n\n"
             "If context is relevant, use it to teach and adapt the solution steps; "
             "otherwise solve from first principles with numbered steps and Unicode math notation."
            )
        ])
    
    def route_and_answer(self, query: str) -> Dict:
        # FIX: Complete guardrails return
        if not basic_input_guardrails(query):
            return {
                "query": query,
                "answer": "Only mathematics content allowed.",
                "source": "guardrails",
                "confidence_score": 0.0,
                "kb_matches": 0
            }
        
        # STEP 1: Try Knowledge Base
        kb_hits = self.retriever.search(query, settings.TOP_K, settings.SCORE_THRESHOLD)
        
        if kb_hits:
            # KB found results
            confidence = max((h["score"] for h in kb_hits), default=0.0)
            context = "\n\n---\n\n".join(
                f"Problem: {h['problem']}\nSolution: {h['solution']}\n"
                f"[Score={h['score']:.3f}, Level={h['level']}, Type={h['type']}]"
                for h in kb_hits
            )
            source = "knowledge_base"
            print(f"✓ Using {len(kb_hits)} KB results (best: {confidence:.3f})")
        
        else:
            # STEP 2: Fallback to Web Search
            print("⚠️ KB failed; trying WolframAlpha...")
            # FIX: Use correct variable name
            web_result = self.web_search_client.search_web(query)
            
            if web_result["success"]:
                context = f"WolframAlpha answer:\n{web_result['content']}"
                source = "web_search"
                confidence = 0.5
                print(f"✓ WolframAlpha returned answer")
            else:
                context = "No KB or web results. Solve from first principles."
                source = "llm_knowledge"
                confidence = 0.0
                print("⚠️ Both KB and web search failed; using LLM only")
        
        # STEP 3: Generate explanation with LLM
        chain = self.prompt | self.llm
        resp = chain.invoke({"question": query, "context": context})
        answer = resp.content
        
        return {
            "query": query,
            "answer": answer,
            "source": source,
            "confidence_score": float(confidence),
            "kb_matches": len(kb_hits) if kb_hits else 0
        }

_agent: Optional[MathAgent] = None

def get_agent() -> MathAgent:
    global _agent
    if _agent is None:
        _agent = MathAgent()
    return _agent
