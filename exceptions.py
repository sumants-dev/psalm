class VectorCollectionNotFound(Exception):
    def __init__(self, collection_name: str):
        super().__init__(f"Vector Collection {collection_name} was not found.")