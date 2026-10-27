# chatbot_rag.py
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from langchain_community.document_loaders import DirectoryLoader, CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_google_genai import ChatGoogleGenerativeAI
from pinecone import Pinecone

# ✅ Load env vars
load_dotenv()
os.environ["PINECONE_API_KEY"] = os.getenv("PINECONE_API_KEY")
os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")

app = FastAPI()

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in production, replace "*" with frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Init pipeline once at startup
# -------------------------
print("Loading embeddings + Pinecone index...")

# Use multilingual-e5-large → 1024-dim
embeddings = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-large")

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index_name = "doc-embeddings-e5"  # ✅ must match your already created index

# Attach to existing index instead of creating
vectorstore = PineconeVectorStore.from_existing_index(index_name=index_name, embedding=embeddings)

# Retriever
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})

# LLM
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0, google_api_key=os.getenv("GEMINI_API_KEY"))

# Prompt must include {context} so LangChain can stuff docs
qa_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an assistant for business and marketing insights. Use the provided context to answer."),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
    ("system", "Context:\n{context}")
])

question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

# Chat history store
store = {}
def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

conversational_rag_chain = RunnableWithMessageHistory(
    rag_chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer",
)

# -------------------------
# API Endpoint
# -------------------------
class Query(BaseModel):
    question: str
    session_id: str = "default"

@app.post("/chat")
async def chat(query: Query):
    try:
        response = conversational_rag_chain.invoke(
            {"input": query.question},
            config={"configurable": {"session_id": query.session_id}},
        )
        return {"answer": response["answer"]}
    except Exception as e:
        return {"error": str(e)}

# -------------------------
# Run server (for local dev)
# -------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("chatbot_rag:app", host="0.0.0.0", port=8000, reload=True)
