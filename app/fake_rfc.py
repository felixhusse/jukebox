import time
class SimpleMFRC522:

    def read(self):
        time.sleep(5)
        return "dummy_card_id", "dummy_card_value"

    def read_no_block(self):
        time.sleep(0.5)
        return None, None