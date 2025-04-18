# logger.py
import queue

log_queue = queue.Queue()

def log_event(message):
    log_queue.put(message)

