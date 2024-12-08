import time
import threading
import traceback
import logging
import os
import sys
import datetime
import json
import pkg_resources
class GameInstanceManager():
    def __init__(self, Timing, Debug):
        
        self.Timing = Timing
        self.Debug = Debug
        
        self.max_main_ticks_per_iteration = 256
        
    def logic_loop(self):
        if self.Debug.PRINT_WARNINGS and self.Timing.restarts != 0:
            print(f"\033[93mRestarting {threading.current_thread().name}...\033[0m")
        try:  
            while not self.Timing.exited:
                
                ticks_this_iteration = 0
                start_time = time.perf_counter()
                
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
                    if self.Debug.PRINT_WARNINGS:
                        print("\033[93mWARNING: Too many ticks processed in one iteration of Logic Loop, recalibrating...\033[0m")
                        
                    self.Timing.main_tick_delta_time = 1
                    
                if self.Timing.current_main_tick_time > self.Timing.main_tick_counter_last_cleared + 1:
                    self.get_tps()
                    self.Timing.main_tick_counter = 0
                    self.Timing.main_tick_counter_last_cleared += 1
                
                elapsed_time = time.perf_counter() - start_time
                time.sleep(max(0, self.Timing.tick_interval - elapsed_time))
                                 
        except Exception as e:
            self.handle_exception(e)
        
        finally:
            if self.Debug.PRINT_WARNINGS:
                print(f"\033[92mLogic loop Timing.exited in {threading.current_thread().name}\033[0m")
            return
    
    def do_main_tick(self):
        start = time.perf_counter()
        if self.Timing.exited:
            return

        self.Timing.main_tick_counter += 1
        self.Timing.iteration_times['logic_loop'] = time.perf_counter() - start
        
    def get_tps(self):
        self.Timing.TPS = self.Timing.main_tick_counter
    
    def restart(self, error):
        self.Timing.restarts += 1
        current_time = time.perf_counter()
    
        time_since_last_restart = current_time - self.Timing.last_restart_time
       
        if time_since_last_restart < self.Timing.restart_interval :
            print(f"\033[91mRestart attempt too soon! \nExiting program... \nLast error: \n{error}\033[0m")
            self.Timing.exited = True
            return
        
        self.Timing.last_restart_time = current_time
        print('\033[93mAttempting restart:\033[0m')
        self.DebugStruct.ERROR = error
        
        try:
            self.__do_restart()
        except Exception as e:
            print(f"\033[93mError during restart attempt: {e}\033[0m")
            self.restart(e)
            
    def __do_restart(self):
        self.Timing.current_main_tick_time = 0
        self.Timing.last_main_tick_time = 0
        self.Timing.main_tick_delta_time = 0
        self.Timing.do_first_main_tick = True
        self.Timing.main_tick_counter_last_cleared = 0
        self.Timing.main_tick_counter = 0
        self.Timing.TPS = self.Timing.TPS
        self.Timing.iteration_times['logic_loop'] = 1
        self.Timing.elapsed_times['logic_loop'] = 0
        self.Timing.start_times['logic_loop'] = time.perf_counter()
        self.logic_loop()
    
    def handle_exception(self, e):
        print(f"\033[91mError in {threading.current_thread().name}: \n{e}\033[0m")
        
        tb_str = traceback.format_exc()
        current_thread = threading.current_thread()
        timestamp = datetime.datetime.now().isoformat()
        
        env_info = {
            "OS": os.name,
            "Platform": sys.platform,
            "Python Version": sys.version,
            "Current Working Directory": os.getcwd(),
            "Imported Packages": self.__get_imported_packages(),
            "Build Info": self.__get_build_info()
        }
        
        
        logging.error(f"\033[91m{'Exception occurred at %s in thread %s: %s'}\033[0m", timestamp, current_thread.name, tb_str)
        logging.error("Environment information: %s", env_info)
        
        info = {
            "Exception Information": {
            "Timestamp": timestamp,
            "Thread": current_thread.name,
            "Traceback": tb_str
            },
            
            "Environment Information": env_info
        }
        self.restart((info, e, tb_str))
    
    def __get_imported_packages(self):
        imported_packages = {}
        for name, module in sys.modules.items():
            if name in pkg_resources.working_set.by_key:
                imported_packages[name] = pkg_resources.working_set.by_key[name].version
        return imported_packages

    def __get_build_info(self):
        path = os.path.join(os.getcwd(), 'app/state/build_info.json')
        try:
            with open(path, 'r') as file:
                build_info = json.load(file)
        except Exception as e:
            build_info = None
        return build_info
        
        
