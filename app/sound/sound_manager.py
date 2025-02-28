import pygame
from app.sound.music import Music
from app.sound.sfx import SFX
from app.sound.sound import Sound
from app.core.timing import Timing
import os
from app.instance.engine.four import RNG
import random
import re
import math
from app.core.config_manager import AudioSettings
from app.utils import Vec3

class SoundManager():
    def __init__(self, Sound:Sound, Timing:Timing, RenderStruct):
        """
        The SoundManager class manages handles the playback and looping of music, the playback of SFX and their stero panning,
        and the volume control of both music and SFX.
        
        args:
            Sound (Sound): The Sound object containing the music and SFX output streams.
            Timing (Timing): The timing information and constants.
            RenderStruct (StructRender): The render information and constants.
        """
        self.Sound = Sound
        self.Timing = Timing
        self.RenderStruct = RenderStruct
        
        self.paused = False
        self.mute_when_hidden = False
        self.disable_all_sound = False
        
        self.music_tracks = {
            Music.CHK_019   : {"path": "resources/sound/music/CHK-019 - Aerial City (Chika) - Interface.mp3",                        "loop": (11796,    92554) },    
            Music.KMY_090   : {"path": "resources/sound/music/KMY-090 - To The Limit (Kamiya) - Interface.mp3",                      "loop": (1229,     90522) },
            Music.TKY_051   : {"path": "resources/sound/music/TKY-051 - The Great Eastern Expedition (Takayuki) - Interface.mp3",    "loop": (4620,     210601)},
            Music.KMK_048   : {"path": "resources/sound/music/KMK-048 - Morning Sun (Kamoking) - Interface.mp3",                     "loop": (1970,     65817) },
            Music.MRR_051   : {"path": "resources/sound/music/MRR-051 - In Sorrow And Pains (Mirera) - Interface.mp3",               "loop": (3499,     98534) },
            Music.KVX_016   : {"path": "resources/sound/music/KVX-016 - Peircing Wind (KVK) - Calm.mp3",                             "loop": (1263,     136789)},
            Music.CHK_016   : {"path": "resources/sound/music/CHK-016 - Inorimichite (Chika) - Calm .mp3",                           "loop": (15646,    197331)},
            Music.CHK_038   : {"path": "resources/sound/music/CHK-038 - Wind Trail (Chika) - Calm.mp3",                              "loop": (10551,    224841)},
            Music.THT_037   : {"path": "resources/sound/music/THT-037 - Muscat And White Dishes (Takahashi Takashi) - Calm.mp3",     "loop": (32106,    160106)},
            Music.THT_042   : {"path": "resources/sound/music/THT-042 - Summer Sky And Homework (Takahashi Takashi) - Calm.mp3",     "loop": (18701,    130708)},
            Music.YKW_055   : {"path": "resources/sound/music/YKW-055 - Success Story Akiko (Shioyama) - Interface.mp3",             "loop": (24543,    102941)},
            Music.KMK_040   : {"path": "resources/sound/music/KMK-040 - Classy Cat (Kamoking) - Interface.mp3",                      "loop": (31985,    95979) },
            Music.CHK_055   : {"path": "resources/sound/music/CHK-055 - Akindo (Chika) - Calm.mp3",                                  "loop": (1175,     113354)},
            Music.LSD_040   : {"path": "resources/sound/music/LSD-040 - Philosophy (L-Side) - Interface.mp3",                        "loop": (2868,     116315)},
            Music.ABM_047   : {"path": "resources/sound/music/ABM-047 - Rainbow Of The Night (Aiba Makoto) - Calm.mp3",              "loop": (46278,    116480)},
            Music.CHK_026   : {"path": "resources/sound/music/CHK-026 - White Calabash (Chika) - Special.mp3",                       "loop": (14462,    136727)},
            Music.FNK_040   : {"path": "resources/sound/music/FNK-040 - Smoke (Fujinawa Kazuhiko) - Interface.mp3",                  "loop": (28735,    139135)},
            Music.OMG_040   : {"path": "resources/sound/music/OMG-040 - Lover's Song (Omegane) - Interface.mp3",                     "loop": (14316,    47748) },
            Music.KMK_053   : {"path": "resources/sound/music/KMK-053 - Step On The Scarlet Soil (Kamoking) - Calm.mp3",             "loop": (43700,    125991)},
            Music.JGM_044   : {"path": "resources/sound/music/JGM-044 - Hanging Out In Tokyo (Meesan) - Calm.mp3",                   "loop": (38452,    144039)},
            Music.KMK_033   : {"path": "resources/sound/music/KMK-033 - Backwater (Kamoking) - Battle.mp3",                          "loop": (1784,     113993)},
            Music.KMK_024   : {"path": "resources/sound/music/KMK-024 - Burning Heart (Kamoking) - Battle.mp3",                      "loop": (0,        76803) },
            Music.KMK_038   : {"path": "resources/sound/music/KMK-038 - Storm Spirit (Kamoking) - Battle.mp3",                       "loop": (35611,    119605)},
            Music.KMK_047   : {"path": "resources/sound/music/KMK-047 - Ice Eyes (Kamoking) - Battle.mp3",                           "loop": (8324,     94053) },
            Music.TMK_060   : {"path": "resources/sound/music/TMK-060 - The Time Is Now (Tomoki) - Battle.mp3",                      "loop": (5460,     112125)},
            Music.ABM_048   : {"path": "resources/sound/music/ABM-048 - Prism (Aiba Makoto) - Calm.mp3",                             "loop": (0,        92120) },
            Music.MKK_033   : {"path": "resources/sound/music/MKK-033 - Risky Area (Mikiya Komaba) - Battle.mp3",                    "loop": (36479,    321723)},
            Music.SDM_016   : {"path": "resources/sound/music/SDM-016 - Winter Satellite (Sudo Mikaduki) - Calm.mp3",                "loop": (23754,    172932)},
            Music.YOS_016   : {"path": "resources/sound/music/YOS-016 - First Snow (Yoshi) - Calm.mp3",                              "loop": (21941,    144787)},
            Music.CHK_047   : {"path": "resources/sound/music/CHK-047 - Main Street (Chika) - Calm.mp3",                             "loop": (17737,    200955)},
            Music.KMK_036   : {"path": "resources/sound/music/KMK-036 - Over The Horizon (Kamoking) - Battle.mp3",                   "loop": (10369,    66351) },
            Music.KMK_017   : {"path": "resources/sound/music/KMK-017 - Burning Spirit, Awakening Soul (Kamoking) - Battle.mp3",     "loop": (14826,    69678) },
            Music.KMK_032   : {"path": "resources/sound/music/KMK-032 - Maze Of The Abyss (Kamoking) - Battle.mp3",                  "loop": (687,      118641)},
            Music.KMK_004   : {"path": "resources/sound/music/KMK-004 - Samurai Sword (Kamoking) - Battle.mp3",                      "loop": (6572,     112160)},
            Music.KMK_041   : {"path": "resources/sound/music/KMK-041 - Super Machine Soul (Kamoking) - Battle.mp3",                 "loop": (9000,     104999)},
            Music.KMK_039   : {"path": "resources/sound/music/KMK-039 - Universe 5239 (Kamoking) - Battle.mp3",                      "loop": (15533,    98651) },
            Music.KMK_051   : {"path": "resources/sound/music/KMK-051 - Ultra Super Heroes (Kamoking) - Battle.mp3",                 "loop": (161,      105112)},
            Music.KMK_018   : {"path": "resources/sound/music/KMK-018 - Hyper Velocity (Kamoking) - Special.mp3",                    "loop": (21293,    117284)},
            Music.OMG_019   : {"path": "resources/sound/music/OMG-019 - Twenty-First Century People (Omegane) - Calm.mp3",           "loop": (0,        131816)},
            Music.OMG_016   : {"path": "resources/sound/music/OMG-016 - Waiting For Spring To Come (Omegane) - Calm.mp3",            "loop": (5805,     165802)},
            Music.NBH_022   : {"path": "resources/sound/music/NBH-022 - Go Go Go Summer (Nobuhamu) - Calm.mp3",                      "loop": (11112,    75455) },
            Music.NHR_040   : {"path": "resources/sound/music/NHR-040 - Lonely Journey (Naoki Hirai) - Calm.mp3",                    "loop": (105,      145259)},
            Music.CHK_004   : {"path": "resources/sound/music/CHK-004 - Young Leaves (Chika) - Calm.mp3",                            "loop": (10346,    189230)},
            Music.OMG_051   : {"path": "resources/sound/music/OMG-051 - Confession (Omegane) - Calm.mp3",                            "loop": (0,        80533) },
            Music.TTM_055   : {"path": "resources/sound/music/TTM-055 - Amazing Everyday (Tsutomu) - Calm.mp3",                      "loop": (43645,    136733)},
            Music.CHK_009   : {"path": "resources/sound/music/CHK-009 - Asphalt (Chika) - Calm.mp3",                                 "loop": (5606,     75310) },
            Music.CHK_048   : {"path": "resources/sound/music/CHK-048 - By the Sunlit Window (Chika) - Calm.mp3",                    "loop": (26179,    91752) },
            Music.CHK_053   : {"path": "resources/sound/music/CHK-053 - Origin (Chika) - Calm.mp3",                                  "loop": (135001,   322927)},
            Music.CHK_041   : {"path": "resources/sound/music/CHK-041 - Cherry Blossom Season (Chika) - Calm.mp3",                   "loop": (0,        338556)},
            Music.CHK_021   : {"path": "resources/sound/music/CHK-021 - Raindrops (Chika) - Calm.mp3",                               "loop": (15034,    121613)},
            Music.CHK_014   : {"path": "resources/sound/music/CHK-014 - Entrance Wreath (Chika) - Calm.mp3",                         "loop": (3158,     87492) },
            Music.CHK_057   : {"path": "resources/sound/music/CHK-057 - Peace Message (Chika) - Special.mp3",                        "loop": (22056,    242474)},
        }
        
        self.sound_effects = {
            SFX.MenuHover    : "resources/sound/SFX/menu_hover.ogg",
            SFX.MenuTap      : "resources/sound/SFX/menu_tap.ogg",
            SFX.MenuBack     : "resources/sound/SFX/menu_back.ogg",
            SFX.MenuClick    : "resources/sound/SFX/menu_click.ogg",
            SFX.MenuConfirm  : "resources/sound/SFX/menu_confirm.ogg",
            SFX.MenuHit1     : "resources/sound/SFX/menu_hit_1.ogg",
            SFX.MenuHit2     : "resources/sound/SFX/menu_hit_2.ogg",
            SFX.MenuHit3     : "resources/sound/SFX/menu_hit_3.ogg",
            SFX.Notify1      : "resources/sound/SFX/notify_1.ogg",
            SFX.Notify2      : "resources/sound/SFX/notify_2.ogg",
            SFX.Notify3      : "resources/sound/SFX/notify_3.ogg",
            SFX.Notify4      : "resources/sound/SFX/notify_4.ogg",
            SFX.Notify5      : "resources/sound/SFX/notify_5.ogg",
            SFX.Notify6      : "resources/sound/SFX/notify_6.ogg",
            SFX.OverlayOpen  : "resources/sound/SFX/overlay_open.ogg",
            SFX.OverlayClose : "resources/sound/SFX/overlay_close.ogg",
            SFX.Move         : "resources/sound/SFX/move.ogg",
        }
        
        self.__populate_music_info()
         
        self.calm_songs      = [song for song in self.music_tracks if self.music_tracks[song]["type"] == "Calm"]
        self.battle_songs    = [song for song in self.music_tracks if self.music_tracks[song]["type"] == "Battle"]
        self.interface_songs = [song for song in self.music_tracks if self.music_tracks[song]["type"] == "Interface"]
        self.special_songs   = [song for song in self.music_tracks if self.music_tracks[song]["type"] == "Special"]
         
        self.num_channels = 16
        self.frequency = 44100
        self.bitsize = -16
        self.buffer_size = 1024
    
        self.initialized = True
        self.__init_pygame_mixer()
        self.set_number_of_channels(self.num_channels)
        self.__load_sfx()
        
        self.loop_start = 0  
        self.loop_end = 0   
        self.randomiser = RNG(seed = random.randint(0, 2**32 - 1))
        
        self.music_percentage = -1
        self.sfx_percentage = -1
        self.max_music_volume = 0
        self.max_sfx_volume = 0
        self.pause_start_time = 0
        
        self.__update_music_volume()
        self.__update_sfx_volume()
        
        self.music_position = 0
    
    # ---------------------------------------------------------- MUSIC META DATA ----------------------------------------------------------
     
    def __populate_music_info(self):
        """
        Populates the music tracks dictionary with type, artist, title, and track number.
        """
        for key, track in self.music_tracks.items():
            info = self.__extract_music_info(track["path"])
            self.music_tracks[key].update(info)
    
    def __extract_music_info(self, file_path):
        """
        Extracts type, artist, title, and track number from the file path using regex.
        
        args:
            file_path (str): The path to the music file.
            
        returns:
            dict: A dictionary containing the extracted type, artist, title, and track number.
        """
        pattern = re.compile(r"resources/sound/music/(?P<code>[A-Z]+-\d+) - (?P<title>.+?) \((?P<artist>.+?)\) - (?P<type>.+)\.mp3")
        match = pattern.search(file_path)
        
        if match:
            return {
                "type": match.group("type").strip(),
                "artist": match.group("artist").strip(),
                "title": match.group("title").strip(),
                "track_number": match.group("code").strip()
            }
        else:
            return {
                "type": "",
                "artist": "",
                "title": "",
                "track_number": ""
            }
            
    def get_song_artist_and_title(self, song):
        """
        Obtain the artist and title of a music track in the format "artist - title".
        
        args:
            song (Music): The music track to obtain the artist and title from.
        
        returns:
            "artist - title" (str): The artist and title of the music track.
        """
        if song is Music.RANDOM:
            name = "random"
        elif song is Music.RANDOM_CALM:
            name = "random: calm"
        elif song is Music.RANDOM_BATTLE:
            name = "random: battle"
        elif song is Music.RANDOM_INTERFACE:
            name = "random: interface"
        elif song is Music.RANDOM_SPECIAL:
            name = "random: special"
        else:
            if song not in self.music_tracks.keys():
                return "null - null"
            
            name = f"{self.music_tracks[song]["artist"].lower()} - {self.music_tracks[song]["title"].lower()}"
            
        return name
    
    # --------------------------------------------------------- SFX LOADING ---------------------------------------------------------
                
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
    
    # ------------------------------------------------------- AUDIO PLAYBACK --------------------------------------------------------
    
    def quit(self):
        pygame.mixer.quit()

    def set_number_of_channels(self, channels):
        pygame.mixer.set_num_channels(channels)

    def tick(self):
        self.__update_music_position()
        self.__manage_music_playback()
        self.__update_music_volume()
        self.__update_sfx_volume()
        self.__process_queues()
        
    def __process_queues(self):
        
        if AudioSettings.DISABLE_ALL_SOUND:
            self.Sound.music_queue.clear()
            self.Sound.sfx_queue.clear()
            return
        
        if self.Sound.music_queue:
            music = self.Sound.music_queue.popleft()  
            self.__play_music(music)

        if self.Sound.sfx_queue:
            sound = self.Sound.sfx_queue.popleft() 
            sfx, x, y, z = sound
            self.__play_sfx(sfx, x, y, z)
    
    # ------------------------------------------------------ SFX PLAYBACK -----------------------------------------------------------  
    
    def __play_sfx(self, sfx: SFX, x = 0, y = 0, z = 0):
        """
        Play a sound effect if an available channel exists.
        
        args:
            sfx (SFX): The sound effect to play.
            x (int): The x position of the sound effect in screen space.
            y (int): The y position of the sound effect in screen space.
            z (int): The z position of the sound effect in screen space.
        """
        if AudioSettings.DISABLE_ALL_SOUND:
            return
        
        if sfx not in self.sound_effects:
            return
        
        if self.sound_effects[sfx] is None:
            return
        
        channel = pygame.mixer.find_channel()
        if channel:
            left_gain, right_gain = self.calculate_pan(x, y, z)
            left_volume, right_volume = self.calculate_left_right_volume(left_gain, right_gain)
            channel.set_volume(left_volume, right_volume)
            channel.play(self.sound_effects[sfx])
    
    # ------------------------------------------------------ PAN CALCULATION ---------------------------------------------------------
    
    def calculate_left_right_volume(self, left_gain, right_gain):
        left_volume = self.max_sfx_volume * left_gain
        right_volume = self.max_sfx_volume * right_gain

        return left_volume, right_volume
        
    def calculate_pan(self, x, y, z):
        """
        Calculate the pan based on the x, and y position of the sound effect on the screen.
        
        args:
            x (int): The x position of the sound effect in screen space.
            y (int): The y position of the sound effect in screen space.
            z (int): The z position of the sound effect in screen space.
        """ 
        
        if x == 'center':
            x = self.RenderStruct.RENDER_WIDTH / 2
        
        if y == 'center':
            y = self.RenderStruct.RENDER_HEIGHT / 2
            
        x = max(0, min(x / self.RenderStruct.RENDER_WIDTH, 1))
        y = max(0, min(y / self.RenderStruct.RENDER_HEIGHT, 1))
        z = max(0, min(z / self.RenderStruct.MAX_DEPTH, 1))
        
        if AudioSettings.STEREO_BALANCE == 0:
            x = 0.5
            y = 0.5 
                
        audio_source = Vec3(x, 1 - y, z) - Vec3(0.5, 0.5, 0.5)
        
        if audio_source.x != 0 or audio_source.y != 0:
            audio_source.x *= AudioSettings.STEREO_BALANCE / 100
            audio_source.y *= AudioSettings.STEREO_BALANCE / 100
        
        listener_pos = Vec3(0, 0, 0)
        listener_up = Vec3(0, 1, 0)
        listener_forward = Vec3(0, 0, 1)
        
        side = listener_up.cross(listener_forward).normalise()
        
        audio_x = (audio_source - listener_pos).dot(side)
        audio_z = (audio_source - listener_pos).dot(listener_forward)
        
        angle = math.atan2(audio_x, audio_z)
        
        left_gain = math.sqrt(2)/2 * (math.cos(angle) + math.sin(angle))
        right_gain = math.sqrt(2)/2 * (math.cos(angle) - math.sin(angle))
        
        return left_gain**2, right_gain**2
        
    # ------------------------------------------------------ MUSIC PLAYBACK ---------------------------------------------------------
    
    def __play_music(self, song):
        
        music, do_loop = song
        
        if music is Music.NONE:
            pygame.mixer.music.fadeout(500)
            self.Sound.current_music = None
            self.Sound.music_room_listening = False
            return
        
        elif music is Music.RANDOM:
            music = self.__get_random_song()
        
        elif music is Music.RANDOM_CALM:
            music = self.__get_random_calm_song()
            
        elif music is Music.RANDOM_BATTLE:
            music = self.__get_random_battle_song()
        
        elif music is Music.RANDOM_INTERFACE:
            music = self.__get_random_interface_song()
        
        elif music is Music.RANDOM_SPECIAL:
            music = self.__get_random_special_song()
        
        if music not in self.music_tracks:
            return

        music_info = self.music_tracks[music]
        music_path = music_info["path"]
        
        if do_loop:
            loop = music_info["loop"]
        else:
            loop = None

        if not os.path.exists(music_path):
            return

        if self.Sound.current_music == music:
            return
        
        if pygame.mixer.music.get_busy():  # if already playing music, fade out and queue next song
            pygame.mixer.music.fadeout(500)
            pygame.mixer.music.queue(music_path)
            self.__set_current_song(music, loop)
            return

        pygame.mixer.music.load(music_path)
        pygame.mixer.music.play(loops = 0)
        self.__set_current_song(music, loop)
 
    def __set_current_song(self, music, loop):
        self.Sound.current_music = music
        
        if loop is None:
            self.loop_start, self.loop_end = None, None
            return
        
        self.loop_start, self.loop_end = loop
        pygame.time.set_timer(pygame.USEREVENT, self.loop_end)
        
        self.music_position = 0
        self.remaining_time = 0
    
    # ------------------------------------------------------ MUSIC LOOPING -----------------------------------------------------------
    
    def loop_current_song(self, event):
        """
        Handle Pygame events to manage music looping from specified loop points.
        """
        if self.paused or AudioSettings.DISABLE_ALL_SOUND:
            return
        
        pygame.mixer.music.play(loops = 0, start = self.loop_start / 1000.0)
        self.music_position = self.loop_start / 1000.0
        pygame.time.set_timer(pygame.USEREVENT, self.loop_end - self.loop_start) # timer plays loop end - loop start to only play the looped section
        self.set_music_channel_volume(self.loudness_to_log_linear_picewise(AudioSettings.MUSIC_VOLUME, music = True))
    
    def __update_music_position(self):
        """
        Get the current position of the music track.
        """
        if self.Sound.current_music is None or self.Sound.current_music is Music.NONE:
            self.music_position = 0
            return
        
        if self.paused or self.disable_all_sound:
            return
        
        self.music_position += self.Timing.frame_delta_time
        
        if self.music_position >= self.loop_end:
            self.music_position = self.loop_end
    
    # ------------------------------------------------------ MUSIC PLAYBACK MANAGEMENT -------------------------------------------------
    
    def __manage_music_playback(self):
        if self.disable_all_sound == AudioSettings.DISABLE_ALL_SOUND:
            return
        
        self.disable_all_sound = AudioSettings.DISABLE_ALL_SOUND
        
        if self.disable_all_sound:
            self.pause_all_sounds()
            self.disable_music()
        else:
            self.resume_all_sounds()
            self.enable_music()
        
    def enable_music(self):
        """
        Enable music playback.
        """
        self.resume_music()
        
    def disable_music(self):
        """
        Disable music playback.
        """
        self.pause_music()
        
    def toggle_music_mute(self, flag):
        if not AudioSettings.MUTE_WHEN_HIDDEN or AudioSettings.DISABLE_ALL_SOUND:
            return 
        
        if flag == self.mute_when_hidden:
            return
        
        self.mute_when_hidden = flag
        
        if flag:
            self.pause_music()
        else:
            self.resume_music()
    
    # ------------------------------------------------------ MUSIC PAUSE/RESUME ------------------------------------------------------
       
    def pause_music(self):
        """
        Pause the currently playing music.
        """
        if not pygame.mixer.music.get_busy() or self.paused:
            return
    
        self.paused = True   
        self.remaining_time = int(self.loop_end - self.music_position * 1000) # pygame timer uses ms
        
        if self.remaining_time <= 0:
            self.remaining_time = 0
            
        pygame.mixer.music.stop()
        pygame.time.set_timer(pygame.USEREVENT, 0)
        
    def resume_music(self):
        """
        Resume the currently playing music.
        """
        if not self.paused:
            return
    
        self.paused = False
        pygame.mixer.music.play(loops = 0, start = self.music_position)
        pygame.time.set_timer(pygame.USEREVENT, self.remaining_time)
    
    # ------------------------------------------------------ VOLUME CONTROL ---------------------------------------------------------
    
    def loudness_to_log_linear_picewise(self, loudness, min_db = -80, max_db = 0, music = False):
        """
        Convert loudness (0-200%) to a mixed logarithmic and linear scale (0-1.0).
        Volume is logarithmic up to 100% and linear from 100-200%.
        
        args:
            loudness (float): The loudness level (0-200%).
            min_db (float): The minimum decibel value.
            max_db (float): The maximum decibel value.
            music (bool): Whether the volume is for music or SFX.
        
        returns:
            float: The volume in a mixed logarithmic and linear scale (0 - 1.0).
        """
        loudness /= 2
        
        if music:
            factor = 0.2
        else:
            factor = 1.0
            
        if loudness == 0:
            return 0.0

        if loudness <= 50:
            db_value = min_db + (loudness * (max_db - min_db) / 100) * factor
            log_value = (db_value - min_db) / (max_db - min_db)
              
            if log_value <= 0.01:
                log_value = 0.01

            return log_value
    
        return loudness / 100 * factor
    
    # ------------------------------------------------------ MUSIC VOLUME -----------------------------------------------------------
    
    def __update_music_volume(self):
        """
        Update the volume of the music channel.
        """
        if self.music_percentage == AudioSettings.MUSIC_VOLUME:
            return
        
        self.music_percentage = AudioSettings.MUSIC_VOLUME
        self.max_music_volume = self.loudness_to_log_linear_picewise(AudioSettings.MUSIC_VOLUME, music = True)
        self.set_music_channel_volume(self.max_music_volume)
    
    def set_music_channel_volume(self, volume):
        """
        Set the volume for the music channel.
        
        args:
            volume (float): Volume level between 0.0 and 1.0
        """
        pygame.mixer.music.set_volume(volume)
    
    # ------------------------------------------------------ SFX VOLUME -----------------------------------------------------------
      
    def __update_sfx_volume(self):
        """
        Update the volume of the SFX channels.
        """
        
        if self.sfx_percentage == AudioSettings.SFX_VOLUME:
            return
        
        self.sfx_percentage = AudioSettings.SFX_VOLUME
        self.max_sfx_volume = self.loudness_to_log_linear_picewise(AudioSettings.SFX_VOLUME)
        #self.set_sfx_channels_volume(self.max_sfx_volume)
       
    def set_sfx_channels_volume(self, volume):
        """
        Set the volume for all SFX channels.
        
        args:
            volume (float): Volume level between 0.0 and 1.0
        """
        for i in range(0, self.num_channels):
            pygame.mixer.Channel(i).set_volume(volume)
                     
    def set_sound_volume(self, sound_enum, volume):
        """
        Set the volume for a specific SFX
        
        args:
            sound_enum (SFX): SFX enum representing the sound.
            volume (float): Volume level between 0.0 and 1.0
        """
        if isinstance(sound_enum, SFX):
            
            if sound_enum in self.sound_effects:
                self.sound_effects[sound_enum].set_volume(volume)
            else:
                print(f"Sound effect '{sound_enum}' not loaded.")     
                
    def get_sound_volume(self, sound_enum):
        """
        Get the volume for a specific SFX.
        
        args:
            sound_enum (SFX or Music): SFX enum representing the sound.
        """
        if isinstance(sound_enum, SFX):
            
            if sound_enum in self.sound_effects:
                return self.sound_effects[sound_enum].get_volume()
            else:
                print(f"Sound effect '{sound_enum}' not loaded.")
                return None
          
    # ---------------------------------------------------- MUSIC RANDOMISER --------------------------------------------------------
    
    def __get_random_song(self):
        """
        Get a random song from the music tracks.
        
        Returns:
            Music: A random music track.
        """
        songs = list(self.music_tracks.keys())
        songs.remove(self.Sound.current_music) # to prevent the current song from being selected
        return self.randomiser.shuffle_array(songs)[0]
    
    def __get_random_calm_song(self):
        """
        Get a random calm song from the music tracks.
        
        Returns:
            Music: A random calm music track.
        """
        calm_songs = self.calm_songs.copy()

        if self.Sound.current_music in calm_songs:
            calm_songs.remove(self.Sound.current_music)
            
        return self.randomiser.shuffle_array(calm_songs)[0]
    
    def __get_random_battle_song(self):
        """
        Get a random battle song from the music tracks.
        
        Returns:
            Music: A random battle music track.
        """
        battle_songs = self.battle_songs.copy()
        
        if self.Sound.current_music in battle_songs:
            battle_songs.remove(self.Sound.current_music)
            
        return self.randomiser.shuffle_array(battle_songs)[0]
    
    def __get_random_interface_song(self):
        """
        Get a random interface song from the music tracks.
        
        Returns:
            Music: A random interface music track.
        """
        interface_songs = self.interface_songs.copy()
        
        if self.Sound.current_music in interface_songs:
            interface_songs.remove(self.Sound.current_music)
            
        return self.randomiser.shuffle_array(interface_songs)[0]

    def __get_random_special_song(self):
        """
        Get a random special song from the music tracks.
        
        Returns:
            Music: A random special music track.
        """
        special_songs = self.special_songs.copy()
        
        if self.Sound.current_music in special_songs:
            special_songs.remove(self.Sound.current_music)
            
        return self.randomiser.shuffle_array(special_songs)[0]
    
    # ------------------------------------------------------ UTILITY FUNCTIONS ------------------------------------------------------
    
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