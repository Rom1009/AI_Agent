class AppError(Exception):

    status_code = 500
    error_code = "app_error"

    def __init__(self, message: str | None = None, *, details: dict | None = None):
        super().__init__(message)
        self.message = message or "An unexpected error occured"
        self.details = details or {}

class UserAlreadyExist(AppError):

    status_code = 409
    error_code = "user_already_exists"