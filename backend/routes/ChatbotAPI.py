# 챗봇 라우터, 챗봇 서비스(ChatbotService.py)를 사용 
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from AzureServiceModule.ChatbotService import ChatbotService 
import os 
from dotenv import load_dotenv
load_dotenv()

router = APIRouter()
chatbot_service = ChatbotService(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    endpoint=os.getenv("ENDPOINT_URL"),
    deployment=os.getenv("DEPLOYMENT_NAME"),
    search_key=os.getenv("SEARCH_KEY"),
    search_endpoint=os.getenv("SEARCH_ENDPOINT"),
    search_index=os.getenv("SEARCH_INDEX_NAME")
)

# api/chatbot/response 경로의 라우터입니다. 
# 함수인자값
# Request 요청(body에 user_input과 history가 담겨있어야 합니다.)
@router.post("/response")
async def respond(request: Request):
    body = await request.json()
    user_input = body.get("input", "")
    history = body.get("history", [])

    if not user_input:
        return JSONResponse(content={"error": "입력값이 비어 있습니다."}, status_code=400)

    try:
        result = await chatbot_service.handle_user_input(user_input, history)
        return JSONResponse(content=result)
# 프론트엔드에서 접근할 수 있는 형식 및 리턴값 
# response.data.chat_history : 전체 사용자, 챗봇 히스토리 출력 
# response.data.structured_data : 챗봇 응답만 출력
# response.data.response_text : 현재까지 모인 JSON 변수 
# response.data.intent : 사용자 의도 분류(수집 / 검색 / 혼합)
# response.data.stage : 사용자가 있는 공연 단계(기획 / 판매)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
