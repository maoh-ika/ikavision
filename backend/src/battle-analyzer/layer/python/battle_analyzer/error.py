from enum import Enum

class ErrorCode(Enum):
    INVALID_OPERATION_ERROR_CODE = 0
    INVALID_PARAMETER_ERROR_CODE = 1
    ITEM_NOT_FOUND_ERROR_CODE = 2
    INVALID_KEY_ERROR_CODE = 3
    UNKNONW_FILE_FORMAT_ERROR = 4
    SEND_REQUEST_ERROR = 5
    INTERNAL_ERROR = 500

class AnalyzerError(Exception):
    def __init__(self, msg: str, code: ErrorCode) -> None:
        super().__init__(msg)
        self.msg = msg
        self.code = code

class InternalError(AnalyzerError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg, ErrorCode.INTERNAL_ERROR)

INVALID_OPERATION_ERROR = AnalyzerError(
    msg='operation not allowed',
    code=ErrorCode.INVALID_OPERATION_ERROR_CODE
)

INVALID_PARAMETER_ERROR = AnalyzerError(
    msg='invalid parameters',
    code=ErrorCode.INVALID_PARAMETER_ERROR_CODE
)

ITEM_NOT_FOUND_ERROR = AnalyzerError(
    msg='item not found',
    code=ErrorCode.ITEM_NOT_FOUND_ERROR_CODE
)

INVALID_KEY_ERROR = AnalyzerError(
    msg='invalid object key',
    code=ErrorCode.INVALID_KEY_ERROR_CODE
)

UNKNONW_FILE_FORMAT_ERROR = AnalyzerError(
    msg='unknown file format',
    code=ErrorCode.UNKNONW_FILE_FORMAT_ERROR
)

SEND_REQUEST_ERROR = AnalyzerError(
    msg='failed to send request',
    code=ErrorCode.SEND_REQUEST_ERROR
)