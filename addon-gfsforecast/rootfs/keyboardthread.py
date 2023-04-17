import threading
from typing import Callable

class KeyboardThread(threading.Thread):

    def __init__(self, input_callback: Callable[[str], None], name: str = 'keyboard-input-thread'):
        self.input_callback = input_callback
        super(KeyboardThread, self).__init__(name=name, daemon=True)
        self.start()

    def run(self):
        while True:
            self.input_callback(input().replace('"', '')) #waits to get input + Return
