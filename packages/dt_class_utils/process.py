import os
import sys
import time
import logging
import signal

from .app_status import AppStatus


class DTProcess(object):

    def __init__(self, name=None):
        self._status = AppStatus.INITIALIZING
        self._sigint_counter = 0
        self._app_name = type(self).__name__ if not name else name
        self._shutdown_cbs = []
        signal.signal(signal.SIGINT, self._on_sigint)
        # define logger
        logging.basicConfig()
        self.logger = logging.getLogger(self._app_name)
        self.logger.setLevel(logging.INFO)
        if 'DEBUG' in os.environ and bool(os.environ['DEBUG']):
            self.logger.setLevel(logging.DEBUG)
        self._start_time = time.time()
        self._status = AppStatus.RUNNING

    def start_time(self):
        return self._start_time

    def uptime(self):
        return time.time() - self._start_time

    def status(self):
        return self._status

    def name(self):
        return self._app_name

    def is_shutdown(self):
        return self._status == AppStatus.TERMINATING

    def shutdown(self):
        if self.is_shutdown():
            return
        self._status = AppStatus.TERMINATING
        for cb, args, kwargs in self._shutdown_cbs:
            cb(*args, **kwargs)

    def kill(self):
        self._status = AppStatus.KILLING
        sys.exit(-1000)

    def register_shutdown_callback(self, cb, *args, **kwargs):
        if callable(cb):
            self._shutdown_cbs.append((cb, args, kwargs))

    # noinspection PyUnusedLocal
    def _on_sigint(self, sig, frame):
        if self._sigint_counter == 0:
            self.logger.info('Shutdown request received! Gracefully terminating....')
            self.logger.info('Press [Ctrl+C] three times to force kill.')
            self.shutdown()
        if self._sigint_counter == 3:
            self.logger.info('Escalating to SIGKILL.')
            self.kill()
        self._sigint_counter += 1
