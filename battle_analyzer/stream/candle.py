import sys


class Candle:
    def __init__(self, start_date, end_date, value_limit=2):
        self._start_date = start_date
        self._end_date = end_date
        self._values = []
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