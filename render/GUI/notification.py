from render.GUI.font import Font
import pygame
import re
import math
from utils import load_image, align_top_left, ease_out_back_interpolate, smoothstep_interpolate, ease_out_elastic_interpolate
from app.core.sound.sfx import SFX

class Notification():
    def __init__(self, surface, message, Timing, Sound, type, RENDER_SCALE = 1):
        
        self.remove = False
        
        self.surface = surface
        self.RENDER_SCALE = RENDER_SCALE
        
        self.Timing = Timing
        self.Sound = Sound
        
        self.message = message
        self.font = Font('hun2', int(20 * self.RENDER_SCALE))
        self.shadow_radius = int(3 * self.RENDER_SCALE)
        
        self.max_width = int(400 * self.RENDER_SCALE)
        self.image_width = int(40 * self.RENDER_SCALE)
        self.image_padding = int(10 * self.RENDER_SCALE)
        
        self.type = type
        
        if self.type == "warning":
            self.image_path = "resources/GUI/warning.png"
            self.border_colour = "#FFC600"
            self.notify_sound = SFX.Notify5
            
        self.render()
        
        self.height = self.notification_surface.get_height()
        self.y_position = self.surface.get_height() + self.height
        
        self.default_x_position = self.surface.get_width() + - self.notification_surface.get_width() - int(20 * self.RENDER_SCALE) 
        self.offscreen_x_position = self.surface.get_width() 
        
        self.animate_appear = False
        self.animate_disappear = False
        
        self.appear_time = 0.75
        self.disappear_time = 0.5
        
        self.appear_timer = 0
        self.disappear_timer = 0
        
        self.time = 0
        self.maxium_lifetime = 4
        
        self.animate_push_up = False
        self.target_y = 0
        self.push_up_timer = 0
        self.push_up_time = 0.5
        
        self.alpha = 255
        self.play_appear_sound = False
        
    def render(self):
        """
        Render a tooltip
        
        args:
            tooltip (str): The tooltip to render
        """
        text = self.__wrap_text(self.message, self.font.font, self.max_width)
        
        if text is None:
            return pygame.Surface((1, 1), pygame.HWSURFACE|pygame.SRCALPHA)
        
        height = 0
        
        for line in text:
            height += self.font.font.size(line)[1]
        
        self.notification_surface = pygame.Surface((self.max_width + self.image_width + self.image_padding * 3, height + int(10 * self.RENDER_SCALE) + self.image_padding * 2), pygame.HWSURFACE|pygame.SRCALPHA)
        self.notification_surface.fill((8, 8, 8, 200))
        
       
        pygame.draw.rect(self.notification_surface, self.border_colour, self.notification_surface.get_rect(), math.ceil(2 * self.RENDER_SCALE))
        
        for i, line in enumerate(text):
            self.font.draw(self.notification_surface, line, "#ffffff", 'left_top', self.image_padding * 2 + self.image_width , i * self.font.font.size(line)[1] + self.image_padding)
        
        self.render_image()
        
    def render_image(self):
        """
        Render the image on the button
        """
        image = load_image(self.image_path)     
        
        aspect_ratio = image.get_width() / image.get_height()
        new_height = int(self.image_width * aspect_ratio)

        image = pygame.transform.smoothscale(image, (self.image_width, new_height))
        image_rect = align_top_left(self.notification_surface.get_rect(), image.get_width(), image.get_height(), self.image_padding, self.image_padding)
        self.notification_surface.blit(image, image_rect.topleft)
        
    def __strip_tags(self, text):
        """
        Strip colour tags from the text
        
        args:
            text (str): The text to strip the tags from
        """
        tag_pattern = r"\[colour=#[0-9A-Fa-f]{6}\]|\[\/colour\]"
        return re.sub(tag_pattern, "", text)

    def __wrap_text(self, text, font, max_width):
        """	
        Wrap text to fit inside a given width
        
        args:
            text (str): The text to wrap
            font (pygame.font.Font): The font to use
            max_width (int): The maximum width of the text
        """
        if text is None:
            return
        
        words = re.split(r"(\s+)", text)
        lines = []
        current_line = ""

        for word in words:
            stripped_word = self.__strip_tags(current_line + word)
            
            if font.size(stripped_word.strip())[0] > max_width:
                
                if font.size(word.strip())[0] > max_width:
                    
                    while font.size(word.strip())[0] > max_width:  # Split the word if it's too long
                        for i in range(1, len(word) + 1):
                            if font.size(word[:i].strip())[0] > max_width - font.size(current_line.strip())[0]:
            
                                lines.append(current_line.strip() + word[:i-1])
                                word = word[i-1:]
                                current_line = ""
                                break
                            
                    current_line += word
                else:
                    lines.append(current_line.strip())   # Add the current line to lines and start a new line with the word
                    current_line = word
            else:
                current_line += word

        if current_line:
            lines.append(current_line.strip())

        return lines
    
    def update(self):
        self.count_time_alive()
        self.do_animate_appear()
        self.do_animate_disappear()
        self.do_animate_push_up()
        self.play_sound()
        
        self.draw()

    def play_sound(self):
        if not self.play_appear_sound:
            return
        
        self.play_appear_sound = False
        self.Sound.sfx_queue.append(self.notify_sound)
        
    def count_time_alive(self):
        if self.animate_appear or self.animate_disappear:
            return
         
        self.time += self.Timing.frame_delta_time 
        
        if self.time >= self.maxium_lifetime:
            self.start_disappear_animation()
            
    def draw(self):
        self.surface.blit(self.notification_surface, (self.x_position, self.y_position))
        
    def start_appear_animation(self):
        self.animate_appear = True
        
    def start_disappear_animation(self):
        self.animate_disappear = True
        
    def do_animate_appear(self):
        if not self.animate_appear:
            return
        
        self.appear_timer += self.Timing.frame_delta_time
        
        progress = self.appear_timer / self.appear_time
        progress = max(0, min(1, progress))
        
        self.x_position = ease_out_elastic_interpolate(self.offscreen_x_position, self.default_x_position, progress, 3.5, 0.2)
        
        if progress >= 1:
            self.animate_appear = False
            self.appear_timer = 0
            self.x_position = self.default_x_position
            self.play_appear_sound = True
            
    def do_animate_disappear(self):
        if not self.animate_disappear:
            return
        
        self.disappear_timer += self.Timing.frame_delta_time
        
        progress = self.disappear_timer / self.disappear_time
        progress = max(0, min(1, progress))
        
        self.alpha = smoothstep_interpolate(255, 0, progress)
        self.notification_surface.set_alpha(self.alpha)
        self.x_position = smoothstep_interpolate(self.default_x_position, self.offscreen_x_position, progress)
        
        if progress >= 1:
            self.animate_disappear = False
            self.disappear_timer = 0
            self.remove = True
        
    def start_push_up_animation(self):
        self.animate_push_up = True
    
    def do_animate_push_up(self):
        if not self.animate_push_up:
            self.y_position = self.target_y
            return
        
        self.push_up_timer += self.Timing.frame_delta_time
        
        progress = self.push_up_timer / self.push_up_time
        progress = max(0, min(1, progress))
        
        self.y_position = ease_out_back_interpolate(self.y_position, self.target_y, progress)
        
        if progress >= 1:
            self.animate_push_up = False
            self.push_up_timer = 0
            self.y_position = self.target_y
        
        
        