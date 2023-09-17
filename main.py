# ---------------- INITIALISATION ---------------- #






#Imports
import pygame
from pygame.locals import *
import sys
import math
import time
import csv
import os
import random

pygame.init()

# Read settings
with open("settings.csv") as settings_file:
    settings_reader = csv.reader(settings_file)
    i = -1
    for row in settings_reader:
        i += 1
        if i == 0:
            width = int(row[1])
        if i == 1:
            height = int(row[1])
        if i == 2:
            fps = int(row[1])


game_state = "menu"
# ALWAYS SET THIS BACK TO TRUE WHEN SWITCHING GAME STATE VERY IMPORTANT
objects_initialised = True

two_vec = pygame.math.Vector2
width_ratio = width / 1280
height_ratio = height / 720

FramePerSec = pygame.time.Clock()
last_time = time.time()

debugger_font = pygame.font.SysFont("Arial", 18 * int(height_ratio))
menu_font = pygame.font.SysFont("bahnschrift", int(50 * height_ratio))

pressed_keys = pygame.key.get_pressed()

slidersurface = pygame.display.set_mode((width, height))
displaysurface = pygame.display.set_mode((width, height))
playersurface = pygame.display.set_mode((width, height))
objectsurface = pygame.display.set_mode((width, height))
pygame.display.set_caption("Voxel")


pygame.mixer.music.load('main_menu.wav')






# ---------------- CLASSES ---------------- #






class MenuBox(pygame.sprite.Sprite):

    def __init__(self, res_width, res_height, box_fps, box_x, box_y, box_y_distance, text):
        super().__init__()
        self.box_width = 300 * width_ratio
        self.box_height = 80 * height_ratio

        # Used to set resolution and fps values when boxes clicked to change settings
        self.res_height = res_height
        self.res_width = res_width
        self.box_fps = box_fps

        self.image = pygame.Surface((self.box_width, self.box_height))
        self.image.fill((128, 0, 128))
        self.rect = self.image.get_rect()
        
        self.pos = two_vec((box_x, box_y + box_y_distance))
        self.rect.center = self.pos

        self.text = text

    def menu_display(self):
        menu_text = menu_font.render(self.text, True, pygame.Color("white"))
        text_rect = menu_text.get_rect(center=(self.pos.x, self.pos.y))
        slidersurface.blit(menu_text, text_rect)

    def click_check(self):
        # Check if box is being hovered over
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(displaysurface, (0, 0, 0), self.rect, width = int(5 * width_ratio))
            self.image.fill((73, 182, 24))
        else:
            self.image.fill((30, 30, 30))
        # Check if box has been pressed
        mouse_state = pygame.mouse.get_pressed()
        if mouse_state[0] == 1:
            if self.rect.collidepoint(event.pos):
                time.sleep(0.1)
                return True




class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.width = 60 * width_ratio
        self.height = 60 * height_ratio
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()

        self.pos = two_vec((0, 360 * height_ratio))
        self.new_pos = two_vec((0, 0))
        self.side = "left"

        self.rect.center= self.pos

    def update_line(self):
        # Get mouse position
        mouse_pos = pygame.mouse.get_pos()
        pygame.draw.line(slidersurface, (0, 0, 0), self.pos, mouse_pos, width = 5)

        # x = sqrt(r-(y-a)^2) + b
        # y = sqrt(r-(x-a)^2) + b
        

    def change(self):
        mouse_pos = pygame.mouse.get_pos()
        results = [0] * 3

        # Calculate gradient
        dif_y = (self.pos.y - mouse_pos[1])
        dif_x = (mouse_pos[0] - self.pos.x)
        if dif_x != 0 and dif_y != 0:
            gradient = - dif_y / dif_x
        else:
            gradient = 0.0000001
        
        # Go to the side being pointed at by finding intercepts
        if self.side == "left":
            y_intercept_right = gradient * width + self.pos.y
            x_intercept_top = - self.pos.y / gradient
            x_intercept_bottom = (height - self.pos.y) / gradient

            results[0] = go_right(y_intercept_right)
            results[1] = go_top(x_intercept_top)
            results[2] = go_bottom(x_intercept_bottom)


        elif self.side == "right":
            y_intercept_left = self.pos.y - gradient * width
            x_intercept_top = - y_intercept_left / gradient
            x_intercept_bottom = (height - y_intercept_left) / gradient

            results[0] = go_left(y_intercept_left)
            results[1] = go_top(x_intercept_top)
            results[2] = go_bottom(x_intercept_bottom)


        elif self.side == "top":
            y_intercept_left = - gradient * self.pos.x
            y_intercept_right = gradient * width + y_intercept_left
            x_intercept_bottom = (height - y_intercept_left) / gradient

            results[0] = go_left(y_intercept_left)
            results[1] = go_right(y_intercept_right)
            results[2] = go_bottom(x_intercept_bottom)


        elif self.side == "bottom":
            y_intercept_left = height - gradient * self.pos.x
            y_intercept_right = gradient * width + y_intercept_left
            y_intercept_top = - y_intercept_left / gradient

            results[0] = go_left(y_intercept_left)
            results[1] = go_right(y_intercept_right)
            results[2] = go_top(y_intercept_top)


        self.new_results(results)  
        self.pos = two_vec((self.new_pos.x, self.new_pos.y))
        self.rect.center= self.pos

    
    def new_results(self, results):
        for i in results:
            if i:
                self.new_pos.x = i[0]
                self.new_pos.y = i[1]
                self.side = i[2]



class Object(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.width = random.randint(30, 100) * width_ratio
        self.height = random.randint(30, 100) * height_ratio
        self.image = pygame.Surface((self.width, self.height))

        colour1 = random.randint(0, 255)
        colour2 = random.randint(0, 255)
        colour3 = random.randint(0, 255)
        self.image.fill((colour1, colour2, colour3))
        self.rect = self.image.get_rect()

        self.pos = two_vec((640 * width_ratio, 360 * height_ratio))
        self.velocity = two_vec((random.randint(4, 10) * width_ratio, random.randint(4, 10) * height_ratio))

        self.rect.center = self.pos

    def update_pos(self):
        self.pos += self.velocity * dt

        # angle = 20
        # self.image = pygame.transform.rotate(objectsurface, angle)
        # self.rect = self.image.get_rect()
        
        # Bounce off edges of screen
        if round(self.pos.x + (self.width / 2)) >= width or round(self.pos.x - (self.width / 2)) <= 0:
            self.velocity.x = - self.velocity.x
        if round(self.pos.y + (self.height / 2)) >= height or round(self.pos.y - (self.height / 2)) <= 0:
            self.velocity.y = - self.velocity.y
        
        self.rect.center = self.pos


                

    
	
# ---------------- FUNCTIONS ---------------- #






def display_fps():
    fps = str(int(FramePerSec.get_fps()))
    fps_text = debugger_font.render(fps, True, pygame.Color("coral"))
    return fps_text



def exit_menu(state):
    # Return objects initialised as True, state for the menu to return to and flag to decide if it should return to settings
    if pressed_keys[K_ESCAPE]:
        time.sleep(0.1)
        # Return in main menu
        if state == "settings":
            return True, "main", False
        elif state == "resolution" or state == "fps":
            return True, "settings", True
        # Return to main menu from level
        elif state == "level":
            return True, "menu", False


def sprites_display(sprite_group):
    # Draw boxes and text
    sprite_group.draw(displaysurface)
    for i in sprite_group:
        i.menu_display()


def file_change(file, option, width, height, fps, current_level):
    # Rewrite data in settings.csv or current_level.csv
    file_read = csv.reader(open(file))
    lines = list(file_read)
    if option == "settings":
        lines[0][1] = str(width)
        lines[1][1] = str(height)
        lines[2][1] = str(fps)
    elif option == "level":
        lines[0][0] = str(current_level + 1)
    file_write = csv.writer(open(file, "w+", newline = ""))
    file_write.writerows(lines)

    if option == "settings":
        pygame.quit()
        sys.exit()
    

def gradient_display(display, left_colour, right_colour, surface_rect):
    try:
        colour_rect = pygame.Surface(( 2, 2 ))
        pygame.draw.line(colour_rect, left_colour,  ( 0,0 ), ( 0,1 ))
        pygame.draw.line(colour_rect, right_colour, ( 1,0 ), ( 1,1 ))
        # Stretch lines as required
        colour_rect = pygame.transform.smoothscale(colour_rect, (surface_rect.width, surface_rect.height))
        display.blit(colour_rect, surface_rect)
    except ValueError:
        pass


def go_left(intercept):
    if intercept >= 0 and intercept <= height:
        return 0, intercept, "left"


def go_right(intercept):
    if intercept >= 0 and intercept <= height:
        return width, intercept, "right"


def go_top(intercept):
    if intercept >= 0 and intercept <= width:
        return intercept, 0, "top"

def go_bottom(intercept):
    if intercept >= 0 and intercept <= width:
        return intercept, height, "bottom"




	

# ---------------- MAIN PROGRAM ---------------- #






# ---------------- CONSTANT LOOP ---------------- #


while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if game_state == "level":
                    player.change()

    # Set delta time for framerate
    dt = time.time() - last_time
    dt *= 60
    last_time = time.time()

    # Get the current pressed keys
    pressed_keys = pygame.key.get_pressed()


    # ---------------- MENU LOOP ---------------- #


    if game_state == "menu":
        # Run things to initialise only once
        if objects_initialised == True:
            #Play music
            pygame.mixer.music.play(-1)

            # Set menu state to either main menu or settings menu
            menu_state = "main"
            if 'settings_check' in globals():
                if settings_check:
                    menu_state = "settings"

            # Set gradient background information
            grad_colour1 = 255
            grad_colour2 = 12
            grad_flag = "down"

            # Set logo information
            logo_width = 1302 * 0.4 * width_ratio
            logo_height = 628 * 0.4 * height_ratio

            logo_image = pygame.image.load("logo_transparent_3.png")
            logo_image = pygame.transform.rotozoom(logo_image, 0, 0.4 * width_ratio)

            # Box positions and distance between boxes
            box_x = 640 * width_ratio
            box_y = 240 * height_ratio
            box_y_distance = 100 * height_ratio

            # Main menu boxes
            play_box = MenuBox(0, 0, 0, box_x, box_y, box_y_distance, "Play")
            create_box = MenuBox(0, 0, 0, box_x, box_y, box_y_distance * 2, "Create")
            settings_box = MenuBox(0, 0, 0, box_x, box_y, box_y_distance * 3, "Settings")
            exit_box = MenuBox(0, 0, 0, box_x, box_y, box_y_distance * 4, "Exit")

            # Settings boxes
            resolution_box = MenuBox(0, 0, 0, box_x, box_y, box_y_distance, "Resolution")
            fps_box = MenuBox(0, 0, 0, box_x, box_y, box_y_distance * 2, "FPS")

            # Resolution boxes
            box_y = 0
            nhd_box = MenuBox(640, 360, 0, box_x, box_y, box_y_distance * 2, "640 x 360")
            hd_box = MenuBox(1280, 720, 0, box_x, box_y, box_y_distance * 3, "1280 x 720")
            fhd_box = MenuBox(1920, 1080, 0, box_x, box_y, box_y_distance * 4, "1920 x 1080")
            qhd_box = MenuBox(2560, 1440, 0, box_x, box_y, box_y_distance * 5, "2560 x 1440")
            uhd_box = MenuBox(3840, 2160, 0, box_x, box_y, box_y_distance * 6, "3840 x 2160")

            # FPS boxes
            box_y = 0
            thirty = MenuBox(0, 0, 30, box_x, box_y, box_y_distance * 2, "30")
            fourty_five = MenuBox(0, 0, 45, box_x, box_y, box_y_distance * 3, "45")
            sixty = MenuBox(0, 0, 60, box_x, box_y, box_y_distance * 4, "60")
            hundred_fourty_four = MenuBox(0, 0, 144, box_x, box_y, box_y_distance * 5, "144")
            two_hundred_fourty = MenuBox(0, 0, 240, box_x, box_y, box_y_distance * 6, "240")

            menu_sprites = pygame.sprite.Group()
            settings_sprites = pygame.sprite.Group()
            resolution_sprites = pygame.sprite.Group()
            fps_sprites = pygame.sprite.Group()

            menu_sprites.add(play_box)
            menu_sprites.add(create_box)
            menu_sprites.add(settings_box)
            menu_sprites.add(exit_box)
            
            settings_sprites.add(resolution_box)
            settings_sprites.add(fps_box)

            resolution_sprites.add(nhd_box)
            resolution_sprites.add(hd_box)
            resolution_sprites.add(fhd_box)
            resolution_sprites.add(qhd_box)
            resolution_sprites.add(uhd_box)
            
            fps_sprites.add(thirty)
            fps_sprites.add(fourty_five)
            fps_sprites.add(sixty)
            fps_sprites.add(hundred_fourty_four)
            fps_sprites.add(two_hundred_fourty)

            objects_initialised = False

        # Display changing gradient background
        if grad_flag == "down":
            if grad_colour1 > 12:
                grad_colour1 -= 0.5 * dt
                grad_colour2 += 0.5 * dt
                # print("colour1: " + str(grad_colour1) + "\n" + "colour2: " + str(grad_colour2))
            else:
                grad_flag = "up"
        elif grad_flag == "up":
            if grad_colour1 < 255:
                grad_colour1 += 0.5 * dt
                grad_colour2 -= 0.5 * dt
                # print("colour1: " + str(grad_colour1) + "\n" + "colour2: " + str(grad_colour2))
            else:
                grad_flag = "down"

        displaysurface.fill(( 0,0,0 ))
        gradient_display(displaysurface, (12, grad_colour1, 12), (12, grad_colour2, 12), pygame.Rect( 0, 0, width, height))

        # Display logo
        displaysurface.blit(logo_image, (width / 2 - logo_width / 2, height / 5 - logo_height / 2))


        if menu_state == "main":
            sprites_display(menu_sprites)

            # Check if boxes clicked
            if play_box.click_check():
                objects_initialised = True
                game_state = "level"
            elif create_box.click_check():
                pass
            elif settings_box.click_check():
                menu_state = "settings"
            elif exit_box.click_check():
                pygame.quit()
                sys.exit()

        elif menu_state == "settings":
            sprites_display(settings_sprites)

            # Check if boxes clicked
            if resolution_box.click_check():
                menu_state = "resolution"
            elif fps_box.click_check():
                menu_state = "fps"

        elif menu_state == "resolution":
            # Flag used to set menu_state when initialising
            settings_check = True
            sprites_display(resolution_sprites)
            
            # Check if boxes clicked
            for box in resolution_sprites:
                if box.click_check():
                    width = box.res_width
                    height = box.res_height
                    file_change("settings.csv", "settings", width, height, fps, 0)

        elif menu_state == "fps":
            # Flag used to set menu_state when initialising
            settings_check = True
            sprites_display(fps_sprites)

            # Check if boxes clicked
            for box in fps_sprites:
                if box.click_check():
                    fps = box.box_fps
                    file_change("settings.csv", "settings", width, height, fps, 0)
        
        # Exit to previous menu if escape pressed
        exit_check = exit_menu(menu_state)
        if exit_check != None:
            # INITIALISING AGAIN IS NOT NEEDED WITHIN THE MENU
            # objects_initialised = exit_check[0]
            menu_state = exit_check[1]
            settings_check = exit_check[2]


    # ---------------- LEVEL LOOP ---------------- #

            
    elif game_state == "level":
        # Run things to initialise only once
        if objects_initialised == True:
            #Stop music
            pygame.mixer.music.stop()

           
            # -------- Sprites -------- #
            player = Player()
            player_sprites = pygame.sprite.Group()
            player_sprites.add(player)


            # Create objects
            object_sprites = pygame.sprite.Group()
            num_objects = 5
            for i in range(num_objects):
                object = Object()
                object_sprites.add(object)


            objects_initialised = False


        # -------- Background and slider -------- #
        
                
        # White background
        displaysurface.fill((255, 255, 255))
        # Display FPS in top right
        displaysurface.blit(display_fps(), (width - (width // 21), 0))


        # -------- Exit back to menu -------- #


        exit_check = exit_menu(game_state)
        if exit_check != None:
            objects_initialised = exit_check[0]
            game_state = exit_check[1]


        player.update_line()

        for object_i in object_sprites:
            object_i.update_pos()
        
        
        # -------- Display sprites and update -------- #
        
        player_sprites.draw(playersurface)
        object_sprites.draw(objectsurface)
    

    pygame.display.update()
    FramePerSec.tick(fps)
