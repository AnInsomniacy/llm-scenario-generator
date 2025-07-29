import chromadb


def query_snippets(query_text, category=None, n_results=3):
    client = chromadb.PersistentClient(path="scenic_codebase")
    collection = client.get_collection("scenario_snippets")

    where_filter = {"type": category} if category else None

    results = collection.query(
        query_texts=[query_text],
        n_results=n_results,
        where=where_filter,
        include=["documents", "metadatas", "distances"]
    )

    return results


def display_results(results, query_desc="Query"):
    print(f"{query_desc}:")
    for i, (desc, meta, dist) in enumerate(
            zip(results['documents'][0], results['metadatas'][0], results['distances'][0])):
        print(f"{i + 1}. UID: {meta['uid']} | Distance: {dist:.3f}")
        print(f"   Description: {desc}")
        print(f"   Code: {meta['code']}")
        print()


def main():
    results = query_snippets("vehicle lane change", "behavior", 2)
    display_results(results, "Vehicle behavior search")


if __name__ == "__main__":
    main()
