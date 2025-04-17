import gradio as gr
import asyncio
import os
import json
from dotenv import load_dotenv
from backend.AzureServiceModule.ChatbotService import ChatbotService
import threading
import uvicorn

# 환경 변수 로드
load_dotenv()

# ChatbotService 인스턴스 생성
chatbot = ChatbotService(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    endpoint=os.getenv("ENDPOINT_URL"),
    deployment=os.getenv("DEPLOYMENT_NAME"),
    search_key=os.getenv("SEARCH_KEY"),
    search_endpoint=os.getenv("SEARCH_ENDPOINT"),
    search_index=os.getenv("SEARCH_INDEX_NAME")
)

# 대화 기록을 저장할 변수
history = []

# 비동기 함수를 동기 함수로 래핑
def predict(message, chat_history):
    global history
    
    if not message.strip():
        return chat_history, "", ""
    
    # 비동기 함수 실행을 위한 이벤트 루프
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # 챗봇 서비스 호출
    result = loop.run_until_complete(chatbot.handle_user_input(message, history))
    
    # 대화 기록 업데이트
    history = result["chat_history"]
    
    # Gradio 챗봇에 추가할 메시지 생성
    bot_message = result["response_text"]
    
    # 메시지 형식으로 추가
    chat_history.append({"role": "user", "content": message})
    chat_history.append({"role": "assistant", "content": bot_message})
    
    # 수집된 변수 정보 표시
    collected_vars = json.dumps(result["structured_data"], ensure_ascii=False, indent=2)
    
    # 사이드바 정보 업데이트
    sidebar_info = f"🔍 단계: {result['stage']}\n📝 의도: {result['intent']}\n\n💾 수집된 변수:\n{collected_vars}"
    
    return chat_history, sidebar_info, ""

# Gradio 인터페이스 생성
with gr.Blocks() as demo:
    gr.Markdown("# 공연 기획 챗봇")
    
    with gr.Row():
        with gr.Column(scale=3):
            chatbot_component = gr.Chatbot(height=600, type="messages")
            
            # 기본 텍스트박스
            msg = gr.Textbox(
                placeholder="공연에 대해 물어보세요...", 
                lines=1
            )
            
            with gr.Row():
                clear = gr.Button("대화 초기화")
                submit_btn = gr.Button("전송", variant="primary")
            
        with gr.Column(scale=1):
            sidebar = gr.Textbox(label="공연 정보", lines=20, max_lines=30)
    
    # 메시지 전송 시 이벤트 연결
    msg.submit(predict, [msg, chatbot_component], [chatbot_component, sidebar, msg])
    submit_btn.click(predict, [msg, chatbot_component], [chatbot_component, sidebar, msg])
    
    # 초기화 버튼 이벤트 연결
    def clear_chat():
        global history
        history = []
        return [], "공연 정보가 초기화되었습니다."
    
    clear.click(clear_chat, None, [chatbot_component, sidebar])

# FastAPI 서버를 별도 스레드에서 실행
def run_fastapi():
    try:
        from backend.demo import app
        uvicorn.run(app, host="127.0.0.1", port=8000)
    except Exception as e:
        print(f"FastAPI 서버 실행 오류: {str(e)}")

# 메인 실행
if __name__ == "__main__":
    # FastAPI 서버 시작 (선택 사항)
    try:
        threading.Thread(target=run_fastapi, daemon=True).start()
        print("FastAPI 서버가 백그라운드에서 시작되었습니다.")
    except:
        print("FastAPI 서버가 이미 실행 중이거나 시작할 수 없습니다.")
    
    # Gradio 앱 실행
    demo.launch()