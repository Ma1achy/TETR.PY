import multiprocessing
import time
import pygame
import keyboard
from dataclasses import dataclass, field
from typing import Dict

@dataclass
class Timing:
    FPS: int = 144
    TPS: int = 256
    POLLING_RATE: int = 1000

    # Timing structures for main, render, and input loops
    start_times: Dict[str, float] = field(default_factory=lambda: {
        'input_loop': 0,
        'main_loop': 0,
        'render_loop': 0
    })
    elapsed_times: Dict[str, float] = field(default_factory=lambda: {
        'input_loop': 0,
        'main_loop': 0,
        'render_loop': 0
    })

class InputManager:
    def __init__(self, key_states_queue, stop_event):
        self.key_states_queue = key_states_queue
        self.stop_event = stop_event
        self.key_states = {}

    def start_keyboard_hook(self):
        keyboard.hook(self.get_key_events)

    def get_key_events(self, key_event):
        if key_event.event_type == keyboard.KEY_DOWN:
            self.key_states[key_event.name] = True
        elif key_event.event_type == keyboard.KEY_UP:
            self.key_states[key_event.name] = False
        self.key_states_queue.put(self.key_states)

    def run(self):
        self.start_keyboard_hook()
        while not self.stop_event.is_set():
            time.sleep(0.001)

class FourApp:
    def __init__(self):
        self.key_states_queue = multiprocessing.Queue()
        self.stop_event = multiprocessing.Event()
        self.input_manager = InputManager(self.key_states_queue, self.stop_event)

    def run(self):
        input_process = multiprocessing.Process(target=self.input_manager.run)
        input_process.start()

        try:
            while True:
                if not self.key_states_queue.empty():
                    key_states = self.key_states_queue.get()
                    print(key_states)
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.stop_event.set()
            input_process.join()

if __name__ == '__main__':
    app = FourApp()
    app.run()