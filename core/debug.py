class Debug():
    def __init__(self, Config, TimingStruct, HandlingStruct, GameInstanceStruct, FlagStruct, RenderStruct, DebugStruct):
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
        self.TimingStruct = TimingStruct
        self.HandlingStruct = HandlingStruct
        self.GameInstanceStruct = GameInstanceStruct
        self.FlagStruct = FlagStruct
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
        self.__calculate_metrics(self.DebugStruct.TPS_list, self.TimingStruct.TPS, self.DebugStruct.tps_idx, "TickRate", True)
        self.__calculate_metrics(self.DebugStruct.tick_time_list, self.TimingStruct.iter_times["game_loop"], self.DebugStruct.tick_time_idx, "ExecutionTime", False)
        self.__calculate_metrics(self.DebugStruct.delta_tick_list, (self.Config.TPS - self.DebugStruct.Current_TickRate), self.DebugStruct.delta_tick_idx, "DeltaTick", False)
        
        self.DebugStruct.TickCounter = self.TimingStruct.tick_counter
        
    def __get_frame_debug(self):
        """
        Get the frame related debug information
        """
        self.__calculate_metrics(self.DebugStruct.FPS_list, self.DebugStruct.FPS, self.DebugStruct.fps_idx, "FrameRate", True)
        self.__calculate_metrics(self.DebugStruct.render_time_list, self.TimingStruct.iter_times["render_loop"], self.DebugStruct.render_idx, "RenderTime", False)
    
    def __get_polling_debug(self):
        """
        Get the polling related debug information
        """
        self.__calculate_metrics(self.DebugStruct.polling_rate_list, self.DebugStruct.polling_rate, self.DebugStruct.polling_idx, "PollingRate", True)
        self.__calculate_metrics(self.DebugStruct.polling_time_list, self.TimingStruct.iter_times["handle_events"], self.DebugStruct.polling_time_idx, "PollingTime", False) 
  
    def get_metrics(self):
        """
        Get the debug metrics for the debug menu
        """
        self.__get_tick_debug()
        self.__get_frame_debug()
        self.__get_polling_debug()
        
        # DAS
        self.DebugStruct.DAS_Left_Counter = self.HandlingStruct.DAS_LEFT_COUNTER
        self.DebugStruct.DAS_Right_Counter = self.HandlingStruct.DAS_RIGHT_COUNTER
        self.DebugStruct.DAS_Threshold = self.Config.HANDLING_SETTINGS['DAS']
        self.DebugStruct.DAS_Cancel = self.Config.HANDLING_SETTINGS['DASCancel']
        self.DebugStruct.DCD = self.Config.HANDLING_SETTINGS['DCD']
        
        # ARR
        self.DebugStruct.ARR_Left_Counter = self.HandlingStruct.ARR_LEFT_COUNTER
        self.DebugStruct.ARR_Right_Counter = self.HandlingStruct.ARR_RIGHT_COUNTER
        self.DebugStruct.ARR_Threshold = self.Config.HANDLING_SETTINGS['ARR']
        
        # direction prioritisation
        self.DebugStruct.Prioritise_Direction = self.Config.HANDLING_SETTINGS['PrioriDir']
        self.DebugStruct.Direction = self.HandlingStruct.dir_priority
        
        # soft drop
        self.DebugStruct.Soft_Drop_Factor = self.Config.HANDLING_SETTINGS['SDF']
        self.DebugStruct.Prefer_Soft_Drop = self.Config.HANDLING_SETTINGS['PrefSD']
        
        # gravity
        self.DebugStruct.Gravity = self.GameInstanceStruct.gravity
        self.DebugStruct.G_in_ticks = self.GameInstanceStruct.G_units_in_ticks
        self.DebugStruct.Gravity_Counter = self.GameInstanceStruct.gravity_counter
        self.DebugStruct.Gravity_Multiplier = self.GameInstanceStruct.soft_drop_factor
        
        # lock delay
        self.DebugStruct.On_Floor = self.GameInstanceStruct.current_tetromino.is_on_floor() if self.GameInstanceStruct.current_tetromino else False
        self.DebugStruct.Lock_Delay = self.GameInstanceStruct.lock_delay
        self.DebugStruct.Lock_Delay_Ticks = self.GameInstanceStruct.lock_delay_in_ticks
        self.DebugStruct.Lock_Delay_Counter = self.GameInstanceStruct.current_tetromino.lock_delay_counter if self.GameInstanceStruct.current_tetromino else 0
        self.DebugStruct.Max_Moves = self.GameInstanceStruct.current_tetromino.max_moves_before_lock if self.GameInstanceStruct.current_tetromino else 0
        self.DebugStruct.Lowest_Pivot = self.GameInstanceStruct.current_tetromino.lowest_pivot_position if self.GameInstanceStruct.current_tetromino else 0
        
        # prevent accidental hard drop
        self.DebugStruct.Prevent_Accidental_Hard_Drop = self.Config.HANDLING_SETTINGS['PrevAccHD']
        self.DebugStruct.Prevent_Accidental_Hard_Drop_Flag = self.FlagStruct.DO_PREVENT_ACCIDENTAL_HARD_DROP
        self.DebugStruct.Prevent_Accidental_Hard_Drop_Time = int(self.Config.HANDLING_SETTINGS['PrevAccHDTime'] / 60 * self.Config.TPS)
        self.DebugStruct.Prevent_Accidental_Hard_Drop_Counter = self.HandlingStruct.PREV_ACC_HD_COUNTER
        
        self.DebugStruct.Seed = self.GameInstanceStruct.seed