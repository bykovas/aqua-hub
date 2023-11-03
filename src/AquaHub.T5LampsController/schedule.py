from datetime import datetime, timedelta
import random

class Schedule:
    _demoModeExpireTime = None

    @staticmethod
    def get_current_values():
        result = [0] * 2
        result[0] = random.randint(20, 90)
        result[1] = random.randint(20, 90)

        return result

    @staticmethod
    def set_demo_mode():
        Schedule._demoModeExpireTime = datetime.now() + timedelta(seconds=30)

    @staticmethod
    def is_demo_mode():
        if Schedule._demoModeExpireTime is None:
            return False
        return Schedule._demoModeExpireTime > datetime.now()
