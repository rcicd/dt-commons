import signal
import sys

class DTProcess(object):

    def __init__(self):
        self.is_shutdown = False
        self.term_signal_received = False
        signal.signal(signal.SIGINT, self._on_SIGINT)

    def _on_SIGINT(self, sig, frame):
        if not self.term_signal_received:
            self.term_signal_received = True
            print('Shutdown request received! Gracefully terminating....')
        self.shutdown()

    def shutdown(self):
        self.is_shutdown = True
