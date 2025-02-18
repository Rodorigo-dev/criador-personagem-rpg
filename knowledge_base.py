from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from config import CAPITULOS, KNOWLEDGE_BASE_PATH, PDF_PATH, KEYWORD_MAPPING
import os
import tiktoken

class DnDKnowledgeBase:
    def __init__(self, llm):
        self.llm = llm
        self.vector_store = self._load_or_create_vectorstore()
    
    def _load_or_create_vectorstore(self):
        if os.path.exists(KNOWLEDGE_BASE_PATH):
            print("Carregando base de conhecimento existente...")
            embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
            return FAISS.load_local(KNOWLEDGE_BASE_PATH, embeddings, allow_dangerous_deserialization=True)
        
        return self._create_vectorstore()
    
    def _create_vectorstore(self):
        print("Criando nova base de conhecimento...")
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        todos_documentos = []
        # largeembeddings / smalltextembeddings
        loader = PyPDFLoader(PDF_PATH)
        paginas = loader.load()
        
        for capitulo_id, info in CAPITULOS.items():
            print(f"Processando capítulo: {info['name']}...")
            
            paginas_capitulo = [
                p for p in paginas 
                if info['start'] <= int(p.metadata.get('page', 0)) <= info['end']
            ]
            
            for pagina in paginas_capitulo:
                pagina.metadata['chapter'] = info['name']
                pagina.metadata['chapter_id'] = capitulo_id
            
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=2000,
                chunk_overlap=200,
                length_function=len,
                separators=["\n\n\n", "\n\n", "\n", ". ", " ", ""]
            )
            chunks = text_splitter.split_documents(paginas_capitulo)
            todos_documentos.extend(chunks)
        
        vectorstore = FAISS.from_documents(todos_documentos, embeddings)
        vectorstore.save_local(KNOWLEDGE_BASE_PATH)
        return vectorstore
    
    def get_chapter_for_query(self, query: str) -> str:
        query_lower = query.lower()
        for chapter, keywords in KEYWORD_MAPPING.items():
            if any(keyword in query_lower for keyword in keywords):
                return CAPITULOS[chapter]['name']
        return None
    
    def query(self, query: str) -> dict:
        capitulo = self.get_chapter_for_query(query)
        search_kwargs = {"k": 5}
        
        if capitulo:
            search_kwargs["filter"] = {"chapter": capitulo}
        
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs=search_kwargs
            ),
            return_source_documents=True
        )
        
        resultado = qa_chain.invoke({"query": query})
        
        # Conta tokens
        encoding = tiktoken.encoding_for_model("gpt-4o-mini")
        tokens_entrada = len(encoding.encode(query))
        tokens_documentos = sum(len(encoding.encode(doc.page_content)) for doc in resultado["source_documents"])
        tokens_saida = len(encoding.encode(resultado["result"]))
        # checar função de uso de tokens langchain - openaicallback
        return {
            "resposta": resultado["result"],
            "documentos": resultado["source_documents"],
            "tokens": {
                "entrada": tokens_entrada,
                "documentos": tokens_documentos,
                "saida": tokens_saida,
                "total": tokens_entrada + tokens_documentos + tokens_saida
            }
        } 