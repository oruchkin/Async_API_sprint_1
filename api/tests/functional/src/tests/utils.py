def construct_es_documents(index: str, entities: list[dict]) -> list[dict]:
    bulk_query: list[dict] = []
    for row in entities:
        data = {"_index": index, "_id": row["id"], "_source": row}
        bulk_query.append(data)

    return bulk_query
