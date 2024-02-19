from enum import Enum
from prediction.frame import Frame

class TestResult(Enum):
    TARGET = 0
    NOT_TARGET = 1
    PENDING = 2

def find_target_frames(frames: list[Frame], is_target_frame, exit_test_frame_count: int, interval: int=1) -> (int, int):
    start_index = None
    end_index = None
    exit_frame_count = exit_test_frame_count
    for idx, frame in enumerate(frames):
        if idx % interval != 0:
            if start_index is not None:
                end_index = idx
            continue
        result = is_target_frame(frame, start_index is not None)
        if result == TestResult.TARGET:
            if start_index is None:
                start_index = idx
            else:
                end_index = idx
                exit_frame_count = exit_test_frame_count # reset count
        elif result == TestResult.NOT_TARGET:
            if start_index is not None:
                # count down for finidng opening end frame
                exit_frame_count -= 1
                if exit_frame_count <= 0:
                    break
        elif result == TestResult.PENDING:
            pass

    if start_index is not None and end_index is None:
        end_index = start_index # just 1 opening frame is included in the video
    return start_index, end_index

def taget_frames_generator(frames: list[Frame], is_target_frame, exit_test_frame_count: int, interval: int=1):
    length = len(frames)
    cur_pos = 0
    while cur_pos < length:
        start_idx, end_idx = find_target_frames(frames[cur_pos:], is_target_frame, exit_test_frame_count, interval)
        if start_idx is None and end_idx is None:
            break
        else:
            start_pos = start_idx + cur_pos
            end_pos = end_idx + cur_pos
            yield frames[start_pos:end_pos + 1], start_pos, end_pos
            cur_pos = end_pos + 1
#            frames = frames[cur_pos:]
