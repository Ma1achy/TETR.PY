import time
import threading

class GameInstanceManager():
    def __init__(self, Timing, PRINT_WARNINGS):
        
        self.Timing = Timing
        self.PRINT_WARNINGS = PRINT_WARNINGS
        self.max_main_ticks_per_iteration = 256
        
    def logic_loop(self):
        try:
            while not self.Timing.exited:
                iteration_start_time = time.perf_counter()
                ticks_this_iteration = 0
                
                self.Timing.current_main_tick_time = time.perf_counter() - self.Timing.start_times['logic_loop']
                self.Timing.elapsed_times['logic_loop'] = self.Timing.current_main_tick_time
                
                self.Timing.main_tick_delta_time += (self.Timing.current_main_tick_time - self.Timing.last_main_tick_time) / self.Timing.tick_interval
                self.Timing.last_main_tick_time = self.Timing.current_main_tick_time
                
                if self.Timing.do_first_main_tick:

                    self.do_main_tick()
                    self.Timing.do_first_main_tick = False
                    ticks_this_iteration += 1
                    
                while self.Timing.main_tick_delta_time >= 1 and ticks_this_iteration < self.max_main_ticks_per_iteration: # only process a certain number of ticks per iteration otherwise drop the extra ticks to catch up
                    self.do_main_tick()
                    self.Timing.main_tick_delta_time -= 1
                    ticks_this_iteration += 1
                
                # recalibrate if too many ticks are processed in one iteration
                if ticks_this_iteration > self.max_main_ticks_per_iteration:
                    if self.PRINT_WARNINGS:
                        print("\033[93mWARNING: Too many ticks processed in one iteration of Logic Loop, recalibrating...\033[0m")
                        
                    self.Timing.main_tick_delta_time = 1
                    
                if self.Timing.current_main_tick_time > self.Timing.main_tick_counter_last_cleared + 1:
                    self.get_tps()
                    self.Timing.main_tick_counter = 0
                    self.Timing.main_tick_counter_last_cleared += 1
                
                iteration_end_time = time.perf_counter()
                elapsed_time = iteration_end_time - iteration_start_time
                        
                time.sleep(max(0, self.Timing.tick_interval - elapsed_time))
                                 
        except Exception as e:
            print(f"\033[91mError in {threading.current_thread().name}: {e}\033[0m")
            return
        
        finally:
            if self.PRINT_WARNINGS:
                print(f"\033[92mLogic loop Timing.exited in {threading.current_thread().name}\033[0m")
            self.Timing.exited = True
            return
    
    def do_main_tick(self):
        start = time.perf_counter()
        if self.Timing.exited:
            return
        
        self.Timing.main_tick_counter += 1
        self.Timing.iteration_times['logic_loop'] = time.perf_counter() - start
        
    def get_tps(self):
        self.Timing.TPS = self.Timing.main_tick_counter
