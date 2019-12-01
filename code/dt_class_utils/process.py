import signal
import sys

class DTProcess(object):

    def __init__(self):
        self.is_shutdown = False
        self.term_signal_received = False
        self._shutdown_cbs = []
        signal.signal(signal.SIGINT, self._on_SIGINT)

    def _on_SIGINT(self, sig, frame):
        if not self.term_signal_received:
            self.term_signal_received = True
            name = type(self).__name__
            print(f'[{name}]: Shutdown request received! Gracefully terminating....')
        self.shutdown()

    def shutdown(self):
        self.is_shutdown = True
        for cb in self._shutdown_cbs:
            cb()

    def register_shutdown_callback(self, cb):
        if callable(cb):
            self._shutdown_cbs.append(cb)
