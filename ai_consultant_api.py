from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # Add this import
from pydantic import BaseModel, field_validator
from typing import List, Optional
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
import requests
import uvicorn
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("❌ GEMINI_API_KEY not found in .env file!")
    exit(1)

try:
    genai.configure(api_key=GEMINI_API_KEY)
    # Use the correct model name
    model = genai.GenerativeModel('gemini-1.5-flash')  # Updated model name
    print("✅ Gemini API configured successfully")
except Exception as e:
    print(f"❌ Failed to configure Gemini API: {e}")
    exit(1)

app = FastAPI(title="AI Shopping Consultant API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

class ProductData(BaseModel):
    name: str
    price: str
    rating: Optional[str] = None
    total_ratings: Optional[str] = None
    sold_count: Optional[str] = None
    store_type: Optional[str] = None
    store_rating: Optional[str] = None
    store_reviews: Optional[str] = None
    processing_time: Optional[str] = None
    description: Optional[str] = None
    url: str

class AIConsultationRequest(BaseModel):
    product_data: ProductData
    user_budget: Optional[float] = None
    user_preferences: Optional[str] = None

class ConsultationResponse(BaseModel):
    recommendation: str
    confidence_score: float
    analysis: str
    pros: List[str]
    cons: List[str]
    key_insights: List[str]
    budget_analysis: Optional[str] = None

def create_analysis_prompt(product_data: ProductData, user_budget: Optional[float] = None, user_preferences: Optional[str] = None) -> str:
    """Create detailed prompt for Gemini AI analysis"""
    
    prompt = f"""
Analisis produk Tokopedia berikut sebagai konsultan belanja AI yang berpengalaman:

INFORMASI PRODUK:
- Nama: {product_data.name}
- Harga: {product_data.price}
- Rating: {product_data.rating or 'Tidak tersedia'}
- Jumlah Rating: {product_data.total_ratings or 'Tidak tersedia'}
- Terjual: {product_data.sold_count or 'Tidak tersedia'}
- Tipe Toko: {product_data.store_type or 'Tidak tersedia'}
- Rating Toko: {product_data.store_rating or 'Tidak tersedia'}
- Jumlah Review Toko: {product_data.store_reviews or 'Tidak tersedia'}
- Waktu Proses: {product_data.processing_time or 'Tidak tersedia'}
- Deskripsi: {product_data.description[:500] if product_data.description else 'Tidak tersedia'}...
- URL: {product_data.url}

PREFERENSI USER:
- Budget: {f"Rp {user_budget:,.0f}" if user_budget else 'Tidak disebutkan'}
- Preferensi: {user_preferences or 'Tidak disebutkan'}

Berikan analisis mendalam dan rekomendasi pembelian dalam format JSON berikut:

{{
    "recommendation": "LAYAK_BELI" | "TIDAK_LAYAK_BELI" | "LAYAK_BELI_DENGAN_CATATAN",
    "confidence_score": 0.85,
    "analysis": "Analisis lengkap produk berdasarkan data yang tersedia...",
    "pros": ["Keunggulan 1", "Keunggulan 2", "Keunggulan 3"],
    "cons": ["Kekurangan 1", "Kekurangan 2"],
    "key_insights": ["Insight penting 1", "Insight penting 2"],
    "budget_analysis": "Analisis kesesuaian dengan budget user"
}}

KRITERIA REKOMENDASI:
- LAYAK_BELI: Rating >4.5, toko terpercaya, banyak terjual, harga wajar
- TIDAK_LAYAK_BELI: Rating <4.0, toko kurang terpercaya, sedikit terjual, harga tidak wajar
- LAYAK_BELI_DENGAN_CATATAN: Rating 4.0-4.5, ada pertimbangan khusus

Berikan analisis yang objektif dan membantu pengambilan keputusan.
"""
    return prompt

@app.post("/ai-consultant", response_model=ConsultationResponse)
async def get_ai_consultation(request: AIConsultationRequest):
    """Get AI-powered purchase recommendation"""
    try:
        # Create analysis prompt
        prompt = create_analysis_prompt(
            product_data=request.product_data,
            user_budget=request.user_budget,
            user_preferences=request.user_preferences
        )
        
        print(f"🤖 Analyzing product: {request.product_data.name}")
        
        # Generate response with updated model
        response = model.generate_content(prompt)
        
        if not response.text:
            raise HTTPException(status_code=500, detail="No response from AI model")
        
        # Parse JSON response
        try:
            # Clean response text (remove markdown code blocks if present)
            response_text = response.text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            # Find JSON object in response
            start_idx = response_text.find("{")
            end_idx = response_text.rfind("}") + 1
            
            if start_idx != -1 and end_idx != 0:
                json_text = response_text[start_idx:end_idx]
                ai_analysis = json.loads(json_text)
            else:
                raise ValueError("No JSON found in response")
            
            # Validate required fields
            required_fields = ["recommendation", "confidence_score", "analysis", "pros", "cons", "key_insights"]
            for field in required_fields:
                if field not in ai_analysis:
                    raise ValueError(f"Missing required field: {field}")
            
            # Validate recommendation value
            valid_recommendations = ["LAYAK_BELI", "TIDAK_LAYAK_BELI", "LAYAK_BELI_DENGAN_CATATAN"]
            if ai_analysis["recommendation"] not in valid_recommendations:
                raise ValueError(f"Invalid recommendation: {ai_analysis['recommendation']}")
            
            # Create response
            consultation_response = ConsultationResponse(
                recommendation=ai_analysis["recommendation"],
                confidence_score=float(ai_analysis["confidence_score"]),
                analysis=ai_analysis["analysis"],
                pros=ai_analysis["pros"],
                cons=ai_analysis["cons"],
                key_insights=ai_analysis["key_insights"],
                budget_analysis=ai_analysis.get("budget_analysis")
            )
            
            print(f"✅ Analysis completed: {consultation_response.recommendation}")
            return consultation_response
            
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse AI response as JSON: {e}")
            print(f"Raw response: {response.text}")
            raise HTTPException(status_code=500, detail="Invalid JSON response from AI model")
        
        except ValueError as e:
            print(f"❌ Invalid AI response format: {e}")
            raise HTTPException(status_code=500, detail=f"Invalid AI response: {str(e)}")
            
    except Exception as e:
        print(f"❌ Error in AI consultation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI consultation failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test Gemini connection
        test_response = model.generate_content("Test: return 'OK'")
        return {
            "status": "healthy",
            "gemini_api": "connected",
            "model": "gemini-1.5-flash",
            "test_response": test_response.text if test_response else "No response",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "gemini_api": "disconnected",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/")
async def root():
    return {
        "message": "🤖 AI Shopping Consultant API",
        "version": "1.0.0",
        "status": "running",
        "gemini_configured": bool(GEMINI_API_KEY),
        "model": "gemini-1.5-flash",
        "endpoints": {
            "POST /ai-consultant": "Analyze product and get AI recommendation",
            "GET /health": "Health check",
        }
    }

if __name__ == "__main__":
    print("🤖 Starting AI Shopping Consultant API...")
    print(f"✅ Gemini API Key: {'configured' if GEMINI_API_KEY else 'missing'}")
    uvicorn.run(app, host="0.0.0.0", port=8001)
