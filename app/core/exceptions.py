from fastapi import HTTPException, status


class CredentialsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


class ItemNotFoundException(HTTPException):
    def __init__(self, item_name: str = "Item"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"{item_name} not found"
        )


class AIProcessingException(HTTPException):
    def __init__(self, detail: str = "AI Model failed to process the request"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail
        )
