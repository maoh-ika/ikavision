from enum import Enum

class ErrorCode(Enum):
    BATTLE_OPEN_NOT_FOUND = 100
    BATTLE_END_NOT_FOUND = 101
    BATTLE_RESULT_NOT_FOUND = 102
    NO_BATTLE = 103
    INVALID_BATTLE = 104
    INVALID_PARAMS = 400
    INTERNAL_ERROR = 500

class AnalyzerError(Exception):
    def __init__(self, msg: str, code: ErrorCode) -> None:
        super().__init__(msg)
        self.msg = msg
        self.code = code

class InternalError(AnalyzerError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg, ErrorCode.INTERNAL_ERROR)

BATTLE_OPEN_NOT_FOUND_ERROR = AnalyzerError(
    msg='BATTLE_OPEN_NOT_FOUND',
    code=ErrorCode.BATTLE_OPEN_NOT_FOUND
)

BATTLE_END_NOT_FOUND_ERROR = AnalyzerError(
    msg='BATTLE_END_NOT_FOUND',
    code=ErrorCode.BATTLE_END_NOT_FOUND
)

BATTLE_RESULT_NOT_FOUND_ERROR = AnalyzerError(
    msg='BATTLE_RESULT_NOT_FOUND',
    code=ErrorCode.BATTLE_RESULT_NOT_FOUND
)

INVALID_BATTLE_ERROR = AnalyzerError(
    msg='INVALID_BATTLE',
    code=ErrorCode.INVALID_BATTLE
)

NO_BATTLE_ERROR = AnalyzerError(
    msg='NO_BATTLE',
    code=ErrorCode.NO_BATTLE
)

INVALID_PARAMS_ERROR = AnalyzerError(
    msg='INVALID_PARAMS',
    code=ErrorCode.INVALID_PARAMS
)