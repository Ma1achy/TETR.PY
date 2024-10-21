from config import StructConfig
from core.state.struct_render import StructRender
from core.state.struct_flags import StructFlags
from core.state.struct_gameinstance import StructGameInstance
from core.state.struct_timing import StructTiming
from core.state.struct_debug import StructDebug
from render.board.struct_board import StructBoardConsts
import pygame

class UIActionText():
    def __init__(self, Config:StructConfig, RenderStruct:StructRender, FlagStruct:StructFlags, GameInstanceStruct:StructGameInstance, TimingStruct:StructTiming, DebugStruct:StructDebug):

        self.Config = Config
        self.RenderStruct = RenderStruct
        self.FlagStruct = FlagStruct
        self.GameInstanceStruct = GameInstanceStruct
        self.TimingStruct = TimingStruct
        self.DebugStruct = DebugStruct
        
    def draw(self, surface):
        pass
            