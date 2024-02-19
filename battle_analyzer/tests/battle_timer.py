from battle_analyzer import BattleAnalysisResult, BattlePreprocessResult

class BattleTimer:
    def __init__(self, preprocess_result: BattlePreprocessResult,  result: BattleAnalysisResult) -> None:
        self.frame_rate = preprocess_result.frame_rate
        self.movie_frames = preprocess_result.movie_frames
        self.battle_open_frame = result.battle_info.battle_open_frame
        self.battle_end_frame = result.battle_info.battle_end_frame
        self.movie_seconds = preprocess_result.movie_frames / preprocess_result.frame_rate
        self.battle_seconds = self.frame_to_battle_second(self.battle_end_frame) - self.frame_to_battle_second(self.battle_open_frame)
        self.battle_open_second = self.frame_to_movie_second(self.battle_open_frame)
        self.battle_end_second = self.frame_to_movie_second(self.battle_end_frame)

    def movie_second_to_battle_second(self, movie_time: float) -> float:
        return movie_time - self.battle_open_second
    
    def battle_second_to_movie_Second(self, battle_time: float) -> float:
        return battle_time + self.battle_open_second
    
    def frame_to_movie_second(self, frame: float) -> float:
        return frame / self.frame_rate
    
    def frame_to_battle_second(self, frame: float) -> float:
        return (frame - self.battle_open_frame) / self.frame_rate
    
    def movie_time_to_movie_frame(self, movie_time: float) -> float:
        return self.movieFrames * (movie_time / self.movie_seconds)
