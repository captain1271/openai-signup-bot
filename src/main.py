import threading
import time

from config import signup_worker_num
from pool_manager import ThreadPoolManager
from signup import run_sign_up
from state_manager import GlobalStateManager
from verify_email import verify_email


def sign_up_worker(sm):
    pm = ThreadPoolManager(signup_worker_num)
    while not sm.should_stop():
        pm.add_task(run_sign_up, sm)
        time.sleep(0.1)


def main():
    sm = GlobalStateManager()

    email_worker = threading.Thread(target=verify_email, args=(sm,))
    email_worker.start()

    sign_worker = threading.Thread(target=sign_up_worker, args=(sm,))
    sign_worker.start()

    email_worker.join()
    sign_worker.join()


if __name__ == '__main__':
    main()
