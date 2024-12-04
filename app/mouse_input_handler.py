class MouseInputHandler():
    def __init__(self, Mouse):
        
        self.Mouse = Mouse
        self.is_focused = False

    def on_mouse_down(self, event):
        if not self.is_focused:
            return
        
        self.queue_mouse_events({f'mb{event.button}':{'down': True, 'up': False, 'pos': event.pos}})
      
    def on_mouse_up(self, event):
        if not self.is_focused:
            return
        
        self.queue_mouse_events({f'mb{event.button}':{'down': False, 'up': True, 'pos': event.pos}})
   
    def on_mouse_scroll(self, event):
        if not self.is_focused:
            return
        
        self.queue_mouse_events({'scrollwheel': {'x': event.precise_x, 'y': event.precise_y, 'inverted': event.flipped}}) # inverted is a bool that indicates if the scroll direction is inverted on the system
        
    def on_mouse_move(self, event):
        if not self.is_focused:
            self.Mouse.position = 0, 0
            return
        
        self.Mouse.position = event.pos
        
    def queue_mouse_events(self, mouse_event):
        self.Mouse.events.put(mouse_event)