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
    
    # Add flexibility for different field types
    @field_validator('rating', 'store_rating', mode='before')
    def validate_rating(cls, v):
        if v is None:
            return None
        # Convert to string if needed
        return str(v)
    
    @field_validator('total_ratings', 'store_reviews', mode='before')
    def validate_counts(cls, v):
        if v is None:
            return None
        # Convert to string if needed
        return str(v)

# Enhanced models to handle the full scraping response structure
class ScrapingProductDetails(BaseModel):
    product_name: str
    store_name: Optional[str] = None
    product_url: Optional[str] = None
    review_url: Optional[str] = None
    scraped_at: Optional[str] = None
    price: str
    rating: str
    rating_count: Optional[str] = None
    sold_count: Optional[str] = None
    description: Optional[str] = None
    
    # Add flexibility for different field types
    @field_validator('rating', mode='before')
    def validate_rating(cls, v):
        if v is None:
            return "0"
        return str(v)
    
    @field_validator('rating_count', 'sold_count', mode='before')
    def validate_counts(cls, v):
        if v is None:
            return "Tidak tersedia"
        return str(v)

class ReviewData(BaseModel):
    rating: int
    reviewer_name: str
    review_text: str
    review_date: str
    variant: Optional[str] = None
    scraped_at: Optional[str] = None

class ScrapingSummary(BaseModel):
    total_reviews_scraped: int
    target_ratings: List[int]
    max_reviews_per_rating: int
    scraped_at: str

class FullScrapingResponse(BaseModel):
    product_details: ScrapingProductDetails
    reviews: List[ReviewData]
    summary: ScrapingSummary

class AIConsultationRequest(BaseModel):
    product_data: ProductData
    user_budget: Optional[float] = None
    user_preferences: Optional[str] = None

# New request format that handles full scraping response
class FullAIConsultationRequest(BaseModel):
    product_details: ScrapingProductDetails
    reviews: Optional[List[ReviewData]] = None
    summary: Optional[ScrapingSummary] = None
    user_budget: Optional[float] = None
    user_preferences: Optional[str] = None

# Flexible request that can handle both formats
class FlexibleAIRequest(BaseModel):
    # Support both old format
    product_data: Optional[ProductData] = None
    # And new format
    product_details: Optional[ScrapingProductDetails] = None
    reviews: Optional[List[ReviewData]] = None
    summary: Optional[ScrapingSummary] = None
    # User preferences
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

def create_enhanced_analysis_prompt(product_details: ScrapingProductDetails, reviews: Optional[List[ReviewData]] = None, summary: Optional[ScrapingSummary] = None, user_budget: Optional[float] = None, user_preferences: Optional[str] = None) -> str:
    """Create enhanced prompt with full scraping data including reviews"""
    
    # Analyze review sentiment
    review_analysis = ""
    if reviews:
        # Count ratings
        rating_counts = {}
        positive_reviews = []
        negative_reviews = []
        
        for review in reviews[:20]:  # Limit to first 20 reviews for token efficiency
            rating = review.rating
            rating_counts[rating] = rating_counts.get(rating, 0) + 1
            
            if rating >= 4:
                positive_reviews.append(review.review_text[:200])
            elif rating <= 2:
                negative_reviews.append(review.review_text[:200])
        
        review_analysis = f"""
ANALISIS REVIEW ({len(reviews)} total reviews):
Distribusi Rating: {rating_counts}

SAMPLE REVIEW POSITIF:
{chr(10).join([f"- {review}" for review in positive_reviews[:5]])}

SAMPLE REVIEW NEGATIF:
{chr(10).join([f"- {review}" for review in negative_reviews[:5]])}
"""
    
    prompt = f"""
Analisis produk Tokopedia berikut sebagai konsultan belanja AI yang berpengalaman dengan data lengkap:

INFORMASI PRODUK:
- Nama: {product_details.product_name}
- Harga: {product_details.price}
- Rating: {product_details.rating}
- Jumlah Rating: {product_details.rating_count or 'Tidak tersedia'}
- Terjual: {product_details.sold_count or 'Tidak tersedia'}
- Toko: {product_details.store_name or 'Tidak tersedia'}
- URL: {product_details.product_url or 'Tidak tersedia'}
- Deskripsi: {product_details.description[:500] if product_details.description else 'Tidak tersedia'}...

{review_analysis}

PREFERENSI USER:
- Budget: {f"Rp {user_budget:,.0f}" if user_budget else 'Tidak disebutkan'}
- Preferensi: {user_preferences or 'Tidak disebutkan'}

Berikan analisis mendalam dan rekomendasi pembelian dalam format JSON berikut:

{{
    "recommendation": "LAYAK_BELI" | "TIDAK_LAYAK_BELI" | "LAYAK_BELI_DENGAN_CATATAN",
    "confidence_score": 0.85,
    "analysis": "Analisis lengkap produk berdasarkan data yang tersedia dan review pelanggan...",
    "pros": ["Keunggulan 1", "Keunggulan 2", "Keunggulan 3"],
    "cons": ["Kekurangan 1", "Kekurangan 2"],
    "key_insights": ["Insight penting 1", "Insight penting 2"],
    "budget_analysis": "Analisis kesesuaian dengan budget user"
}}

KRITERIA REKOMENDASI:
- LAYAK_BELI: Rating >4.5, toko terpercaya, banyak terjual, harga wajar, review positif
- TIDAK_LAYAK_BELI: Rating <4.0, toko kurang terpercaya, sedikit terjual, harga tidak wajar, banyak keluhan
- LAYAK_BELI_DENGAN_CATATAN: Rating 4.0-4.5, ada pertimbangan khusus berdasarkan review

PETUNJUK ANALISIS:
1. Gunakan data review untuk validasi kualitas produk
2. Perhatikan pola keluhan dan pujian dari pembeli
3. Fokus pada value for money dan kualitas produk
4. Pertimbangkan kredibilitas toko dan track record
5. Bandingkan dengan produk sejenis di pasar
6. Berikan rekomendasi yang objektif berdasarkan data
7. Gunakan bahasa Indonesia yang mudah dipahami
"""
    
    return prompt

@app.post("/ai-consultant", response_model=ConsultationResponse)
async def get_ai_consultation(request: AIConsultationRequest):
    """Get AI-powered purchase recommendation"""
    try:
        print(f"📥 Received consultation request")
        print(f"📊 Product data: {request.product_data}")
        print(f"💰 User budget: {request.user_budget}")
        print(f"📝 User preferences: {request.user_preferences}")
        
        # Create analysis prompt
        prompt = create_analysis_prompt(
            product_data=request.product_data,
            user_budget=request.user_budget,
            user_preferences=request.user_preferences
        )
        
        print(f"🤖 Analyzing product: {request.product_data.name}")
        print(f"📤 Sending prompt to Gemini...")
        
        # Generate response with updated model
        response = model.generate_content(prompt)
        
        if not response.text:
            raise HTTPException(status_code=500, detail="No response from AI model")
        
        print(f"📥 Raw AI response: {response.text}")
        
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

@app.post("/ai-consultant-flexible", response_model=ConsultationResponse)
async def get_flexible_ai_consultation(request: FlexibleAIRequest):
    """Get AI-powered purchase recommendation with flexible input format"""
    try:
        print(f"📥 Received flexible consultation request")
        
        # Check which format is being used
        if request.product_details:
            # New format with full scraping response
            print(f"📊 Using new format with product_details")
            print(f"📊 Product: {request.product_details.product_name}")
            print(f"📊 Reviews: {len(request.reviews) if request.reviews else 0}")
            print(f"💰 User budget: {request.user_budget}")
            print(f"📝 User preferences: {request.user_preferences}")
            
            # Create enhanced analysis prompt
            prompt = create_enhanced_analysis_prompt(
                product_details=request.product_details,
                reviews=request.reviews,
                summary=request.summary,
                user_budget=request.user_budget,
                user_preferences=request.user_preferences
            )
            
            print(f"🤖 Analyzing product with reviews: {request.product_details.product_name}")
            
        elif request.product_data:
            # Old format compatibility
            print(f"📊 Using old format with product_data")
            print(f"📊 Product: {request.product_data.name}")
            print(f"💰 User budget: {request.user_budget}")
            print(f"📝 User preferences: {request.user_preferences}")
            
            # Create standard analysis prompt
            prompt = create_analysis_prompt(
                product_data=request.product_data,
                user_budget=request.user_budget,
                user_preferences=request.user_preferences
            )
            
            print(f"🤖 Analyzing product: {request.product_data.name}")
            
        else:
            raise HTTPException(status_code=400, detail="Either product_data or product_details must be provided")
        
        print(f"📤 Sending prompt to Gemini...")
        
        # Generate response with updated model
        response = model.generate_content(prompt)
        
        if not response.text:
            raise HTTPException(status_code=500, detail="No response from AI model")
        
        print(f"📥 Raw AI response: {response.text}")
        
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
        print(f"❌ Error in flexible AI consultation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI consultation failed: {str(e)}")

@app.post("/debug-request")
async def debug_request(request: AIConsultationRequest):
    """Debug endpoint to see what data is being received"""
    return {
        "received_data": {
            "product_data": request.product_data.dict(),
            "user_budget": request.user_budget,
            "user_preferences": request.user_preferences
        },
        "validation_status": "valid",
        "timestamp": datetime.now().isoformat()
    }

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
            "POST /ai-consultant": "Analyze product and get AI recommendation (legacy format)",
            "POST /ai-consultant-flexible": "Analyze product with flexible format (supports both old and new structure)",
            "POST /debug-request": "Debug endpoint to see received data",
            "GET /health": "Health check",
        },
        "supported_formats": {
            "new_format": "Full scraping response with product_details, reviews, and summary",
            "old_format": "Legacy format with product_data for backward compatibility"
        }
    }

if __name__ == "__main__":
    print("🤖 Starting AI Shopping Consultant API...")
    print(f"✅ Gemini API Key: {'configured' if GEMINI_API_KEY else 'missing'}")
    uvicorn.run(app, host="0.0.0.0", port=8001)
