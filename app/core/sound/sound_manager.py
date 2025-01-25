import pygame
from app.core.sound.music import Music
from app.core.sound.sfx import SFX
from app.core.sound.sound import Sound
import os

class SoundManager():
    def __init__(self, Sound:Sound):
        
        self.Sound = Sound
        
        self.music_tracks = {
            Music.CHK_019    : {"path": "resources\sound\music\CHK-019 - Aerial City (Chika) - Interface.mp3",      "loop": (11806, 92554)},
            Music.KMY_090    : {"path": "resources\sound\music\KMY-090 - To The Limit (Kamiya) - Interface.mp3",    "loop": (1229, 90522)},
        }
        
        self.sound_effects = {
            SFX.MenuHover    : "resources\sound\SFX\menu_hover.ogg",
            SFX.MenuTap      : "resources\sound\SFX\menu_tap.ogg",
            SFX.MenuBack     : "resources\sound\SFX\menu_back.ogg",
            SFX.MenuClick    : "resources\sound\SFX\menu_click.ogg",
            SFX.MenuConfirm  : "resources\sound\SFX\menu_confirm.ogg",
            SFX.MenuHit1     : "resources\sound\SFX\menu_hit_1.ogg",
            SFX.MenuHit2     : "resources\sound\SFX\menu_hit_2.ogg",
            SFX.MenuHit3     : "resources\sound\SFX\menu_hit_3.ogg",
        }
        
        self.num_channels = 16
        self.frequency = 44100
        self.bitsize = -16
        self.buffer_size = 1024
        
        self.initialized = True
        self.__init_pygame_mixer()
        self.set_number_of_channels(self.num_channels)
        self.__load_sfx()
        
        self.current_music = None
        self.loop_start = 0  
        self.loop_end = 0   
        
    def __load_sfx(self):
        for sfx in self.sound_effects:
            if not os.path.exists(self.sound_effects[sfx]):
                self.sound_effects[sfx] = None
                continue 
            self.sound_effects[sfx] = pygame.mixer.Sound(self.sound_effects[sfx])
           
    def __init_pygame_mixer(self):
        pygame.mixer.init(
            frequency = self.frequency,
            size = self.bitsize,
            channels = 2,
            buffer = self.buffer_size
        )
        pygame.mixer.set_reserved(1) # reserve channel 0 for music

    def quit(self):
        pygame.mixer.quit()

    def set_number_of_channels(self, channels):
        pygame.mixer.set_num_channels(channels)

    def tick(self):
        self.__process_queues()
        
    def __process_queues(self):
        
        if self.Sound.music_queue:
            music = self.Sound.music_queue.popleft()  
            self.__play_music(music)

        if self.Sound.sfx_queue:
            sfx = self.Sound.sfx_queue.popleft() 
            self.__play_sfx(sfx)
    
    def loop_current_song(self, event):
        """
        Handle Pygame events to manage music looping from specified loop points.
        """
        pygame.mixer.music.play(loops = 0, start = self.loop_start / 1000.0)
        pygame.time.set_timer(pygame.USEREVENT, self.loop_end - self.loop_start) # timer plays loop end - loop start to only play the looped section

    def __play_sfx(self, sfx: SFX):
        """
        Play a sound effect if an available channel exists.
        
        args:
            sfx (SFX): The sound effect to play.
        """
        if sfx not in self.sound_effects:
            return
        
        if self.sound_effects[sfx] is None:
            return
        
        channel = pygame.mixer.find_channel()
        if channel:
            channel.play(self.sound_effects[sfx])
    
    def __play_music(self, music: Music):
        if music not in self.music_tracks:
            return

        music_info = self.music_tracks[music]
        music_path = music_info["path"]
        loop_start, loop_end = music_info["loop"]

        if not os.path.exists(music_path):
            return

        if self.current_music == music:
            return
        
        if pygame.mixer.music.get_busy():  # if already playing music, fade out and queue next song
            pygame.mixer.music.fadeout(500)
            pygame.mixer.music.queue(music_path)
            self.__set_current_song(music, loop_start, loop_end)
            return

        pygame.mixer.music.load(music_path)
        pygame.mixer.music.play(loops = 0)
        
        self.__set_current_song(music, loop_start, loop_end)
 
    def __set_current_song(self, music, loop_start, loop_end):
        self.current_music = music
        self.loop_start, self.loop_end = loop_start, loop_end
        
        if self.loop_start and self.loop_end is not None:
            pygame.time.set_timer(pygame.USEREVENT, self.loop_end)
        
    def set_sound_volume(self, sound_enum, volume):
        """
        Set the volume for a specific sound or music.
        
        args:
            sound_enum (SFX or Music): SFX or Music enum representing the sound.
            volume (float): Volume level between 0.0 and 1.0
        """
        if isinstance(sound_enum, SFX):
            
            if sound_enum in self.sound_effects:
                self.sound_effects[sound_enum].set_volume(volume)
            else:
                print(f"Sound effect '{sound_enum}' not loaded.")     
                
        elif isinstance(sound_enum, Music):
            
            if sound_enum in self.music_tracks:
                pygame.mixer.Channel(0).set_volume(volume)
            else:
                print(f"Music '{sound_enum}' not loaded.")
        else:
            print("Invalid sound enum type. Must be SFX or Music.")

    def get_sound_volume(self, sound_enum):
        """
        Get the volume for a specific sound or music.
        
        args:
            sound_enum (SFX or Music): SFX or Music enum representing the sound.
        """
        if isinstance(sound_enum, SFX):
            
            if sound_enum in self.sound_effects:
                return self.sound_effects[sound_enum].get_volume()
            else:
                print(f"Sound effect '{sound_enum}' not loaded.")
                return None
            
        elif isinstance(sound_enum, Music):
            
            if sound_enum in self.music_tracks:
                return pygame.mixer.Channel(0).get_volume()
            else:
                print(f"Music '{sound_enum}' not loaded.")
                return None
        else:
            print("Invalid sound enum type. Must be SFX or Music.")
            return None

    def set_music_channel_volume(self, volume):
        """
        Set the volume for the music channel.
        
        args:
            volume (float): Volume level between 0.0 and 1.0
        """
        pygame.mixer.Channel(0).set_volume(volume)
        
    def set_sfx_channels_volume(self, volume):
        """
        Set the volume for all SFX channels.
        
        args:
            volume (float): Volume level between 0.0 and 1.0
        """
        for i in range(1, self.num_channels):
            pygame.mixer.Channel(i).set_volume(volume)

    def stop_all_sounds(self):
        pygame.mixer.stop()

    def pause_all_sounds(self):
        pygame.mixer.pause()

    def resume_all_sounds(self):
        pygame.mixer.unpause()

    def fade_out_all_sounds(self, time):
        pygame.mixer.fadeout(time)

    def is_mixer_busy(self):
        return pygame.mixer.get_busy()
    
    def get_no_of_playing_channels(self):
        """
        Get the number of currently playing channels in the Pygame mixer.
        
        Returns:
            int: The number of currently playing channels.
        """
        p = 0 
        for i in range(self.num_channels):
            if pygame.mixer.Channel(i).get_busy():
                p += 1
        return p