import signal
import sys

class DTProcess(object):

    def __init__(self):
        self.is_shutdown = False
        signal.signal(signal.SIGINT, self._on_SIGINT)

    def _on_SIGINT(self, sig, frame):
        print('Shutdown request received! Gracefully terminating....')
        self.is_shutdown = True
