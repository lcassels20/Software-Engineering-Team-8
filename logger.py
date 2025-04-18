event_log = None

def log_event(message):
    global event_log
    if event_log:
        def safe_insert():
            event_log.config(state="normal")
            event_log.insert("end", message + "\n")
            event_log.see("end")
            event_log.config(state="disabled")
        event_log.after(0, safe_insert)  
