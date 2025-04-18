# logger.py
event_log = None

def log_event(message):
    global event_log
    if event_log:
        event_log.config(state="normal")
        event_log.insert("end", message + "\n")
        event_log.see("end")
        event_log.config(state="disabled")
