from app.input.mouse.mouse import MouseEvents
class MouseInputManager():
    def __init__(self, Mouse):
        
        self.Mouse = Mouse
        self.is_focused = False

        self.button_map = {
            1: MouseEvents.MOUSEBUTTON1,
            2: MouseEvents.MOUSEBUTTON2,
            3: MouseEvents.MOUSEBUTTON3,
            4: MouseEvents.MOUSEBUTTON4,
            5: MouseEvents.MOUSEBUTTON5,
            6: MouseEvents.MOUSEBUTTON6,
            7: MouseEvents.MOUSEBUTTON7,
            8: MouseEvents.MOUSEBUTTON8,
            9: MouseEvents.MOUSEBUTTON9,
            10: MouseEvents.MOUSEBUTTON10,
        }
        
    def on_mouse_down(self, event):
        """
        Handle the mouse button down event and queue the mouse button event
        
        args:
            event (pygame.event): the event to handle
        """
        if not self.is_focused:
            return
        
        self.queue_mouse_events({self.button_map.get(event.button, MouseEvents.MOUSEBUTTON1):{'down': True, 'up': False, 'pos': event.pos}})
      
    def on_mouse_up(self, event):
        """
        Handle the mouse button up event and queue the mouse button event
        
        args:
            event (pygame.event): the event to handle
        """
        if not self.is_focused:
            return
        
        self.queue_mouse_events({self.button_map.get(event.button, MouseEvents.MOUSEBUTTON1):{'down': False, 'up': True, 'pos': event.pos}})
   
    def on_mouse_scroll(self, event):
        """
        Handle the mouse scroll event and queue the scroll wheel event
        
        args:
            event (pygame.event): the event to handle
        """
        if not self.is_focused:
            return
        
        self.queue_mouse_events({MouseEvents.SCROLLWHEEL: {'x': event.precise_x, 'y': event.precise_y, 'inverted': event.flipped}}) # inverted is a bool that indicates if the scroll direction is inverted on the system
        
    def on_mouse_move(self, event):
        """
        Handle the mouse move event and update the mouse position and motion
        
        args:
            event (pygame.event): the event to handle
        """
        if not self.is_focused:
            self.Mouse.position = 0, 0
            return
        
        self.Mouse.position = event.pos
        self.Mouse.motion = event.rel
        
    def queue_mouse_events(self, mouse_event):
        """
        Queue the mouse events
        
        args:
            mouse_event (dict): the mouse event to queue
        """
        self.Mouse.events.put(mouse_event)
