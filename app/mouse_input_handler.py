from collections import deque

class MouseInputHandler():
    def __init__(self, mouse_events:deque):
        
        self.is_focused = False
        self.mouse_position = 0, 0
        self.mouse_events = mouse_events

    def on_mouse_down(self, event):
        if not self.is_focused:
            return
        
        self.queue_mouse_events({f'MB{event.button}':{'down': True, 'up': False, 'pos': event.pos}})
      
    def on_mouse_up(self, event):
        if not self.is_focused:
            return
        
        self.queue_mouse_events({f'MB{event.button}':{'down': False, 'up': True, 'pos': event.pos}})
   
    def on_mouse_scroll(self, event):
        if not self.is_focused:
            return
        
        self.queue_mouse_events({'scroll': {'x': event.precise_x, 'y': event.precise_y, 'inverted': event.flipped}}) # inverted is a bool that indicates if the scroll direction is inverted on the system
        
    def on_mouse_move(self, event):
        if not self.is_focused:
            self.mouse_position = 0, 0
            return
        
        self.mouse_position = event.pos
        
    def queue_mouse_events(self, mouse_event):
        self.mouse_events.append(mouse_event)