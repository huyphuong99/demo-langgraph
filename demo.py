from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Define the state type
class ChatState(TypedDict):
    question: str
    answer: str
    critique: str
    final_answer: str
    iterations: int

# Initialize LLM
llm = ChatOpenAI(temperature=0.7)

# Node to generate initial answer
def generate_answer(state: ChatState) -> dict:
    prompt = ChatPromptTemplate.from_template(
        "Question: {question}\nPlease provide a detailed answer:"
    )
    chain = prompt | llm
    result = chain.invoke({"question": state["question"]})
    return {
        "answer": result.content,
        "iterations": state.get("iterations", 0) + 1
    }

# Node to critique the answer
def critique_answer(state: ChatState) -> dict:
    prompt = ChatPromptTemplate.from_template(
        "Question: {question}\nAnswer: {answer}\n"
        "Please critique this answer and identify any gaps or areas for improvement:"
    )
    chain = prompt | llm
    result = chain.invoke({
        "question": state["question"],
        "answer": state["answer"]
    })
    return {"critique": result.content}

# Node to improve the answer
def improve_answer(state: ChatState) -> dict:
    prompt = ChatPromptTemplate.from_template(
        "Question: {question}\nOriginal Answer: {answer}\n"
        "Critique: {critique}\n"
        "Please provide an improved answer based on the critique:"
    )
    chain = prompt | llm
    result = chain.invoke({
        "question": state["question"],
        "answer": state["answer"],
        "critique": state["critique"]
    })
    return {"final_answer": result.content}

# Function to decide whether to continue or finish
def should_continue(state: ChatState) -> str:
    if state["iterations"] >= 3:
        return "finish"
    if "no significant issues" in state["critique"].lower():
        return "finish"
    return "continue"

# Create the graph
chat_graph = StateGraph(ChatState)

# Add nodes
chat_graph.add_node("generate", generate_answer)
chat_graph.add_node("critique", critique_answer)
chat_graph.add_node("improve", improve_answer)

# Add edges
chat_graph.add_edge("generate", "critique")
chat_graph.add_edge("critique", "improve")

# Add conditional edges
chat_graph.add_conditional_edges(
    "improve",
    should_continue,
    {
        "continue": "generate",
        "finish": END
    }
)

# Set entry point
chat_graph.set_entry_point("generate")

# Compile the graph
chat_app = chat_graph.compile()

def main():
    # Example usage
    question = "What are the key benefits of using LangGraph?"
    
    # Initialize state
    initial_state = {
        "question": question,
        "answer": "",
        "critique": "",
        "final_answer": "",
        "iterations": 0
    }
    
    # Run the graph
    result = chat_app.invoke(initial_state)
    
    # Print results
    print("\n=== Final Results ===")
    print(f"Question: {result['question']}")
    print(f"\nFinal Answer: {result['final_answer']}")
    print(f"\nNumber of iterations: {result['iterations']}")

if __name__ == "__main__":
    main() 