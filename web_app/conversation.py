from haystack import Document
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.document_stores.in_memory import InMemoryDocumentStore
from data_pipeline import fetch_research_papers
from itertools import chain
from typing import Any
from haystack.dataclasses import ChatMessage
from haystack import component
from haystack.core.component.types import Variadic
from haystack_experimental.chat_message_stores.in_memory import InMemoryChatMessageStore
from haystack_experimental.components.retrievers import ChatMessageRetriever
from haystack_experimental.components.writers import ChatMessageWriter
from typing import List
from haystack import Pipeline
from haystack.components.builders import ChatPromptBuilder, PromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.components.generators import OpenAIGenerator
from haystack.components.converters import OutputAdapter

def initialize_chatbot(user_subject : str, no_papers : int) -> tuple[Pipeline, ChatMessage, ChatMessage]:
    dataset = fetch_research_papers(user_subject, max_results=no_papers)


    dataset = [
        {"content" : document.summary,
        "meta" : {
            "title" : document.title,
            "published" : document.published,
            "author" : document.author,
            "category" : document.arxiv_primary_category["term"],
            }
        }  
        for document in dataset
    ]


    docs = [Document(content=doc["content"], meta=doc["meta"]) for doc in dataset]

    document_store = InMemoryDocumentStore()
    document_store.write_documents(documents=docs)

    

    # Memory components
    memory_store = InMemoryChatMessageStore()
    memory_retriever = ChatMessageRetriever(memory_store)
    memory_writer = ChatMessageWriter(memory_store)
    system_message = ChatMessage.from_system("You are a helpful AI assistant using provided supporting documents and conversation history to assist humans")

    user_message_template ="""Given the conversation history and the provided supporting documents, give a brief answer to the question.
    Note that supporting documents are not part of the conversation. If question can't be answered from supporting documents, say so.

        Conversation history:
        {% for memory in memories %}
            {{ memory.text }}
        {% endfor %}

        Supporting documents:
        {% for doc in documents %}
            {{ doc.content }}
        {% endfor %}

        \nQuestion: {{query}}
        \nAnswer:
    """
    user_message = ChatMessage.from_user(user_message_template)



    @component
    class ListJoiner:
        def __init__(self, _type: Any):
            component.set_output_types(self, values=_type)

        def run(self, values: Variadic[Any]):
            result = list(chain(*values))
            return {"values": result}
        
    query_rephrase_template = """
            Rewrite the question for search while keeping its meaning and key terms intact.
            If the conversation history is empty, DO NOT change the query.
            Use conversation history only if necessary, and avoid extending the query with your own knowledge.
            If no changes are needed, output the current question as is.

            Conversation history:
            {% for memory in memories %}
                {{ memory.text }}
            {% endfor %}

            User Query: {{query}}
            Rewritten Query:
    """



    conversational_rag = Pipeline()

    # components for query rephrasing
    conversational_rag.add_component("query_rephrase_prompt_builder", PromptBuilder(query_rephrase_template))
    conversational_rag.add_component("query_rephrase_llm", OpenAIGenerator())
    conversational_rag.add_component("list_to_str_adapter", OutputAdapter(template="{{ replies[0] }}", output_type=str))

    # components for RAG
    conversational_rag.add_component("retriever", InMemoryBM25Retriever(document_store=document_store, top_k=3))
    conversational_rag.add_component("prompt_builder", ChatPromptBuilder(variables=["query", "documents", "memories"], required_variables=["query", "documents", "memories"]))
    conversational_rag.add_component("llm", OpenAIChatGenerator())

    # components for memory
    conversational_rag.add_component("memory_retriever", ChatMessageRetriever(memory_store))
    conversational_rag.add_component("memory_writer", ChatMessageWriter(memory_store))
    conversational_rag.add_component("memory_joiner", ListJoiner(List[ChatMessage]))

    # connections for query rephrasing
    conversational_rag.connect("memory_retriever", "query_rephrase_prompt_builder.memories")
    conversational_rag.connect("query_rephrase_prompt_builder.prompt", "query_rephrase_llm")
    conversational_rag.connect("query_rephrase_llm.replies", "list_to_str_adapter")
    conversational_rag.connect("list_to_str_adapter", "retriever.query")

    # connections for RAG
    conversational_rag.connect("retriever.documents", "prompt_builder.documents")
    conversational_rag.connect("prompt_builder.prompt", "llm.messages")
    conversational_rag.connect("llm.replies", "memory_joiner")

    # connections for memory
    conversational_rag.connect("memory_joiner", "memory_writer")
    conversational_rag.connect("memory_retriever", "prompt_builder.memories")
    
    
    return conversational_rag, system_message, user_message

'''
import os
from getpass import getpass

if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = getpass("Enter OpenAI API key:")

conversational_rag, system_message, user_message = initialize_chatbot("AI")

while True:
    messages = [system_message, user_message]
    question = input("Enter your question or Q to exit.\n🧑 ")
    if question=="Q":
        break

    res = conversational_rag.run(data={"query_rephrase_prompt_builder": {"query": question},
                             "prompt_builder": {"template": messages, "query": question},
                             "memory_joiner": {"values": [ChatMessage.from_user(question)]}},
                            include_outputs_from=["llm","query_rephrase_llm"])
    search_query = res['query_rephrase_llm']['replies'][0]
    print(f"   🔎 Search Query: {search_query}")
    assistant_resp = res['llm']['replies'][0]
    print(f"🤖 {assistant_resp.text}")
'''