from fastapi import HTTPException, status


class UnauthorizedException(HTTPException):
    def __init__(self, detail: str = "Unauthorized Page"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)

class ForbiddenException(HTTPException):
  def __init__(self):
    super().__init__(status.HTTP_403_FORBIDDEN, "Forbidden")

class NotFoundException(HTTPException):
  def __init__(self):
    super().__init__(status.HTTP_404_NOT_FOUND, "Not Found")