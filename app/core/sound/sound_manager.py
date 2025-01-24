import pygame
from app.core.sound.music import Music
from app.core.sound.sfx import SFX
from app.core.sound.sound import Sound
import os

class SoundManager():
    def __init__(self, Sound:Sound):
        
        self.Sound = Sound
        
        self.music_tracks = {
            
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
        self.buffer_size = 512
        
        self.initialized = True
        self.__init_pygame_mixer()
        self.set_number_of_channels(self.num_channels)
        self.__load_sfx()
        self.__load_music()

    def __load_sfx(self):
        for sfx in self.sound_effects:
            if not os.path.exists(self.sound_effects[sfx]):
                self.sound_effects[sfx] = None
                continue 
            self.sound_effects[sfx] = pygame.mixer.Sound(self.sound_effects[sfx])
           
    def __load_music(self):
        for music in self.music_tracks:
            if not os.path.exists(self.music_tracks[music]):
                self.music_tracks[music] = None
                continue
            self.music_tracks[music] = pygame.mixer.Sound(self.music_tracks[music])
            
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
        """
        Play music on the reserved channel, stopping any current music.
        
        args:
            music (Music): The music track to play.
        """
        if music not in self.music_tracks:
            return
        
        if self.music_tracks[music] is None:
            return
        
        if pygame.mixer.Channel(0).get_sound() == self.music_tracks[music]:
            return
        
        if pygame.mixer.Channel(0).get_busy(): # if already playing music, crossfade between the two
            self.crossfade_music(music)
            return
        
        pygame.mixer.Channel(0).play(pygame.mixer.Sound(self.music_tracks[music]), loops = -1)
    
    def crossfade_music(self, new_music, fade_time = 500):
        """
        Crossfade between the currently playing music and the new music.
        
        Args:
            new_music (str): The key of the new music track to play.
            fade_time (int): The duration of the crossfade in milliseconds.
        """
        pygame.mixer.Channel(0).fadeout(fade_time)
        new_song = pygame.mixer.Sound(self.music_tracks[new_music])
        pygame.mixer.Channel(0).play(new_song, loops = -1, fade_ms = fade_time)
    
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