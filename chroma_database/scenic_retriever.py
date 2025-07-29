"""
Retrieve code snippets from scenic codebase using semantic search

search_snippets(query_text, category=None, limit=3):
    query_text: natural language description to search
    category: filter by type ('behavior', 'geometry', 'spawn') or None for all
    limit: maximum number of results to return
    returns: list of snippet dictionaries with uid, type, description, code, similarity

get_snippet_by_id(uid):
    uid: unique identifier of the snippet
    returns: snippet dictionary or None if not found
"""

import chromadb


def search_snippets(query_text, category=None, limit=3):
    client = chromadb.PersistentClient(path="scenic_codebase")
    collection = client.get_collection("scenario_snippets")

    where_filter = {"type": category} if category else None

    results = collection.query(
        query_texts=[query_text],
        n_results=limit,
        where=where_filter,
        include=["documents", "metadatas", "distances"]
    )

    snippets = []
    for desc, meta, dist in zip(results['documents'][0], results['metadatas'][0], results['distances'][0]):
        snippets.append({
            'uid': meta['uid'],
            'type': meta['type'],
            'description': desc,
            'code': meta['code'],
            'similarity': 1 - dist
        })

    return snippets


def get_snippet_by_id(uid):
    client = chromadb.PersistentClient(path="scenic_codebase")
    collection = client.get_collection("scenario_snippets")

    results = collection.get(
        ids=[uid],
        include=["documents", "metadatas"]
    )

    if results['documents']:
        return {
            'uid': uid,
            'type': results['metadatas'][0]['type'],
            'description': results['documents'][0],
            'code': results['metadatas'][0]['code']
        }
    return None


def main():
    results = search_snippets("vehicle changes lane", "behavior", 2)
    for snippet in results:
        print(f"UID: {snippet['uid']} | Similarity: {snippet['similarity']:.3f}")
        print(f"Description: {snippet['description']}")
        print(f"Code: {snippet['code']}...")
        print()


if __name__ == "__main__":
    main()
