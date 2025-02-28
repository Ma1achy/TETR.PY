import json
import sys
import platform
import pygame
import psutil
import time
import os
import GPUtil

class DebugManager():
    def __init__(self, TimingStruct, RenderStruct, DebugStruct):
        """
        Manage the debug information for the game
        
        args:
            TimingStruct (StructTiming): The timing information and constants
            RenderStruct (StructRender): The render information and constants
            DebugStruct (StructDebug): The debug information
        """
        self.Timing = TimingStruct
        self.RenderStruct = RenderStruct
        self.DebugStruct = DebugStruct
        
        self.get_build_info()
        
        psutil.cpu_percent(interval = None)
        
        self.cpu_last_update_time = 0
        self.memory_last_update_time = 0
        self.gpu_last_update_time = 0
        self.update_interval = 1
        self.cached_cpu_usage = 0
        self.cached_memory_usage = {
            'total_memory': '',
            'used_memory': '',
            'memory_percent': 0
        }
        self.cached_gpu_usage = {
            'gpu_id': '',
            'gpu_name': '',
            'gpu_load': 0,
            'gpu_memory_total': 0,
            'gpu_memory_used': 0,
            'gpu_memory_free': 0,
            'gpu_temperature': 0
        }
    
    
    # =================================================== METRIC CALCULATION ===================================================
    
    def __calculate_metrics(self, values_list, current_value, idx, metric, larger_is_better):
        """
        Calculate the average, best and worst values of a metric
        
        args:
            values_list (list): The list of values to calculate the metrics for
            current_value (int): The current value of the metric
            idx (int): The current index of the list
            metric (str): The name of the metric
            larger_is_better (bool): Whether a larger value is better for the metric
        """
        if idx >= self.DebugStruct.max_avg_len:
            idx = 0
        
        if len(values_list) >= self.DebugStruct.max_avg_len:
            values_list.pop(idx)
        
        values_list.append(current_value)
        idx += 1
        
        average = sum(values_list) / len(values_list)
        
        if larger_is_better:
            best_value = max(values_list)
            worst_value = min(values_list)
        else:
            best_value = min(values_list)
            worst_value = max(values_list)
            
        self.__update_debug_info(metric, current_value, average, best_value, worst_value)
    
    def __update_debug_info(self, metric, current_value, average, best_value, worst_value):
        """
        Update the debug information stored in the debug struct
        
        args:
            metric (str): The name of the metric
            current_value (int): The current value of the metric
            average (int): The average value of the metric
            best_value (int): The best value of the metric
            worst_value (int): The worst value of the metric
        """
        current_attr = f"Current_{metric}"
        average_attr = f"Average_{metric}"
        best_attr = f"Best_{metric}"
        worst_attr = f"Worst_{metric}"
        
        setattr(self.DebugStruct, current_attr, current_value)
        setattr(self.DebugStruct, average_attr, average)
        setattr(self.DebugStruct, best_attr, best_value)
        setattr(self.DebugStruct, worst_attr, worst_value)
    
    # =================================================== DEBUG METRICS ===================================================
    
    def __get_tick_debug(self):
        """
        Get the tick related debug information
        """
        self.DebugStruct.TPS = self.Timing.TPS
        self.DebugStruct.TickCounter = self.Timing.main_tick_counter
        
        self.__calculate_metrics(self.DebugStruct.TPS_list, self.Timing.TPS, self.DebugStruct.tps_idx, "TickRate", True)
        self.__calculate_metrics(self.DebugStruct.tick_time_list, self.Timing.iteration_times["logic_loop"], self.DebugStruct.tick_time_idx, "ExecutionTime", False)
        self.__calculate_metrics(self.DebugStruct.delta_tick_list, (self.Timing.target_TPS - self.DebugStruct.Current_TickRate), self.DebugStruct.delta_tick_idx, "DeltaTick", False)
        
    def __get_frame_debug(self):
        """
        Get the frame related debug information
        """
        self.DebugStruct.FPS = self.Timing.FPS
        self.__calculate_metrics(self.DebugStruct.FPS_list, self.DebugStruct.FPS, self.DebugStruct.fps_idx, "FrameRate", True)
        self.__calculate_metrics(self.DebugStruct.render_time_list, self.Timing.iteration_times["render_loop"], self.DebugStruct.render_idx, "RenderTime", False)
    
    def __get_polling_debug(self):
        """
        Get the polling related debug information
        """
        self.DebugStruct.PollingRate = self.Timing.POLLING_RATE
        self.DebugStruct.PollingCounter = self.Timing.input_tick_counter
        
        self.__calculate_metrics(self.DebugStruct.polling_rate_list, self.DebugStruct.PollingRate, self.DebugStruct.polling_idx, "PollingRate", True)
        self.__calculate_metrics(self.DebugStruct.polling_time_list, self.Timing.iteration_times["input_loop"], self.DebugStruct.polling_time_idx, "PollingTime", False) 
        
    def get_metrics(self):
        """
        Get the debug metrics for the debug menu
        """
        self.__get_tick_debug()
        self.__get_frame_debug()
        self.__get_polling_debug()
        self.__get_debug()
    
    def __get_debug(self):
        """
        Get the debug information
        """
        self.DebugStruct.CPU_Usage = self.get_cpu_usage()
        self.DebugStruct.TotalMemory, self.DebugStruct.UsedMemory, self.DebugStruct.MemoryPercent = self.get_memory_usage()
        self.DebugStruct.GPUStats = self.get_gpu_usage()
    
    def get_pygame_version(self):
        """
        Get the current Pygame version
        """
        return pygame.__version__

    def get_build_info(self):
        """
        Get the build information from the build_info.json file
        """
        with open("app/build_info.json") as f:
            build_info = json.load(f)
        
        self.DebugStruct.BuildInfo = build_info
        
        self.DebugStruct.PythonVersion = self.get_python_version()
        self.DebugStruct.OS = self.get_os_version()
        self.DebugStruct.PygameVersion = self.get_pygame_version()
        
    def get_python_version(self):
        """
        Get the current Python version
        """
        return sys.version.split()[0]

    def get_os_version(self):
        """
        Get the OS version
        """
        return platform.system() + " " + platform.release()

    def get_cpu_usage(self):
        """
        Get the current CPU usage as a percentage
        """
        current_time = time.time()
        if current_time - self.cpu_last_update_time > self.update_interval:
            self.cached_cpu_usage = psutil.cpu_percent(interval=None)
            self.cpu_last_update_time = current_time
        return self.cached_cpu_usage
    
    def format_memory_size(self, size_in_bytes):
        """
        Format a memory size in bytes to a human-readable format
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_in_bytes < 1024:
                return f"{size_in_bytes:.2f} {unit}"
            size_in_bytes /= 1024
        
    def get_memory_usage(self):
        """
        Get the amount memory used by the app
        """
        current_time = time.time()
        if current_time - self.memory_last_update_time > self.update_interval:
  
            memory_info = psutil.virtual_memory()
            total_memory = self.format_memory_size(memory_info.total)
            
            process = psutil.Process(os.getpid())
            process_memory_info = process.memory_info()
            used_memory = self.format_memory_size(process_memory_info.rss)
            memory_percent = process.memory_percent()
            
            self.cached_memory_usage = {
                'total_memory': total_memory,
                'used_memory': used_memory,
                'memory_percent': memory_percent
            }
            self.memory_last_update_time = current_time
        
        return self.cached_memory_usage['total_memory'], self.cached_memory_usage['used_memory'], self.cached_memory_usage['memory_percent']
    
    def get_gpu_usage(self):
        """
        Get the current GPU usage information
        """
        current_time = time.time()
        if current_time - self.gpu_last_update_time > self.update_interval:
            gpus = GPUtil.getGPUs()
            if not gpus:
                self.cached_gpu_usage = {
                    'gpu_id': '???',
                    'gpu_name': '???',
                    'gpu_load': 0,
                    'gpu_memory_total': 0,
                    'gpu_memory_used': 0,
                    'gpu_memory_free': 0,
                    'gpu_temperature': 0
                }
            else:
                gpu = gpus[0]
                self.cached_gpu_usage = {
                    'gpu_id': gpu.id,
                    'gpu_name': gpu.name,
                    'gpu_load': gpu.load * 100,
                    'gpu_memory_total': self.format_memory_size(gpu.memoryTotal * 1024 * 1024),
                    'gpu_memory_used': self.format_memory_size(gpu.memoryUsed * 1024 * 1024),
                    'gpu_memory_free': self.format_memory_size(gpu.memoryFree * 1024 * 1024),
                    'gpu_temperature': gpu.temperature
                }
            self.gpu_last_update_time = current_time
        
        return self.cached_gpu_usage