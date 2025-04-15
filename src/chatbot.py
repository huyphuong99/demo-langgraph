import os
from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import Graph, StateGraph

# Kiểm tra API key
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY không được tìm thấy trong biến môi trường. Hãy đặt biến môi trường OPENAI_API_KEY trước khi chạy ứng dụng.")

# Khởi tạo model
llm = ChatOpenAI(model_name="gpt-3.5-turbo")
prompt = ChatPromptTemplate.from_messages([
    ("system", "Bạn là một trợ lý AI thông minh và hữu ích. Hãy trả lời câu hỏi của người dùng một cách chính xác và ngắn gọn."),
    ("human", "{input}")
])

# Định nghĩa các node trong graph
def process_message(state: Dict[str, Any]) -> Dict[str, Any]:
    """Node xử lý tin nhắn."""
    messages = state.get("messages", [])
    current_message = state.get("current_message", "")

    # Thêm tin nhắn của người dùng vào lịch sử
    messages.append(HumanMessage(content=current_message))

    # Tạo chuỗi xử lý
    chain = prompt | llm

    # Lấy phản hồi từ model
    response = chain.invoke({"input": current_message})

    # Thêm phản hồi vào lịch sử
    messages.append(AIMessage(content=response.content))

    # Cập nhật state
    return {
        "messages": messages,
        "current_message": "",
        "response": response.content
    }

def should_continue(state: Dict[str, Any]) -> str:
    """Node quyết định có tiếp tục hội thoại hay không."""
    last_message = state.get("current_message", "").lower()
    if "tạm biệt" in last_message or "goodbye" in last_message:
        return "end"
    return "continue"

# Tạo graph
def create_chat_graph() -> Graph:
    """Tạo một graph xử lý hội thoại đơn giản."""
    workflow = StateGraph(StateType=Dict[str, Any])
    
    # Thêm các node
    workflow.add_node("process_message", process_message)
    workflow.add_node("should_continue", should_continue)
    
    # Định nghĩa luồng xử lý
    workflow.set_entry_point("process_message")
    workflow.add_edge("process_message", "should_continue")
    
    # Thêm các edge có điều kiện
    workflow.add_conditional_edges(
        "should_continue",
        {
            "continue": "process_message",
            "end": "end"
        }
    )
    
    # Compile graph
    return workflow.compile()

# Khởi tạo state
state = {
    "messages": [],
    "current_message": "",
    "response": ""
}

# Tạo chat graph
chat_graph = create_chat_graph()

def main():
    """Hàm chính để chạy chatbot."""
    print("Chatbot đã sẵn sàng! Gõ 'tạm biệt' để kết thúc.")
    
    # Vòng lặp hội thoại
    while True:
        # Nhận input từ người dùng
        user_input = input("\nBạn: ")
        
        # Cập nhật state
        state["current_message"] = user_input
        
        # Chạy graph
        result = chat_graph.invoke(state)
        
        # Cập nhật state
        state.update(result)
        
        # In phản hồi
        print(f"\nBot: {state['response']}")
        
        # Kiểm tra điều kiện kết thúc
        if "tạm biệt" in user_input.lower() or "goodbye" in user_input.lower():
            print("\nTạm biệt! Hẹn gặp lại!")
            break

if __name__ == "__main__":
    main() 