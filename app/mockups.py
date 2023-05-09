import random
import time
class SimpleMFRC522:

    READER = None

    id_list = ("444", "123", None, None, None)

    def __init__(self):
        self.READER = MFRC522()

    def read(self):
        time.sleep(5)
        return random.randint(1, 10), "random"

    def read_id_no_block(self):
        time.sleep(0.5)
        return random.choice(self.id_list)

class GPIO:

    @staticmethod
    def cleanup():
        print("Clean UP")

class MFRC522:
    def Close_MFRC522(self):
        print("Cleanup called")