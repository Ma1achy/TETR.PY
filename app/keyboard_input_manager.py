import threading
import pynput.keyboard as keyboard # cannot use keyboard module as it is not supported in macOS :-)
import time
import queue 
import traceback
import logging

class KeyboardInputManager:
    def __init__(self, Keyboard, Timing, Debug):
        
        self.Keyboard = Keyboard
        self.Timing = Timing
        self.Debug = Debug
        
        self.max_poll_ticks_per_iteration = 1000
        
    def start_keyboard_hook(self):
        self.keyboard_listener = keyboard.Listener(
            on_press = self.on_key_press,
            on_release = self.on_key_release
        )
        self.keyboard_listener.start()
    
    def stop_keyboard_hook(self):
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_hook = None
    
    def exit(self):
        """
        Stops the InputManager and cleans up resources.
        """
        self.Timing.exited = True
        self.stop_keyboard_hook()
        
    def queue_key_states(self):
        self.Keyboard.key_states_queue.put(self.Keyboard.key_states)

    def on_key_press(self, key):
        
        if not self.Timing.is_focused:
            self.Keyboard.key_states = {}
            return
        
        keyinfo = self.__get_key_info(key)
        
        try:
            KeyEntry = self.Keyboard.key_states[keyinfo]
            if KeyEntry:
                KeyEntry['previous'] = KeyEntry['current']
                KeyEntry['current'] = True
                
        except KeyError:
            KeyEntry = self.Keyboard.key_states.setdefault(keyinfo, {'current': False, 'previous': False})
            KeyEntry['previous'] = KeyEntry['current']
            KeyEntry['current'] = True
           
        self.queue_key_states()
         
    def on_key_release(self, key):
        
        if not self.Timing.is_focused:
            self.Keyboard.key_states = {}
            return
        
        keyinfo = self.__get_key_info(key)
        
        try:
            KeyEntry = self.Keyboard.key_states[keyinfo]
            if KeyEntry and KeyEntry['current']: # only update if the key was pressed to prevent multiple releases from being registered
                KeyEntry['previous'] = KeyEntry['current']
                KeyEntry['current'] = False
                
        except KeyError:
            KeyEntry = self.Keyboard.key_states.setdefault(keyinfo, {'current': False, 'previous': False})
            KeyEntry['previous'] = KeyEntry['current']
            KeyEntry['current'] = False
        
       
        self.queue_key_states()
         
    def __get_key_info(self, key):
        try:
            return key.name
        except AttributeError:
            return key

    def reset_key_states(self):
        for key in self.Keyboard.key_states:
            self.Keyboard.key_states[key]['previous'] = self.Keyboard.key_states[key]['current']
        self.queue_key_states()
        
    def input_loop(self):
        if self.Debug.PRINT_WARNINGS and self.Timing.restarts != 0:
            print(f"\033[93mRestarting {threading.current_thread().name}...\033[0m")
        try:
            while not self.Timing.exited:
                
                ticks_this_iteration = 0
                start_time = time.perf_counter()
                
                self.Timing.current_input_tick_time = time.perf_counter() - self.Timing.start_times['input_loop']
                self.Timing.elapsed_times['input_loop'] = self.Timing.current_input_tick_time
                
                self.Timing.input_tick_delta_time += (self.Timing.current_input_tick_time - self.Timing.last_input_tick_time) / self.Timing.poll_interval
                self.Timing.last_input_tick_time = self.Timing.current_input_tick_time
                
                if self.Timing.do_first_input_tick:
                    self.do_input_tick()
                    self.Timing.do_first_input_tick = False
                    ticks_this_iteration += 1
                
                while self.Timing.input_tick_delta_time >= 1 and ticks_this_iteration < self.max_poll_ticks_per_iteration:
                    self.do_input_tick()
                    self.Timing.input_tick_delta_time -= 1
                    ticks_this_iteration += 1
                    
                if ticks_this_iteration > self.max_poll_ticks_per_iteration:
                    if self.Debug.PRINT_WARNINGS:
                        print("\033[93mWARNING: Too many ticks processed in one iteration of Input Loop, recalibrating...\033[0m")
                        
                    self.Timing.input_tick_delta_time = 1
                
                if self.Timing.current_input_tick_time > self.Timing.input_tick_counter_last_cleared + 1:
                    self.get_poll_rate()
                    self.Timing.input_tick_counter = 0
                    self.Timing.input_tick_counter_last_cleared += 1

                elapsed_time = time.perf_counter() - start_time
                time.sleep(max(0, self.Timing.poll_interval - elapsed_time))
                
        except Exception as e:
            print(f"\033[91mError in {threading.current_thread().name}: {e}\033[0m")
            tb_str = traceback.format_exc()
            logging.error("Exception occurred: %s", tb_str)
            self.__restart((threading.current_thread().name, e, tb_str))
        
        finally:
            if self.Debug.PRINT_WARNINGS:
                print(f"\033[92mInput loop Timing.exited in {threading.current_thread().name}\033[0m")
            return
    
    def do_input_tick(self):
        
        if self.Timing.exited:
            return
        
        start = time.perf_counter()
              
        try:
            self.Keyboard.key_states = self.Keyboard.key_states_queue.get_nowait()
        except queue.Empty:
            self.reset_key_states()
    
        self.Timing.input_tick_counter += 1
        self.Timing.iteration_times['input_loop'] = time.perf_counter() - start
        
    def get_poll_rate(self):
        self.Timing.POLLING_RATE = self.Timing.input_tick_counter
    
    def __restart(self, error):
        self.Debug.ERROR = error
        MAX_RESTARTS = 2
        self.Timing.restarts += 1
        print(f'\033[93mAttempting restart {threading.current_thread().name}\033[0m')
      
        try:
            if self.Timing.restarts > MAX_RESTARTS:
                print(f"\033[91mMaximum restart attempts reached! \nExiting program... \nLast error: {error}\033[0m")
                self.Timing.exited = True
                return
       
            self.__do_restart()
            
        except Exception as e:
            print(f"\033[93mError during restart attempt: {e}\033[0m")
            if self.Timing.restarts > MAX_RESTARTS:
                self.Timing.exited = True
            else:
                self.__restart(e)
    
    def __do_restart(self):
        self.Timing.POLLING_RATE = 1000
        self.Timing.current_input_tick_time = 0
        self.Timing.last_input_tick_time = 0
        self.Timing.input_tick_delta_time = 0
        self.Timing.do_first_input_tick = True
        self.Timing.input_tick_counter = 0
        self.Timing.input_tick_counter_last_cleared = 0
        self.Timing.elapsed_times['input_loop'] = 0
        self.Timing.iteration_times['input_loop'] = 1
        self.Timing.start_times['input_loop'] = time.perf_counter()
 
        self.input_loop()
        
    
