# LangGraph: Hướng dẫn Chi tiết

## Mục lục
- [1. Giới thiệu](#1-giới-thiệu)
- [2. Nguyên lý hoạt động](#2-nguyên-lý-hoạt-động)
- [3. Cài đặt](#3-cài-đặt)
- [4. Khái niệm cốt lõi](#4-khái-niệm-cốt-lõi)
- [5. Xây dựng đồ thị đầu tiên](#5-xây-dựng-đồ-thị-đầu-tiên)
- [6. Tính năng nâng cao](#6-tính-năng-nâng-cao)
- [7. Ví dụ thực tế](#7-ví-dụ-thực-tế)
- [8. Best Practices](#8-best-practices)
- [9. Troubleshooting](#9-troubleshooting)
- [10. Tài liệu tham khảo](#10-tài-liệu-tham-khảo)

## 1. Giới thiệu

### 1.1 LangGraph là gì?
LangGraph là một thư viện mở rộng của LangChain, được thiết kế đặc biệt để xây dựng các ứng dụng AI có trạng thái (stateful) và phức tạp. Khác với chuỗi tuần tự (chains) trong LangChain thông thường, LangGraph cho phép tạo ra các **đồ thị có chu kỳ (cyclic graphs)**, mở rộng khả năng xây dựng luồng công việc phức tạp với khả năng quay lại hoặc lặp lại các bước trước đó.

### 1.2 Tại sao cần LangGraph?
- **Vượt qua giới hạn của chuỗi tuyến tính**: Hỗ trợ các workflow cần vòng lặp và điều kiện rẽ nhánh phức tạp
- **Xây dựng agent thông minh**: Tạo các agent có khả năng lập luận và đánh giá kết quả của chính mình
- **Phối hợp đa tác nhân**: Cho phép nhiều agent chuyên biệt làm việc cùng nhau
- **Tích hợp tương tác người dùng**: Dễ dàng kết hợp human-in-the-loop vào quy trình

### 1.3 Ứng dụng thực tế
- Hệ thống hỏi đáp (QA) với khả năng hỏi lại để làm rõ
- Chatbot có khả năng thu thập thông tin liên tục cho đến khi đủ
- Công cụ hỗ trợ lập trình với khả năng lặp lại đến khi code hoàn chỉnh
- Hệ thống đa agent phối hợp để giải quyết vấn đề phức tạp

## 2. Nguyên lý hoạt động

### 2.1 Mô hình đồ thị
LangGraph sử dụng mô hình đồ thị có hướng (directed graph) để biểu diễn luồng công việc:
- **Nút (Node)**: Đại diện cho các hàm xử lý
- **Cạnh (Edge)**: Xác định luồng từ nút này sang nút khác
- **Cạnh có điều kiện (Conditional Edge)**: Xác định nút tiếp theo dựa trên logic tùy chỉnh

### 2.2 Quản lý trạng thái
- **State**: Một từ điển (dictionary) được truyền qua các nút, lưu trữ dữ liệu trong suốt quá trình
- **Immutability**: Mỗi nút tạo ra phiên bản mới của state thay vì sửa đổi trực tiếp
- **Trả về kết quả một phần**: Nút chỉ cần trả về các khóa đã thay đổi

### 2.3 Luồng thực thi
1. Đồ thị khởi tạo với trạng thái ban đầu
2. Mỗi nút nhận trạng thái hiện tại, xử lý và trả về trạng thái mới
3. Dựa trên logic điều kiện hoặc cạnh cố định, trạng thái được chuyển đến nút tiếp theo
4. Quá trình tiếp tục cho đến khi đạt đến nút kết thúc hoặc điều kiện dừng

## 3. Cài đặt

```bash
# Cài đặt LangGraph
pip install langgraph

# Nếu đã có LangChain
pip install langgraph

# Nếu muốn cài đặt cả LangChain
pip install langchain langgraph
```

Yêu cầu hệ thống:
- Python 3.9+
- LangChain (nếu muốn tích hợp)

## 4. Khái niệm cốt lõi

### 4.1 StateGraph
`StateGraph` là lớp chính để khởi tạo đồ thị có trạng thái. Nó cung cấp các phương thức để:
- Thêm node
- Xác định cạnh
- Thiết lập điểm bắt đầu/kết thúc
- Biên dịch đồ thị thành một ứng dụng có thể thực thi

```python
from langgraph.graph import StateGraph
from typing import TypedDict, Annotated

# Định nghĩa kiểu trạng thái
class State(TypedDict):
    input: str
    output: str

# Khởi tạo đồ thị
graph = StateGraph(State)
```

### 4.2 Node

Node là các hàm xử lý trong đồ thị. Mỗi node nhận trạng thái hiện tại và trả về một từ điển chứa các khóa đã thay đổi:

```python
def process_input(state: State) -> dict:
    # Xử lý đầu vào
    processed_text = state["input"].upper()
    
    # Chỉ trả về khóa đã thay đổi
    return {"output": processed_text}
```

### 4.3 Edge
Edge định nghĩa luồng từ node này đến node khác:

```python
# Thêm cạnh đơn giản
graph.add_edge("input_node", "process_node")
```

### 4.4 Conditional Edge
Cạnh có điều kiện cho phép xác định node tiếp theo dựa trên kết quả xử lý:

```python
# Hàm quyết định node tiếp theo
def decide_next_node(state: State) -> str:
    if len(state["input"]) > 100:
        return "handle_long_input"
    else:
        return "handle_short_input"

# Thêm cạnh có điều kiện
graph.add_conditional_edges(
    "input_validator",
    decide_next_node,
    {
        "handle_long_input": "long_input_node",
        "handle_short_input": "short_input_node"
    }
)
```

### 4.5 Entry Point và Finish Point

```python
# Thiết lập điểm bắt đầu
graph.set_entry_point("start_node")

# Thiết lập điểm kết thúc
graph.set_finish_point("end_node")
```

## 5. Xây dựng đồ thị đầu tiên

### 5.1 Ví dụ đơn giản

```python
from langgraph.graph import StateGraph
from typing import TypedDict, Annotated

# Định nghĩa kiểu trạng thái
class SimpleState(TypedDict):
    count: int
    message: str

# Tạo các node xử lý
def increment(state: SimpleState) -> dict:
    return {"count": state["count"] + 1}

def format_message(state: SimpleState) -> dict:
    return {"message": f"Giá trị hiện tại: {state['count']}"}

# Khởi tạo đồ thị
workflow = StateGraph(SimpleState)

# Thêm các node
workflow.add_node("increment", increment)
workflow.add_node("format", format_message)

# Kết nối các node
workflow.add_edge("increment", "format")

# Thiết lập điểm bắt đầu và kết thúc
workflow.set_entry_point("increment")
workflow.set_finish_point("format")

# Biên dịch đồ thị
app = workflow.compile()

# Chạy đồ thị với trạng thái ban đầu
result = app.invoke({"count": 0, "message": ""})
print(result)  # Output: {'count': 1, 'message': 'Giá trị hiện tại: 1'}
```

### 5.2 Đồ thị có chu kỳ (cyclic graph)

```python
from langgraph.graph import StateGraph
from typing import TypedDict, Annotated
import operator

# Định nghĩa kiểu trạng thái
class LoopState(TypedDict):
    counter: int
    is_complete: bool

def increment_counter(state: LoopState) -> dict:
    return {"counter": state["counter"] + 1}

def check_completion(state: LoopState) -> dict:
    is_complete = state["counter"] >= 5
    return {"is_complete": is_complete}

# Hàm quyết định luồng
def should_continue(state: LoopState) -> str:
    if state["is_complete"]:
        return "end"
    else:
        return "continue"

# Khởi tạo đồ thị
loop_graph = StateGraph(LoopState)

# Thêm các node
loop_graph.add_node("increment", increment_counter)
loop_graph.add_node("check", check_completion)

# Thêm các cạnh
loop_graph.add_edge("increment", "check")

# Thêm cạnh có điều kiện
loop_graph.add_conditional_edges(
    "check",
    should_continue,
    {
        "continue": "increment",  # Quay lại node increment
        "end": END  # Kết thúc đồ thị
    }
)

# Thiết lập điểm bắt đầu
loop_graph.set_entry_point("increment")

# Biên dịch đồ thị
loop_app = loop_graph.compile()

# Chạy đồ thị
result = loop_app.invoke({"counter": 0, "is_complete": False})
print(result)  # Output: {'counter': 5, 'is_complete': True}
```

## 6. Tính năng nâng cao

### 6.1 Tích hợp với LangChain

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph
from typing import TypedDict, Annotated

# Định nghĩa trạng thái
class AgentState(TypedDict):
    input: str
    agent_outcome: str
    final_response: str

# Khởi tạo LLM
llm = ChatOpenAI(temperature=0)

# Tạo prompt
prompt = ChatPromptTemplate.from_template(
    "Câu hỏi: {input}\nHãy trả lời ngắn gọn và chính xác."
)

# Node xử lý LLM
def process_with_llm(state: AgentState) -> dict:
    chain = prompt | llm
    result = chain.invoke({"input": state["input"]})
    return {"agent_outcome": result.content}

# Node định dạng câu trả lời
def format_response(state: AgentState) -> dict:
    return {"final_response": f"Câu trả lời: {state['agent_outcome']}"}

# Tạo đồ thị
agent_graph = StateGraph(AgentState)
agent_graph.add_node("process", process_with_llm)
agent_graph.add_node("format", format_response)
agent_graph.add_edge("process", "format")
agent_graph.set_entry_point("process")
agent_graph.set_finish_point("format")

# Biên dịch và chạy
agent_app = agent_graph.compile()
result = agent_app.invoke({"input": "Thủ đô của Việt Nam là gì?"})
print(result["final_response"])
```

### 6.2 Human-in-the-Loop

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict
import asyncio

class HITLState(TypedDict):
    query: str
    draft_response: str
    human_feedback: str
    final_response: str

# Node tạo bản nháp
def generate_draft(state: HITLState) -> dict:
    # Giả lập phản hồi từ AI
    return {"draft_response": f"Đây là bản nháp trả lời cho: {state['query']}"}

# Node chờ phản hồi người dùng
async def get_human_feedback(state: HITLState) -> dict:
    # Trong thực tế, bạn sẽ sử dụng giao diện UI để lấy phản hồi
    # Ở đây ta giả lập bằng cách tạm dừng
    print(f"Đang chờ phản hồi về bản nháp: {state['draft_response']}")
    await asyncio.sleep(2)  # Giả lập thời gian chờ
    return {"human_feedback": "Cần bổ sung thêm chi tiết và ví dụ."}

# Node tạo phản hồi cuối cùng
def generate_final(state: HITLState) -> dict:
    return {
        "final_response": (
            f"Phản hồi cuối cùng cho: {state['query']}\n"
            f"(Dựa trên bản nháp và phản hồi: {state['human_feedback']})"
        )
    }

# Khởi tạo đồ thị
hitl_graph = StateGraph(HITLState)
hitl_graph.add_node("draft", generate_draft)
hitl_graph.add_node("feedback", get_human_feedback)
hitl_graph.add_node("final", generate_final)

# Kết nối các node
hitl_graph.add_edge("draft", "feedback")
hitl_graph.add_edge("feedback", "final")

# Cấu hình
hitl_graph.set_entry_point("draft")
hitl_graph.set_finish_point("final")

# Chức năng này sẽ được sử dụng trong môi trường bất đồng bộ
```

### 6.3 Xử lý ngoại lệ

```python
from langgraph.graph import StateGraph
from typing import TypedDict, Union

class ErrorHandlingState(TypedDict):
    input: str
    output: Union[str, None]
    error: Union[str, None]

def risky_operation(state: ErrorHandlingState) -> dict:
    try:
        # Mô phỏng một thao tác có thể gây lỗi
        if "trigger_error" in state["input"]:
            raise ValueError("Đã xảy ra lỗi được mô phỏng")
        return {"output": f"Xử lý thành công: {state['input']}"}
    except Exception as e:
        return {"error": str(e)}

def handle_success(state: ErrorHandlingState) -> dict:
    return {"output": f"Kết quả cuối cùng: {state['output']}"}

def handle_error(state: ErrorHandlingState) -> dict:
    return {"output": f"Đã xử lý lỗi: {state['error']}"}

def route_based_on_error(state: ErrorHandlingState) -> str:
    if state.get("error"):
        return "error_path"
    return "success_path"

# Tạo đồ thị
error_graph = StateGraph(ErrorHandlingState)
error_graph.add_node("process", risky_operation)
error_graph.add_node("success_handler", handle_success)
error_graph.add_node("error_handler", handle_error)

# Thêm cạnh có điều kiện
error_graph.add_conditional_edges(
    "process",
    route_based_on_error,
    {
        "success_path": "success_handler",
        "error_path": "error_handler"
    }
)

# Thiết lập cấu hình
error_graph.set_entry_point("process")
error_graph.set_finish_point("success_handler")
error_graph.set_finish_point("error_handler")

# Biên dịch
error_app = error_graph.compile()
```

### 6.4 Persistence và Tracing

```python
from langgraph.graph import StateGraph
from typing import TypedDict
import json
import os

class PersistState(TypedDict):
    step: int
    data: str

def process_step(state: PersistState) -> dict:
    return {"step": state["step"] + 1, "data": f"Dữ liệu cho bước {state['step'] + 1}"}

# Tạo đồ thị
persist_graph = StateGraph(PersistState)
persist_graph.add_node("process", process_step)
persist_graph.add_edge("process", "process", condition=lambda s: s["step"] < 5)
persist_graph.set_entry_point("process")

# Biên dịch với chức năng lưu vết (tracing)
persist_app = persist_graph.compile(checkpointer=JSONFileCheckpointer())

# Lưu trạng thái
def save_state(state, filename="saved_state.json"):
    with open(filename, "w") as f:
        json.dump(state, f)

# Tải trạng thái
def load_state(filename="saved_state.json"):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return {"step": 0, "data": "Khởi tạo"}

# Chạy với trạng thái đã lưu
state = load_state()
result = persist_app.invoke(state)
save_state(result)
```

## 7. Ví dụ thực tế

### 7.1 Agent tự đánh giá (Self-critique Agent)

```python
from langgraph.graph import StateGraph
from typing import TypedDict, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

class CritiqueState(TypedDict):
    question: str
    answer: str
    critique: str
    final_answer: str
    iterations: int

# Khởi tạo LLM
llm = ChatOpenAI(temperature=0.7)

# Node tạo câu trả lời ban đầu
def generate_answer(state: CritiqueState) -> dict:
    prompt = ChatPromptTemplate.from_template("Câu hỏi: {question}\nHãy trả lời:")
    chain = prompt | llm
    result = chain.invoke({"question": state["question"]})
    return {"answer": result.content, "iterations": state.get("iterations", 0) + 1}

# Node đánh giá câu trả lời
def critique_answer(state: CritiqueState) -> dict:
    prompt = ChatPromptTemplate.from_template(
        "Câu hỏi: {question}\nCâu trả lời: {answer}\n"
        "Hãy đánh giá câu trả lời trên và chỉ ra những thiếu sót:"
    )
    chain = prompt | llm
    result = chain.invoke({"question": state["question"], "answer": state["answer"]})
    return {"critique": result.content}

# Node cải thiện câu trả lời
def improve_answer(state: CritiqueState) -> dict:
    prompt = ChatPromptTemplate.from_template(
        "Câu hỏi: {question}\nCâu trả lời ban đầu: {answer}\n"
        "Đánh giá: {critique}\n"
        "Hãy cải thiện câu trả lời dựa trên đánh giá:"
    )
    chain = prompt | llm
    result = chain.invoke({
        "question": state["question"],
        "answer": state["answer"],
        "critique": state["critique"]
    })
    return {"final_answer": result.content}

# Quyết định có tiếp tục vòng lặp không
def should_continue(state: CritiqueState) -> str:
    if state["iterations"] >= 3:
        return "finish"
    if "không có thiếu sót" in state["critique"].lower():
        return "finish"
    return "continue"

# Khởi tạo đồ thị
critique_graph = StateGraph(CritiqueState)
critique_graph.add_node("generate", generate_answer)
critique_graph.add_node("critique", critique_answer)
critique_graph.add_node("improve", improve_answer)

# Kết nối các node
critique_graph.add_edge("generate", "critique")
critique_graph.add_edge("critique", "improve")

# Thêm cạnh có điều kiện
critique_graph.add_conditional_edges(
    "improve",
    should_continue,
    {
        "continue": "generate",  # Quay lại tạo câu trả lời mới
        "finish": END  # Kết thúc
    }
)

critique_graph.set_entry_point("generate")
```

### 7.2 Hệ thống thu thập thông tin (Information Gathering)

```python
from langgraph.graph import StateGraph
from typing import TypedDict, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

class InfoGatheringState(TypedDict):
    user_query: str
    collected_info: List[str]
    missing_info: List[str]
    follow_up_question: str
    user_response: str
    final_answer: str

# Khởi tạo LLM
llm = ChatOpenAI(temperature=0)

# Node phân tích yêu cầu và xác định thông tin cần thiết
def analyze_query(state: InfoGatheringState) -> dict:
    prompt = ChatPromptTemplate.from_template(
        "Yêu cầu: {user_query}\n"
        "Hãy xác định những thông tin cần thiết để trả lời yêu cầu này một cách đầy đủ. "
        "Trả về danh sách các mục thông tin cần thu thập."
    )
    chain = prompt | llm
    result = chain.invoke({"user_query": state["user_query"]})
    
    # Phân tích kết quả để lấy danh sách thông tin cần thu thập
    info_items = [item.strip() for item in result.content.split("\n") if item.strip()]
    
    return {
        "collected_info": state.get("collected_info", []),
        "missing_info": info_items
    }

# Node tạo câu hỏi tiếp theo
def generate_follow_up(state: InfoGatheringState) -> dict:
    if not state["missing_info"]:
        return {"follow_up_question": ""}
    
    next_info = state["missing_info"][0]
    prompt = ChatPromptTemplate.from_template(
        "Tôi cần hỏi người dùng về: {info_item}\n"
        "Hãy tạo một câu hỏi lịch sự và rõ ràng để thu thập thông tin này."
    )
    chain = prompt | llm
    result = chain.invoke({"info_item": next_info})
    
    return {"follow_up_question": result.content}

# Node xử lý phản hồi và cập nhật thông tin
def process_response(state: InfoGatheringState) -> dict:
    if not state["user_response"]:
        return {}
    
    if not state["missing_info"]:
        return {}
    
    # Thêm thông tin mới vào collected_info
    collected = state["collected_info"].copy()
    current_item = state["missing_info"][0]
    collected.append(f"{current_item}: {state['user_response']}")
    
    # Cập nhật missing_info
    missing = state["missing_info"][1:]
    
    return {
        "collected_info": collected,
        "missing_info": missing,
        "user_response": ""  # Xóa phản hồi cũ
    }

# Node tạo câu trả lời cuối cùng
def generate_final_answer(state: InfoGatheringState) -> dict:
    prompt = ChatPromptTemplate.from_template(
        "Yêu cầu ban đầu: {user_query}\n"
        "Thông tin đã thu thập:\n{collected_info}\n\n"
        "Dựa trên thông tin trên, hãy tạo câu trả lời đầy đủ và chính xác."
    )
    
    info_text = "\n".join(state["collected_info"])
    chain = prompt | llm
    result = chain.invoke({
        "user_query": state["user_query"],
        "collected_info": info_text
    })
    
    return {"final_answer": result.content}

# Quyết định nên làm gì tiếp theo
def decide_next_step(state: InfoGatheringState) -> str:
    if not state["missing_info"]:
        return "final"
    return "continue"

# Khởi tạo đồ thị
info_graph = StateGraph(InfoGatheringState)
info_graph.add_node("analyze", analyze_query)
info_graph.add_node("ask", generate_follow_up)
info_graph.add_node("process", process_response)
info_graph.add_node("finalize", generate_final_answer)

# Thêm cạnh
info_graph.add_edge("analyze", "ask")
info_graph.add_edge("ask", "process")

# Thêm cạnh có điều kiện
info_graph.add_conditional_edges(
    "process",
    decide_next_step,
    {
        "continue": "ask",
        "final": "finalize"
    }
)

info_graph.set_entry_point("analyze")
info_graph.set_finish_point("finalize")
```

## 8. Best Practices

### 8.1 Thiết kế đồ thị hiệu quả

1. **Chia nhỏ các chức năng**: Mỗi node nên thực hiện một chức năng cụ thể
2. **Tránh vòng lặp vô hạn**: Luôn có điều kiện thoát cho các chu kỳ
3. **Quản lý trạng thái cẩn thận**: Đảm bảo trạng thái được cập nhật nhất quán

```python
# ✓ Phân chia logic thành các node riêng biệt
def validate_input(state): ...
def process_data(state): ...
def format_output(state): ...

# ✗ Không kết hợp nhiều chức năng vào một node
def do_everything(state): ...
```

### 8.2 Xử lý lỗi

1. **Bắt lỗi trong mỗi node**: Tránh crash toàn bộ đồ thị
2. **Tạo luồng xử lý lỗi riêng**: Có các node chuyên xử lý lỗi
3. **Logging đầy đủ**: Ghi lại thông tin lỗi để debug

```python
def safe_node(state):
    try:
        # Thực hiện xử lý
        return {"result": process_data(state["input"])}
    except Exception as e:
        # Ghi log và trả về lỗi
        logging.error(f"Lỗi trong safe_node: {str(e)}")
        return {"error": str(e)}
```

### 8.3 Tối ưu hiệu suất

1. **Tránh tính toán trùng lặp**: Lưu kết quả trung gian vào state
2. **Xử lý bất đồng bộ**: Sử dụng async cho các tác vụ I/O
3. **Phân chia công việc lớn**: Chia nhỏ thành nhiều node

```python
# Sử dụng bất đồng bộ cho các tác vụ I/O
async def fetch_data(state):
    async with aiohttp.ClientSession() as session:
        async with session.get(state["url"]) as response:
            data = await response.json()
            return {"fetched_data": data}
```

### 8.4 Testing

1. **Unit test cho từng node**: Kiểm tra riêng từng chức năng
2. **Integration test**: Kiểm tra luồng hoàn chỉnh
3. **Mô phỏng các điều kiện lỗi**: Đảm bảo xử lý lỗi hoạt động đúng

```python
# Unit test cho một node
def test_process_node():
    state = {"input": "test data"}
    result = process_node(state)
    assert "output" in result
    assert result["output"] == "PROCESSED: test data"

# Integration test
def test_full_graph():
    graph = create_test_graph()
    app = graph.compile()
    result = app.invoke