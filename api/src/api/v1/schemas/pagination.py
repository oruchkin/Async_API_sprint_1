from fastapi import Query

class PaginatedParams:
    def __init__(
        self,
        page_number: int = Query(1, description="Page number [1, N]", ge=1),
        page_size: int = Query(10, description="Page size [1, 100]", ge=1, le=100)
    ):
        self.page_number = page_number
        self.page_size = page_size
