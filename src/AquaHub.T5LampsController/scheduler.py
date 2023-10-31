from datetime import datetime, timedelta
import random

class Scheduler:
    _demoModeExpireTime = None

    @staticmethod
    def get_current_values():
        result = [0] * 2
        result[0] = random.randint(1, 49)
        result[1] = random.randint(50, 100)

        return result

    @staticmethod
    def set_demo_mode():
        Scheduler._demoModeExpireTime = datetime.now() + timedelta(seconds=30)

    @staticmethod
    def is_demo_mode():
        if Scheduler._demoModeExpireTime is None:
            return False
        return Scheduler._demoModeExpireTime > datetime.now()
