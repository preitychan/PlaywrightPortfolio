import os
import sys
from pathlib import Path
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

def build_rag_chain(readme_path: str = "README.md"):
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set.")
        sys.exit(1)

    file_path = Path(readme_path)
    if not file_path.exists():
        print(f"Error: Could not find '{readme_path}' in the current directory.")
        sys.exit(1)

    # 1. Read the README.md content
    markdown_text = file_path.read_text(encoding="utf-8")

    # 2. Split by Markdown headers first to preserve section context
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]
    md_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    md_header_splits = md_splitter.split_text(markdown_text)

    # 3. Further split large sections into smaller overlapping chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=100)
    chunks = text_splitter.split_documents(md_header_splits)

    # 4. Embed chunks and store in an in-memory FAISS vector store
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

    # 5. Set up the prompt and LLM
    template = """You are a helpful assistant answering questions about a GitHub project.
Use ONLY the following context from the project's README.md to answer the question.
If the answer is not in the context, say "I don't see that information in the README."

Context:
{context}

Question: {question}
"""
    prompt = ChatPromptTemplate.from_template(template)
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    # 6. Build the LCEL RAG chain
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return rag_chain

if __name__ == "__main__":
    print("Indexing README.md...")
    chain = build_rag_chain("README.md")
    print("Ready! Ask a question about your project (type 'exit' to quit).\n")

    while True:
        user_query = input("You: ").strip()
        if user_query.lower() in {"exit", "quit"}:
            break
        if not user_query:
            continue

        answer = chain.invoke(user_query)
        print(f"\nAssistant: {answer}\n")
