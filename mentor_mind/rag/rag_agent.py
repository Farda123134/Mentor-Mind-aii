import logging
from mentor_mind.utils.ai_helper import call_ai
from .rag_engine import RAGEngine

log = logging.getLogger("MentorMind")


class RAGAgent:
    SYSTEM_PROMPT = """You are a document-based Q&A assistant for MENTOR MIND AI.

STRICT RULES:
1. Answer ONLY using the information provided in the document context below.
2. If the answer is not found in the document context, clearly say:
   "I could not find this information in your uploaded document."
   Do NOT make up or guess an answer.
3. Quote relevant lines from the document when helpful to support your answer.
4. Be specific - mention exact facts, numbers, or details found in the document.
5. If the document context is empty or irrelevant, say so honestly.
6. Keep your answer clear and under 300 words.

Format:
ANSWER: [your answer based strictly on the document]
SOURCE: [which part of the document this came from]"""

    GENERAL_PROMPT = """You are MENTOR MIND AI.
No relevant document was found for this question.
Answer helpfully from general knowledge and suggest
the user upload relevant notes for more accurate answers.
Max 300 words."""

    def __init__(self, memory, rag_engine: RAGEngine):
        self.memory     = memory
        self.rag_engine = rag_engine

    def answer_from_docs(self, question: str, session_id: str) -> str:
        self.memory.log("RAGAgent", "search", question[:50])

        results = self.rag_engine.search(question, session_id, n_results=5)

        if not results:
            log.info("No documents found for query: " + question[:50])
            general_answer = call_ai(self.GENERAL_PROMPT, question, max_tokens=400)
            return "No relevant information found in your uploaded documents.\n\n" + general_answer

        relevant_results = [r for r in results if r.get("similarity", 0) > 40]

        if not relevant_results:
            log.info("No sufficiently similar chunks found")
            general_answer = call_ai(self.GENERAL_PROMPT, question, max_tokens=400)
            return "Your documents don't seem to contain information about this. Here's a general answer:\n\n" + general_answer

        context_parts = ["DOCUMENT CONTEXT:\n"]
        for i, r in enumerate(relevant_results, 1):
            context_parts.append(
                "[Excerpt " + str(i) + " from " + r["source"] +
                " - " + str(r["similarity"]) + "% match]"
            )
            context_parts.append(r["text"])
            context_parts.append("")

        context = "\n".join(context_parts)
        full_prompt = "Question: " + question + "\n\n" + context

        log.info("Answering from " + str(len(relevant_results)) + " document chunks")
        return call_ai(self.SYSTEM_PROMPT, full_prompt, max_tokens=700)

    def get_document_list(self, session_id: str) -> str:
        docs = self.rag_engine.list_documents(session_id)
        if not docs:
            return "No documents uploaded yet."
        return "\n".join(["- " + d for d in docs])
