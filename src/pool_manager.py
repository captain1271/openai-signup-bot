from queue import Queue
from threading import Thread, Lock

from loguru import logger


class ThreadPoolManager:
    def __init__(self, max_threads):
        self.max_threads = max_threads
        self.tasks_queue = Queue(max_threads)
        self.threads = []
        self.lock = Lock()
        self._initialize_threads()

    def _initialize_threads(self):
        for _ in range(self.max_threads):
            thread = Thread(target=self._worker)
            thread.daemon = True
            thread.start()
            self.threads.append(thread)

    def add_task(self, func, *args, **kwargs):
        self.tasks_queue.put((func, args, kwargs))

    def _worker(self):
        while True:
            func, args, kwargs = self.tasks_queue.get()
            try:
                func(*args, **kwargs)
            except Exception as e:
                logger.error(f"An error occurred: {e}")
            self.tasks_queue.task_done()

    def wait_completion(self):
        self.tasks_queue.join()
