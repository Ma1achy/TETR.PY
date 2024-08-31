import pygame

def play_t_spin_sound():
    pygame.mixer.music.load("SE/t_spin.wav")
    pygame.mixer.music.set_volume(0.20)
    pygame.mixer.music.play()