import pygame

class SoundManager():
    def __init__(self):
        self.num_channels = 2
        self.frequency = 44100
        self.bitsize = -16
        self.buffer_size = 512
        
    def init_pygame_mixer(self):
        pygame.mixer.init(frequency = self.frequency, size = self.bitsize, channels = self.num_channels, buffer = self.buffer_size, allowedchanges = pygame.AUDIO_ALLOW_FREQUENCY_CHANGE | pygame.AUDIO_ALLOW_CHANNELS_CHANGE)
    
    def pre_init(self):
        pygame.mixer.pre_init(self.frequency, self.bitsize, self.num_channels, self.buffer_size)
        
    def quit(self):
        pygame.mixer.quit()
    
    def stop_all_sounds(self):
        pygame.mixer.stop()
    
    def pause_all_sounds(self):
        pygame.mixer.pause()
    
    def resume_all_sounds(self):
        pygame.mixer.unpause()
    
    def fade_out_all_sounds(self, time):
        pygame.mixer.fadeout(time)
    
    def get_num_channels(self):
        return pygame.mixer.get_num_channels()
    
    def set_number_of_channels(self, channels):
        pygame.mixer.set_num_channels(channels)
    
    def reserve_channel(self, channel):
        pygame.mixer.set_reserved(channel)
        
    def find_unused_channel(self, force = False):
        return pygame.mixer.find_channel(force)
    
    def is_mixer_busy(self):
        return pygame.mixer.get_busy()
    