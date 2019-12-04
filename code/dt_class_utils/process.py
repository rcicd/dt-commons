import os
import sys
import logging
import signal

class DTProcess(object):

    def __init__(self):
        self.is_shutdown = False
        self.term_signal_received = False
        self.app_name = type(self).__name__
        self._shutdown_cbs = []
        signal.signal(signal.SIGINT, self._on_SIGINT)
        # define logger
        logging.basicConfig()
        self.logger = logging.getLogger(self.app_name)
        self.logger.setLevel(logging.INFO)
        if 'DEBUG' in os.environ and bool(os.environ['DEBUG']):
            self.logger.setLevel(logging.DEBUG)

    def _on_SIGINT(self, sig, frame):
        if not self.term_signal_received:
            self.term_signal_received = True
            self.logger.info('Shutdown request received! Gracefully terminating....')
        self.shutdown()

    def shutdown(self):
        self.is_shutdown = True
        for cb in self._shutdown_cbs:
            cb()

    def register_shutdown_callback(self, cb):
        if callable(cb):
            self._shutdown_cbs.append(cb)
