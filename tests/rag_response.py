from services.rag_service import RagService

def test_rag_retrieval():
    rag_service = RagService()
    query = "Who is Prof. WHO?"
    context, score = rag_service.retrieve_with_rerank(query)
    
    print(f"\n[QUERY]: {query}")
    print(f"[RAG BEST MATCH SCORE]: {score}")
    print(f"[RAG CONTEXT]:\n{context}\n")
    
    assert context is not None
    assert "genius" in context.lower() or "creator" in context.lower()

if __name__ == "__main__":
    test_rag_retrieval()
