import random
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory

from app.services import llm
from app.retrieval import vectorstore
from app.chat import get_session_history

TUTOR_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a Socratic AI Tutor. Your goal is to help the student master the topic: {topic}.

RULES:
1. Ask ONE multiple-choice question at a time.
2. Wait for the user's answer.
3. If they answer correctly: Praise them briefly, explain WHY it's correct options, then ask the NEXT question.
4. If they answer incorrectly: Gently explain why it's wrong, give a hint, and let them try again.
5. If they ask a question: Answer it like a teacher, then gently steer back to the quiz.
6. Use the provided context to form your questions.
7. Be encouraging and proactive. If they seem stuck, offer to simplify.

Context:
{context}"""),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])

def create_tutor_chain(topic: str):
    """Creates a conversational chain for the Tutor Mode."""
    if not vectorstore:
        return None
        
    # Retrieve & Shuffle for variety
    docs = vectorstore.similarity_search(topic, k=20)
    random.shuffle(docs)
    docs = docs[:8]
    
    context_str = "\n\n".join([d.page_content for d in docs])
    
    partial_prompt = TUTOR_PROMPT.partial(topic=topic, context=context_str)
    chain = partial_prompt | llm
    
    return RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
    )
