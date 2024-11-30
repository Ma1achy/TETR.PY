class DebugManager():
    def __init__(self, Config, TimingStruct, RenderStruct, DebugStruct):
        """
        Manage the debug information for the game
        
        args:
            Config (StructConfig): The configuration struct
            TimingStruct (StructTiming): The timing struct
            HandlingStruct (StructHandling): The handling struct
            GameInstanceStruct (StructGameInstance): The game instance struct
            FlagStruct (StructFlags): The flag struct
            RenderStruct (StructRender): The render struct
            DebugStruct (StructDebug): The debug struct
        """
        self.Config = Config
        self.Timing = TimingStruct
        self.RenderStruct = RenderStruct
        self.DebugStruct = DebugStruct
    
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
        self.__calculate_metrics(self.DebugStruct.delta_tick_list, (self.Config.TPS - self.DebugStruct.Current_TickRate), self.DebugStruct.delta_tick_idx, "DeltaTick", False)
        
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