from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routes import MLAnalysisAPI
from routes import ChatbotAPI 

app = FastAPI(docs_url="/api/docs")

# CORS 허용 (프론트에서 접근 가능하게)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev 환경에서는 * 가능
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 주의: 챗봇 대화를 통한 분석은 /api/chatbot/response 엔드포인트를 통해 반환됩니다.
app.include_router(MLAnalysisAPI.router, prefix="/api/ml")
app.include_router(ChatbotAPI.router, prefix="/api/chatbot")

# 정적 파일 (D3.js 포함 프론트엔드)
# app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")