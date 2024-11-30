class PygameEventHandler:
    targets = {}

    @staticmethod
    def register(event_type):
        def decorator(fn):
            PygameEventHandler.targets.setdefault(event_type, []).append(fn)
            return fn
        return decorator

    @staticmethod
    def notify(event):
        fn_list = PygameEventHandler.targets.get(event.type, [])
        for fn in fn_list:
            fn(event)