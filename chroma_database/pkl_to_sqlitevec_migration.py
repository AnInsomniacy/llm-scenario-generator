import pickle
import chromadb


def migrate_database(pkl_path, db_path):
    with open(pkl_path, 'rb') as f:
        database = pickle.load(f)

    client = chromadb.PersistentClient(path=db_path)
    collection = client.create_collection("scenario_snippets")

    descriptions = []
    metadatas = []
    ids = []

    for category in ['behavior', 'geometry', 'spawn']:
        desc_list = database[category]['description']
        code_list = database[category]['snippet']

        for i, (desc, code) in enumerate(zip(desc_list, code_list)):
            descriptions.append(desc)
            metadatas.append({
                'uid': f"{category}_{i:03d}",
                'type': category,
                'code': code
            })
            ids.append(f"{category}_{i:03d}")

    collection.add(
        documents=descriptions,
        metadatas=metadatas,
        ids=ids
    )


def main():
    pkl_path = "database_v1.pkl"
    db_path = "scenic_codebase"
    migrate_database(pkl_path, db_path)


if __name__ == "__main__":
    main()
