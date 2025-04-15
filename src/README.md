# Simple LangGraph Chatbot

Đây là một chatbot đơn giản sử dụng LangGraph để xử lý hội thoại. Tất cả logic được chứa trong một file duy nhất để dễ hiểu và dễ sử dụng.

## Cài đặt

1. Cài đặt các dependencies:
```bash
pip install -r requirements.txt
```

2. Đặt biến môi trường OPENAI_API_KEY:
```bash
# Trên Unix/macOS
export OPENAI_API_KEY=your_api_key_here

# Trên Windows
set OPENAI_API_KEY=your_api_key_here
```

## Chạy ứng dụng

```bash
python chatbot.py
```

## Cách hoạt động

Chatbot này sử dụng LangGraph để xử lý luồng hội thoại. Cấu trúc graph đơn giản như sau:

1. Node `process_message`: Xử lý tin nhắn từ người dùng và trả về phản hồi từ model.
2. Node `should_continue`: Quyết định có tiếp tục hội thoại hay không.

Luồng xử lý:
- Người dùng nhập tin nhắn
- Node `process_message` xử lý tin nhắn và trả về phản hồi
- Node `should_continue` kiểm tra xem có tiếp tục hội thoại hay không
- Nếu tiếp tục, quay lại node `process_message`
- Nếu kết thúc, kết thúc hội thoại

## Mở rộng

Bạn có thể mở rộng chatbot này bằng cách:
1. Thêm các node mới để xử lý các tác vụ chuyên biệt
2. Thay đổi prompt để thay đổi hành vi của model
3. Thêm các công cụ (tools) để model có thể thực hiện các hành động cụ thể 