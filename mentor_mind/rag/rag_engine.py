import os
import logging
from typing import List, Dict, Optional

log = logging.getLogger("MentorMind")

try:
    import chromadb
    from chromadb.utils import embedding_functions
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    log.warning("ChromaDB not available")

try:
    from pypdf import PdfReader
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    log.warning("pypdf not available")


class DocumentProcessor:
    """Documents ko process karo aur chunks banao."""

    def __init__(self, chunk_size=800, chunk_overlap=100):
        self.chunk_size    = chunk_size
        self.chunk_overlap = chunk_overlap

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        if not PDF_AVAILABLE:
            return "PDF support not available. Install pypdf."
        try:
            reader = PdfReader(pdf_path)
            text   = ""
            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text += "\n[Page " + str(page_num + 1) + "]\n" + page_text
            log.info("PDF extracted: " + str(len(text)) + " chars from " + str(len(reader.pages)) + " pages")
            return text
        except Exception as e:
            log.error("PDF extraction error: " + str(e))
            return "Error reading PDF: " + str(e)

    def extract_text_from_file(self, file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            return self.extract_text_from_pdf(file_path)
        elif ext in [".txt", ".md"]:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                return "Error reading file: " + str(e)
        else:
            return "Unsupported file type: " + ext

    def split_into_chunks(self, text: str) -> List[str]:
        if not text or len(text.strip()) == 0:
            return []

        chunks = []
        start  = 0
        text   = text.strip()

        while start < len(text):
            end = start + self.chunk_size
            if end < len(text):
                for sep in ["\n\n", "\n", ". ", " "]:
                    pos = text.rfind(sep, start, end)
                    if pos > start:
                        end = pos + len(sep)
                        break
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start = end - self.chunk_overlap

        log.info("Text split into " + str(len(chunks)) + " chunks")
        return chunks


class RAGEngine:
    """Complete RAG System."""

    COLLECTION_NAME = "mentor_mind_docs"

    def __init__(self, persist_dir="./chroma_db"):
        self.persist_dir = persist_dir
        self.processor   = DocumentProcessor()
        self.client      = None
        self.collection  = None
        self._setup()

    def _setup(self):
        if not CHROMA_AVAILABLE:
            log.error("ChromaDB not available!")
            return
        try:
            self.client = chromadb.PersistentClient(path=self.persist_dir)
            self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
            self.collection = self.client.get_or_create_collection(
                name=self.COLLECTION_NAME,
                embedding_function=self.embedding_fn,
                metadata={"description": "MENTOR MIND documents"}
            )
            log.info("ChromaDB ready. Documents: " + str(self.collection.count()))
        except Exception as e:
            log.error("ChromaDB setup failed: " + str(e))

    def add_document(self, text: str, doc_id: str, metadata: Dict = None) -> bool:
        if not self.collection:
            return False
        try:
            chunks = self.processor.split_into_chunks(text)
            if not chunks:
                log.warning("No chunks from document: " + doc_id)
                return False

            ids  = [doc_id + "_chunk_" + str(i) for i in range(len(chunks))]
            meta = metadata or {}
            metadatas = [
                {**meta, "doc_id": doc_id, "chunk_index": i}
                for i in range(len(chunks))
            ]

            self.collection.upsert(
                documents=chunks,
                ids=ids,
                metadatas=metadatas
            )
            log.info("Document added: " + doc_id + " (" + str(len(chunks)) + " chunks)")
            return True
        except Exception as e:
            log.error("Document add error: " + str(e))
            return False

    def add_file(self, file_path: str, session_id: str, topic: str = "") -> Dict:
        if not os.path.exists(file_path):
            return {"success": False, "message": "File not found"}

        text = self.processor.extract_text_from_file(file_path)
        if text.startswith("Error"):
            return {"success": False, "message": text}

        file_name = os.path.basename(file_path)
        doc_id    = session_id + "_" + file_name

        metadata = {
            "session_id": session_id,
            "file_name" : file_name,
            "topic"     : topic,
        }

        success = self.add_document(text, doc_id, metadata)

        if success:
            chunks = self.processor.split_into_chunks(text)
            return {
                "success"     : True,
                "message"     : file_name + " successfully uploaded!",
                "chunks_count": len(chunks),
                "doc_id"      : doc_id
            }
        return {"success": False, "message": "Document processing failed"}

    def search(self, query: str, session_id: str = None, n_results: int = 5) -> List[Dict]:
        if not self.collection:
            return []

        total_docs = self.collection.count()
        if total_docs == 0:
            return []

        try:
            where = {"session_id": session_id} if session_id else None
            results = self.collection.query(
                query_texts=[query],
                n_results=min(n_results, total_docs),
                where=where
            )

            formatted = []
            documents = results.get("documents", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]

            for doc, meta, dist in zip(documents, metadatas, distances):
                similarity = round((1 - dist) * 100, 1)
                formatted.append({
                    "text"      : doc,
                    "source"    : meta.get("file_name", "Unknown"),
                    "topic"     : meta.get("topic", ""),
                    "similarity": similarity
                })

            log.info("Search found " + str(len(formatted)) + " relevant chunks")
            return formatted
        except Exception as e:
            log.error("Search error: " + str(e))
            return []

    def list_documents(self, session_id: str) -> List[str]:
        if not self.collection:
            return []
        try:
            results = self.collection.get(where={"session_id": session_id})
            files = list(set([
                m.get("file_name", "Unknown")
                for m in results.get("metadatas", [])
            ]))
            return files
        except Exception:
            return []

    def delete_document(self, doc_id: str, session_id: str) -> bool:
        if not self.collection:
            return False
        try:
            results = self.collection.get(
                where={"session_id": session_id, "doc_id": doc_id}
            )
            ids = results.get("ids", [])
            if ids:
                self.collection.delete(ids=ids)
                return True
            return False
        except Exception as e:
            log.error("Delete error: " + str(e))
            return False
