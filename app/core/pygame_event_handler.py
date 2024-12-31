class PygameEventHandler:
    """
    A event handler helper for pygame events.
    """
    targets = {}

    @staticmethod
    def register(event_type):
        """
        Register a function to be called when a pygame event is triggered
        """
        def decorator(fn):
            PygameEventHandler.targets.setdefault(event_type, []).append(fn)
            return fn
        return decorator

    @staticmethod
    def notify(event):
        """
        Notify the functions that are listening for the event
        """
        fn_list = PygameEventHandler.targets.get(event.type, [])
        for fn in fn_list:
            fn(event)