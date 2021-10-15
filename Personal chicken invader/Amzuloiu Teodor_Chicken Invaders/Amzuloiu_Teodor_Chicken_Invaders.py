# CHICKEN INVADERS - ATM VERSION
import math  
import decimal
import pygame
from pygame.locals import *
import random
import os
import time
from pygame import mixer
from pygame.math import Vector2

pygame.font.init()

#init pygame
pygame.init()


#initializari dimensiuni
WIDTH = 1000
HEIGHT = 800
SHIP_SIZE_SQUARE = 70
ENEMY_SIZE_SQUARE = 70
LASER_DIM = 20

white = (255,255,255)
black = (0,0,0)
red = (255, 0, 0)
green = (0, 155, 0)

difficulty = 'Easy'
dificultate = 1
score = 0
lives = 5
run = True

main_font = pygame.font.SysFont("comicsans", 50)
title_font = pygame.font.SysFont("comicsans", 100)
subtitle_font = pygame.font.SysFont("comicsans", 40)
small_font = pygame.font.SysFont("comicsans", 35)
lost_font = pygame.font.SysFont("comicsans", 80)
small2_font = pygame.font.SysFont("comicsans", 25)

#background_x = 0
FPS = 60
CLOCK = pygame.time.Clock()

#screen set-up
screen=pygame.display.set_mode((WIDTH + 200,HEIGHT))
pygame.display.set_caption("Chicken invaders ATM vERsiOn")

#initializari imagini
background = pygame.transform.scale(pygame.image.load('materiale/background.jpg'),(WIDTH, HEIGHT))
pause_img = pygame.transform.scale(pygame.image.load('materiale/paused.png'),(WIDTH + 200 , HEIGHT))
shiba_player = pygame.transform.scale(pygame.image.load('materiale/player.png'), (SHIP_SIZE_SQUARE,SHIP_SIZE_SQUARE))
cat_enemy = pygame.transform.scale(pygame.image.load('materiale/enemy.png'),(ENEMY_SIZE_SQUARE,ENEMY_SIZE_SQUARE))
cat_enemy2 = pygame.transform.scale(pygame.image.load('materiale/enemy2.png'),(ENEMY_SIZE_SQUARE,ENEMY_SIZE_SQUARE))
cat_enemy3 = pygame.transform.scale(pygame.image.load('materiale/enemy3.png'),(ENEMY_SIZE_SQUARE,ENEMY_SIZE_SQUARE))
cat_enemy4 = pygame.transform.scale(pygame.image.load('materiale/enemy4.png'),(ENEMY_SIZE_SQUARE,ENEMY_SIZE_SQUARE))

laser_player = pygame.transform.scale(pygame.image.load('materiale/laser.png'),(LASER_DIM,LASER_DIM + 10))
laser_enemy = pygame.transform.scale(pygame.image.load('materiale/laser_enemy.png'),(LASER_DIM,LASER_DIM + 10))

#BACKGROUND SOUND
music = pygame.mixer.music.load('materiale/music.mp3')
pygame.mixer.music.play(-1)

#clase
class button():
    def __init__(self, color, x,y,width,height, text=''):
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text

    def draw(self,win,outline=None):
        if outline:
            pygame.draw.rect(win, outline, (self.x-2,self.y-2,self.width+4,self.height+4),0)
            
        pygame.draw.rect(win, self.color, (self.x,self.y,self.width,self.height),0)
        
        if self.text != '':
            font = pygame.font.SysFont('comicsans', 60)
            text = font.render(self.text, 1, (0,0,0))
            win.blit(text, (self.x + (self.width/2 - text.get_width()/2), self.y + (self.height/2 - text.get_height()/2)))

    def isOver(self, pos):
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        screen.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= HEIGHT and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)

class nava:
    COOLDOWN = 30

    def __init__(self, x, y, health=1):
        self.x = x
        self.y = y
        self.health = health
        self.nava_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    
    def draw(self, window):
       screen.blit(self.nava_img, (self.x, self.y))
       for laser in self.lasers:
           laser.draw(screen)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 1
                self.lasers.remove(laser)
                

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x +25, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


class Player(nava):
    def __init__(self, x,y,health=1):
        super().__init__(x,y, health)
        self.nava_img = shiba_player
        self.laser_img = laser_player
        self.mask = pygame.mask.from_surface(self.nava_img)
        self.max_health = health

    #def move_lasers(self, vel, objs):
    #    global score
    #    self.cooldown()
    #    for laser in self.lasers:
    #        laser.move(vel)
    #        if laser.off_screen(HEIGHT):
    #            self.lasers.remove(laser)
    #        else:
    #            for obj in objs:
    #                if  laser.collision(obj):
    #                    objs.remove(obj)
    #                    self.lasers.remove(laser)
    #                    score += 1
    def move_lasers(self, vel, objs):
        global score
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
               for obj in objs:
                    if laser.y - obj.y < ENEMY_SIZE_SQUARE and abs(laser.x - obj.x) < 70 and obj.y > ENEMY_SIZE_SQUARE:
                       objs.remove(obj)
                       self.lasers.remove(laser)
                       score += 1
        
                        

class Enemy(nava):
   SKIN_MAP = {                                     
              "cat1" : (cat_enemy, laser_enemy),
              "cat2" : (cat_enemy2, laser_enemy),
              "cat3" : (cat_enemy3, laser_enemy),
              "cat4" : (cat_enemy4, laser_enemy)
              }    
       
   def __init__(self, x, y, skin, health=1 ): 
         super().__init__(x,y,health)
         self.nava_img, self.laser_img=self.SKIN_MAP[skin]
         self.mask=pygame.mask.from_surface(self.nava_img)
   def move(self, vel):
        self.y +=vel
   
   def move_lasers(self, vel, obj):
        global lives
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif obj.y - laser.y  < LASER_DIM and abs(laser.x - obj.x) < SHIP_SIZE_SQUARE :
                lives -= 1
                self.lasers.remove(laser)

   def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x +25, self.y + ENEMY_SIZE_SQUARE, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

def collide(obj1, obj2):
     #offset_x = obj2.x - obj1.x
     #offset_y = obj2.y - obj1.y
     ### TO DO: alta modalitate
     #return obj1.mask.overlap(obj2.mask, (int(offset_x), int(offset_y))) != None
    # distance = math.sqrt((math.pow(obj1.x - obj2.x,2)) + (math.pow(obj1.y - obj2.x,2)))
     #if distance < 50:
      #  return True
     #return False

     offset = (obj2.x - obj1.x, obj2.y - obj1.y)
     result1 = obj1.mask.overlap(obj2.mask, (int(obj2.x - obj1.x), int(obj2.y - obj1.y)))
     result2 = obj2.mask.overlap(obj1.mask, (int(obj1.x - obj2.x), int(obj1.y - obj2.y)))
     result3 = obj2.mask.overlap(obj1.mask, (int(obj2.x - obj1.x), int(obj2.y - obj1.y)))
     if result1 or result2 or result3:
         return True
     else:
         return False
    #hits = pygame.sprite.groupcollide(obj1, obj2, True, True)
    #if hits:
    #    return True
    #return False
   
    

#functii
def events():
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            pygame.quit()
            quit()

def pause():
    paused = True

    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = False
                elif event.key == pygame.K_q:
                    pygame.quit()
                    quit()
        screen.blit(pause_img, (0,0))
        mesaj_pause = main_font.render("Press SPACE to continue... ",1, white )
        screen.blit(mesaj_pause,((WIDTH + 200)/2 - mesaj_pause.get_width()/2,HEIGHT - 200))

        pygame.display.update()
        CLOCK.tick(5)

 #meniu principal
def game_intro(): 
    intro = True
    greenbutton = button((0,255,0),(WIDTH + 200)/2 - 250/2, 250, 250, 100, 'Start')
    redbutton = button((0,255,0),(WIDTH + 200)/2 - 3*250/2 - 30, 500, 250, 100, 'Difficulty')
    quitbutton = button((0,255,0), (WIDTH + 200)/2 + 250/2 + 30, 500, 250, 100, 'Quit Game')
   
    while intro:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                 pygame.quit()
                 quit()

        screen.fill(white)
        #mesaje pe ecran
        mesaj_1 = title_font.render("Chicken Invaders",1, green)
        mesaj_2 = subtitle_font.render("ATM vERsiOn",1, red)
        screen.blit(mesaj_1,((WIDTH + 200)/2 - mesaj_1.get_width()/2,100))
        screen.blit(mesaj_2,((WIDTH + 200)/2 +150, 100 + mesaj_2.get_height() + mesaj_2.get_height()))
        #end
        #desenarea butoanelor pe ecran
        greenbutton.draw(screen, (0,0,0))
        redbutton.draw(screen, (0,0,0))
        quitbutton.draw(screen, (0,0,0))
        #end
        pygame.display.update()
        CLOCK.tick(FPS)

        for event in pygame.event.get():
            pos = pygame.mouse.get_pos()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if greenbutton.isOver(pos):
                  #  intro = False
                  main()
                if redbutton.isOver(pos):
                    #nivel dificultate
                    dif = True
                    easybutton = button((green),(WIDTH + 200)/2 - 250/2, 250, 250, 100, 'Easy')
                    normalbutton = button((green), (WIDTH + 200)/2 - 250/2, 400, 250, 100, 'Normal')
                    hardbutton = button((green), (WIDTH + 200)/2 - 250/2, 550, 250, 100, 'Hard')
                    while dif:
                        screen.fill(white)
                        mesaj_1 = title_font.render("Chicken Invaders",1, green)
                        mesaj_2 = subtitle_font.render("ATM vERsiOn",1, red)
                        screen.blit(mesaj_1,((WIDTH + 200)/2 - mesaj_1.get_width()/2,100))
                        screen.blit(mesaj_2,((WIDTH + 200)/2 +150, 100 + mesaj_2.get_height() + mesaj_2.get_height()))
                        easybutton.draw(screen, (0,0,0))
                        normalbutton.draw(screen, (0,0,0))
                        hardbutton.draw(screen, (0,0,0))
                        pygame.display.update()
                        CLOCK.tick(FPS)

                        for event in pygame.event.get():
                             pos = pygame.mouse.get_pos()
                             if event.type == pygame.MOUSEBUTTONDOWN:
                                 global difficulty
                                 global dificultate
                                 if easybutton.isOver(pos):
                                     difficulty = 'Easy'
                                     dificultate = 1
                                     dif = False
                                 if normalbutton.isOver(pos):
                                     difficulty = 'Normal'
                                     dificultate = 2
                                     dif = False
                                 if hardbutton.isOver(pos):
                                     difficulty = 'Hard'
                                     dificultate = 3
                                     dif = False
                             if event.type == pygame.MOUSEMOTION:
                                 if easybutton.isOver(pos):
                                    easybutton.color = (red)
                                 else:
                                    easybutton.color = (green)
                                 if normalbutton.isOver(pos):
                                    normalbutton.color = (red)
                                 else:
                                    normalbutton.color = (green)
                                 if hardbutton.isOver(pos):
                                    hardbutton.color = (red)
                                 else:
                                    hardbutton.color = (green)
                            #end nivel dificultate
                if quitbutton.isOver(pos):
                   pygame.quit()
                   quit()
            #schimbarea culorii butonului in momentul trecerii mouse ului
            if event.type == pygame.MOUSEMOTION:
                if greenbutton.isOver(pos):
                    greenbutton.color = (red)
                else:
                    greenbutton.color = (green)
                if redbutton.isOver(pos):
                    redbutton.color = (red)
                else:
                    redbutton.color = (green)
                if quitbutton.isOver(pos):
                    quitbutton.color = (red)
                else:
                    quitbutton.color = (green)
   #end_meniu principal
     
def main():
    #initializari
    global lives
    
    run = True
    background_x = 0
    level = 0
    
    
   
    #entitati ++
    enemies=[]
    wave_length = 5
    enemy_vel = 0.6 + 0.1*dificultate
    enemy_laser_vel = 2 + dificultate
    laser_vel = 4 
    is_paused = 0
    player = Player(WIDTH/2-SHIP_SIZE_SQUARE/2, HEIGHT-SHIP_SIZE_SQUARE-10)

    lost = False
    lost_count = 0
    
    
    
    while run:    
        events()
        
       
        screen.fill(black)
        #miscare background
        rel_x = background_x % background.get_rect().height
        screen.blit(background, (0,rel_x - HEIGHT))
        
        if rel_x < 800:
             screen.blit(background, (0, rel_x))
        background_x -= 2
        #end 
        # afisare scor/nivel/dificultate/numar de vieti ramase
        lives_label = main_font.render(f"Lives: {lives}",1, red)
        level_label = main_font.render(f"Level: {level}",1, green)
        mesaj_4 = main_font.render("Score: ", 1, white)
        score_label = small_font.render(f"{score}",1, white )
        screen.blit(lives_label,(WIDTH + 100 - lives_label.get_width()/2,50))
        screen.blit(level_label,(WIDTH + 100 - level_label.get_width()/2,100))
        screen.blit(mesaj_4, (WIDTH + 100 - mesaj_4.get_width()/2,HEIGHT - score_label.get_height()- 10 - mesaj_4.get_height()))
        screen.blit(score_label,(WIDTH + 100 - score_label.get_width()/2,HEIGHT - score_label.get_height()- 10))

        mesaj_3 = main_font.render("Difficulty: ",1, white )
        dif_label = main_font.render(f"{difficulty}",1, white)
        screen.blit(mesaj_3,(WIDTH + 100 - mesaj_3.get_width()/2,HEIGHT/2 - mesaj_3.get_height() - dif_label.get_height()))
        screen.blit(dif_label,(WIDTH + 100 - dif_label.get_width()/2,HEIGHT/2  - dif_label.get_height()))

        mesaj_5 = small2_font.render("Press SPACE to pause: ", 1, white)
        screen.blit(mesaj_5,(WIDTH + 100 - mesaj_5.get_width()/2,HEIGHT  - score_label.get_height() - mesaj_4.get_height() - mesaj_5.get_height() - 100))
        #end

        for enemy in enemies:
                enemy.draw(screen)

        player.draw(screen)

        if lost:
              lost_label = lost_font.render("You Lost!", 1, white)
              screen.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, HEIGHT/2 - lost_label.get_height()/2))
            


        pygame.display.update()
        CLOCK.tick(FPS)

        
        


        if lives <= 0:
                lost = True
                lost_count += 1

        if lost:
                if lost_count > FPS * 3:
                    run = False 
                    lost = False
                    
                else:
                    continue

       


            

        if len(enemies) == 0:
                level += 1
                wave_length += dificultate  #nr inamici adaugati la fiecare incrementare de nivel
                for i in range(wave_length):
                    enemy=Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500*level/5, -100), random.choice(["cat1", "cat2", "cat3", "cat4" ])) #modificare aparitie inamici "/5"
                    enemies.append(enemy)

        mouse_pos = pygame.mouse.get_pos()

        run2 =(mouse_pos[0] - player.x)*0.1    #modific de aici daca nu-mi convine viteza
        rise = (mouse_pos[1] - player.y)*0.1
            
            #border interdiction
        if player.x +run2 > 0 and player.x +run2 < WIDTH - SHIP_SIZE_SQUARE:   #left/righ
                player.x +=run2
        if player.y +rise > 0 and player.y +rise < HEIGHT - SHIP_SIZE_SQUARE:    #up/down
                player.y +=rise
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
              if event.key == pygame.K_SPACE:
                  pause()
       # if keys[pygame.K_SPACE]:
        if 1:
                player.shoot()
                
                
            #inamici
        for enemy in enemies[:]:
                enemy.move(enemy_vel)
                enemy.move_lasers(enemy_laser_vel, player)

                if random.randrange(0, (20 - dificultate)*60) == 1:
                    enemy.shoot()

                if enemy.y + ENEMY_SIZE_SQUARE > HEIGHT:                        
                    enemies.remove(enemy)
                
                if collide(enemy, player):
                    lives -= 1
                    enemies.remove(enemy)


        player.move_lasers(-laser_vel, enemies) 
        
     




#meniu principal
game_intro()
#loop-ul principal

