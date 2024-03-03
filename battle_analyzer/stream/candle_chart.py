from dataclasses import dataclass

@dataclass
class CandleValue:
    timestamp: int
    value: float

class Candle:
    def __init__(self, start_date, end_date, value_limit=2):
        self._start_date = start_date
        self._end_date = end_date
        self._values: list[CandleValue] = []
        self.value_limit = value_limit

    def add_value(self, value):
        if value.timestamp < self._start_date or self._end_date < value.timestamp:
            return False

        if value in self._values:
            return False

        self._values.append(value)
        if self.value_count > self.value_limit:
            self._values.pop(0)
        return True

    @property
    def values(self):
        return self._values

    @property
    def value_count(self):
        return len(self._values)

    @property
    def start_date(self):
        return self._start_date

    @property
    def end_date(self):
        return self._end_date

    @property
    def is_empty(self):
        return len(self._values) == 0

    @property
    def open_value(self):
        if self.is_empty:
            return None
        return self._values[0]

    @property
    def last_value(self):
        if self.is_empty:
            return None
        return self._values[-1]

    @property
    def high_value(self):
        if self.is_empty:
            return None
        return max(self._values, key=lambda p: p.value)
    
    @property
    def low_value(self):
        if self.is_empty:
            return None
        return min(self._values, key=lambda p: p.value)

    @property
    def average(self):
        if self.value_count == 0:
            return 0.0
        return sum(map(lambda p: p.value, self._values)) / self.value_count

    @property
    def sum(self):
        if self.value_count == 0:
            return 0.0
        return sum([v.value for v in self._values])

    @property
    def is_positive(self):
        if self.open_value is None or self.last_value is None:
            return False
        return self.open_value.value < self.last_value.value

    @property
    def is_negative(self):
        if self.open_value is None or self.last_value is None:
            return False
        return self.last_value.value < self.open_value.value

    def find_values(self, start_date, end_date):
        return [v for v in self._values if start_date <= v.timestamp and v.timestamp <= end_date]

    def to_dict(self):
        return {
            'start_date': self.start_date,
            'end_date': self.end_date,
            'values': [{ 'value': v.value, 'timestamp': v.timestamp } for v in self.values]
        }

class CandleChart:
    def __init__(self, candle_count=30, candle_period=3000, fill_with_blank=True, is_fixed_period=True):
        self._candle_count = candle_count
        self._candle_period = candle_period
        self._fill_with_blank = fill_with_blank
        self._is_fixed_period = is_fixed_period
        self._candles = []

    @property
    def candles(self):
        return self._candles

    @property
    def first_candle(self):
        if self.is_empty:
            return None
        return self._candles[0]

    @property
    def last_candle(self):
        if self.is_empty:
            return None
        return self._candles[-1]

    @property
    def prev_candle(self):
        if len(self._candles) < 2:
            return None
        return self._candles[-2]

    @property
    def candle_count(self):
        return len(self._candles)

    @property
    def max_candle_count(self):
        return self._candle_count

    @property
    def period(self):
        return self._candle_period

    @property
    def is_empty(self):
        return len(self._candles) == 0

    @property
    def is_filled(self):
        return self._candle_count <= self.candle_count

    def get_candle(self, index):
        if len(self._candles) <= index or index < -len(self._candles):
            return None
        return self._candles[index]
   
    def get_last_candles(self, count):
        return self._candles[-count:]

    def find_candles(self, start_date, end_date):
        return [c for c in self._candles if (
           start_date <= c.end_date and c.start_date <= end_date
        )]

    def find_values(self, start_date, end_date):
        values = []
        for c in self.find_candles(start_date, end_date):
            values += c.find_values(start_date, end_date)
        return values

    def add_value(self, value: CandleValue):
        if self.is_empty:
            candle = self._make_candle(value)
            self._candles.append(candle)
            return candle

        new_candle = None
        if value.timestamp < self.first_candle.start_date:
            new_candle = self.makeCandle(value)
            if self._fill_with_blank:
                blank_ticks = (abs(new_candle.end_date - self.first_candle.start_date)) // self._candle_period
                for i in range(blank_ticks):
                    blank = self._make_blank_candle_backward(self.candles[0])
                    self.candles.insert(0, blank)
            self.candles.insert(0, new_candle)
        elif self.last_candle.end_date < value.timestamp:
            # add new candle and fill blank periods
            new_candle = self._make_candle(value)
            if self._fill_with_blank:
                blank_count = (new_candle.start_date - self.last_candle.end_date) // self._candle_period
                for _ in range(blank_count):
                    blank = self._make_blank_candle_forward(self.candles[-1])
                    self._candles.append(blank)
            self._candles.append(new_candle)
        else:
            # update current candle
            for candle in reversed(self._candles):
                if candle.add_value(value):
                    break
        
        if 0 < self._candle_count:
            while self._candle_count < len(self._candles):
                self._candles.pop(0)
        
        return new_candle

    def clear(self):
        self._candles = []

    def _make_candle(self, value):
        period = self._calculate_candle_period(value.timestamp)
        candle = Candle(period[0], period[1])
        candle.add_value(value)
        return candle
    
    def _make_blank_candle_backward(self, next_candle: Candle) -> Candle:
        next_end = next_candle.start_date
        next_start = next_end - self._candle_period
        candle = Candle(next_start, next_end)
        return candle

    def _make_blank_candle_forward(self, prev_candle: Candle) -> Candle:
        next_start = prev_candle.end_date
        next_end = next_start + self._candle_period
        candle = Candle(next_start, next_end)
        return candle

    def _calculate_candle_period(self, timestamp):
        mod = timestamp % self._candle_period
        start_date = timestamp - mod
        end_date = start_date + self._candle_period
        return (start_date, end_date)
