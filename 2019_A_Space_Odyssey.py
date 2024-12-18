# Developers: Moller Rodrigues

## IMPORTS ##
import simplegui
from user301_hPMHbpw1h9_0 import Vector
import random

## CLASSES ##

# SPRITE CLASS - loads and draws sprite on canvas
class Sprite():
    def __init__(self, sprite_sheet, columns, rows, fIndex):
        # SPRITE ATTRIBUTES
        self.img = sprite_sheet
        self.sprite_columns = columns
        self.sprite_rows = rows
        self.fIndex = fIndex
        self.width = self.img.get_width()
        self.height = self.img.get_height()
        self.frameWidth = self.width/self.sprite_columns
        self.frameHeight = self.height/self.sprite_rows
        self.frameCentreX = self.frameWidth/2
        self.frameCentreY = self.frameHeight/2
        self.frameIndex = (self.fIndex) # fIndex is a tuple (X,Y) where x is the column and Y is the row
        self.x = self.frameWidth*self.frameIndex[0] + self.frameCentreX
        self.y = self.frameHeight*self.frameIndex[1] + self.frameCentreY
        self.center_source = [self.frameWidth*self.frameIndex[0]+self.frameCentreX,self.frameHeight*self.frameIndex[1]+self.frameCentreY]
        self.width_height_dest = [self.frameWidth, self.frameHeight]

    ## METHOD TO DRAW SPRITE ON CANVAS
    def draw(self, canvas, center_dest, width_height_dest):
        try: # DRAW WITH ERROR HANDLING - sometimes the image does not load in time as we are not instantiating aliens at game start but every new game
            canvas.draw_image(
                self.img, # image URL
                (self.center_source[0],self.center_source[1]), # center_source
                (self.width_height_dest[0], self.width_height_dest[1]), # width_height_source
                (center_dest[0], center_dest[1]), # center_dest
                (width_height_dest[0], width_height_dest[1]) # width_height_dest
            )
        except ValueError:
            GAME.current_screen = "error"

# ALIEN CLASS - creates an alien object which is also a child of Sprite
class Alien(Sprite):
    def __init__(self,sprite_sheet, columns, rows, fIndex, pos, vel):
        Sprite.__init__(self,sprite_sheet, columns, rows, fIndex)
        self.pos = pos
        self.vel = vel.copy()           # Change this value to change alien speed


# ALIEN FLEET - handler for all aliens
class AlienFleet():
    def __init__(self, SPRITE_SHEET, current_enemy_settings):
        # FLEET ATTRIBUTES
        self.current_enemy_settings = current_enemy_settings
        self.grid = []
        self.SPRITE_DIMENSIONS = (60,56)
        self.START_X = 50
        self.ALIEN_TYPES = [(0,1), (1,0), (1,1), (0,2)]
        self.NUMBER_OF_ENEMIES = current_enemy_settings[0]
        self.NUMBER_OF_WAVES = current_enemy_settings[1]
        self.ROW_START_POS = [350,250,150,50]
        self.dead = 0
        self.number_of_enemies = None
        self.SPRITE_SHEET = SPRITE_SHEET

    ## METHOD TO SETUP UP GRID OF ALIEN OBJECTS USING 2D ARRAY ##
    def setup_grid(self):
        count = 0
        for row in range(0,self.NUMBER_OF_WAVES):
            self.grid.append([])
            base = 0
            for enemy in range(0,self.NUMBER_OF_ENEMIES):
                base += self.START_X
                x = (50* (enemy+1)) + base
                pos = Vector(x,self.ROW_START_POS[row])
                self.grid[row].append(Alien(self.SPRITE_SHEET, 2, 3, self.ALIEN_TYPES[row], pos, Vector(self.current_enemy_settings[2],0)))
                count +=1
        self.number_of_enemies = count
    ## METHOD TO DRAW GRID ON SCREEN ##
    def draw_grid(self, canvas):
        for row in range(0,self.NUMBER_OF_WAVES):
            for enemy in range(0,self.NUMBER_OF_ENEMIES):
                alien = self.grid[row][enemy]
                if alien == None:
                    continue
                else:
                    pos = alien.pos.getP()
                    alien.draw(canvas,pos,self.SPRITE_DIMENSIONS)
    ## METHOD TO UPDATE ENEMY POSITION ##
    def update(self):
        for row in range(0,self.NUMBER_OF_WAVES):
            for enemy in range(0,self.NUMBER_OF_ENEMIES):
                alien = self.grid[row][enemy]
                if alien == None:
                    continue
                else:
                    if alien.pos.x >= 1450:
                        alien_direction = Vector(0,50)
                        alien.pos.add(alien_direction)
                        alien_vel = alien.vel.multiply(-1)
                        alien.pos.add(alien_vel)
                    if alien.pos.x <= 50:
                        alien_direction = Vector(0,50)
                        alien.pos.add(alien_direction)
                        alien_vel = alien.vel.multiply(-1)
                        alien.pos.add(alien_vel)
                    if alien.pos.y >= 750:
                        GAME.game_stats.lives -= 1
                        if GAME.game_stats.lives < 0:
                            GAME.current_screen = "game_over"
                        else:
                            self.reset()
                            return
                    alien.pos.add(alien.vel)
    ## METHOD TO CHECK IF ALIEN HAS BEEN HIT ##
    def check_collisions(self, canvas, projectiles):
        for row in range(0,self.NUMBER_OF_WAVES):
            for enemy in range(0,self.NUMBER_OF_ENEMIES):
                alien = self.grid[row][enemy]
                if alien == None:
                    continue
                else:
                    for projectile in projectiles:
                        if projectile.pos.copy().y <= alien.pos.copy().y + 27 and projectile.pos.copy().x >= alien.pos.copy().x-35 and projectile.pos.copy().x <= alien.pos.copy().x+35:
                            GAME.projectiles.remove_proj(projectile)
                            GAME.exp_sound.play()
                            if alien.fIndex == (0,1):
                                GAME.game_stats.add_to_score(5)
                            elif alien.fIndex == (1,0):
                                GAME.game_stats.add_to_score(10)
                            elif alien.fIndex == (1,1):
                                GAME.game_stats.add_to_score(15)
                            elif alien.fIndex == (0,2):
                                GAME.game_stats.add_to_score(20)
                            GAME.exp_timer.start()
                            GAME.exp_count = 0
                            if GAME.exp_count >= 5:
                                pass
                            else:
                                GAME.explosion_set[GAME.exp_count].draw(canvas, alien.pos.getP(), (60,56))
                            self.grid[row][enemy] = None
                            self.dead += 1
    ## METHOD TO RESET ALIENs TO START POS ##
    def reset(self):
        for row in range(0,self.NUMBER_OF_WAVES):
            base = 0
            for enemy in range(0,self.NUMBER_OF_ENEMIES):
                alien = self.grid[row][enemy]
                if alien == None:
                    continue
                else:
                    base += self.START_X
                    x = (50* (enemy+1)) + base
                    alien.pos = Vector(x,self.ROW_START_POS[row])
                    if alien.vel.x <0:
                        alien.vel = alien.vel.multiply(-1)
    ## METHOD TO REVIVE ALL ENEMIES AND SEND THEM BACK TO START ##
    def restart(self):
        self.dead = 0
        self.grid = []
        for row in range(0,self.NUMBER_OF_WAVES):
            self.grid.append([])
            base = 0
            for enemy in range(0,self.NUMBER_OF_ENEMIES):
                base += self.START_X
                x = (50* (enemy+1)) + base
                pos = Vector(x,self.ROW_START_POS[row])
                self.grid[row].append(Alien(self.SPRITE_SHEET, 2, 3, self.ALIEN_TYPES[row], pos, Vector(self.current_enemy_settings[2],0)))
    ## METHOD WHICH RETURNS THE FRONTLINE OF ENEMIES (negating dead enemies from front row and including alive enemies from other rows) ##
    def front_row(self):
        front = []
        for row in range(0,self.NUMBER_OF_WAVES):
            for enemy in range(0,self.NUMBER_OF_ENEMIES):
                alien = self.grid[row][enemy]
                if row == 0 and alien != None:
                    front.append(alien)
                    continue
                elif self.grid[row-1][enemy] == None and alien != None:
                    front.append(alien)
        return front


# BOSS CLASS - final enemy boss object
class Boss:
    def __init__(self, image):
         ## BOSS ATTRIBUTES ##
        self.pos = Vector(750,120)
        self.start_pos = Vector(750,120)
        self.vel = Vector(2,0)
        self.img = image
        self.boss_center_source = (97, 51.5)
        self.boss_width_height_dest = (194,103)
        self.neutral_vel = Vector()
        self.x_right_limit = 1403
        self.x_left_limit = 97
        self.hp = 150
    ## METHOD TO DRAW BOSS AND BOSS HP ON CANVAS ##
    def draw(self, canvas):
        GAME.image_drawer(canvas, self.img ,self.boss_center_source, self.pos.getP(), self.boss_width_height_dest)
        canvas.draw_text("BOSS HP", [40,40], 18, "Yellow")
        canvas.draw_polygon([(5,45), (5,55), (self.hp,55), (self.hp,45)], 2, "Navy", "Blue")
    ## METHOD TO EXECUTE ATTACK SEQUENCE 1 ##
    def attack_seq_1(self):
        base_y = -0.9
        for i in range(0,10):
            GAME.projectiles.enemy_projectiles.append(Projectile("enemy", self.pos.copy() , Vector(base_y, 0.8)))
            base_y += 0.2
    ## METHOD TO EXECUTE ATTACK SEQUENCE 2 ##
    def attack_seq_2(self):
        base_y = -0.7
        for i in range(0,9):
            GAME.projectiles.enemy_projectiles.append(Projectile("enemy", self.pos.copy() , Vector(base_y, 0.8)))
            base_y += 0.2
    ## METHOD TO UPDATE BOSS POSITION ##
    def update(self):
        if self.boundary_reached() == "right":
            self.vel = self.vel.copy().multiply(-1)
        elif self.boundary_reached() == "left":
            self.vel = self.vel.copy().multiply(-1)

        self.pos.add(self.vel)
    ## METHOD TO CHECK IF BOSS HAS REACHED A BOUNDARY##
    def boundary_reached(self):
        x = self.pos.getP()[0]
        limit = None
        if x >= self.x_right_limit:
            limit = "right"
        elif x <= self.x_left_limit:
            limit = "left"
        return limit

    def reset(self):
        self.pos = self.start_pos

    def check_collisions(self, canvas, projectiles):
        for projectile in projectiles:
            if projectile.pos.copy().y <= self.pos.copy().y + 51.5 and projectile.pos.copy().x >=  self.pos.copy().x-90 and projectile.pos.copy().x <=  self.pos.copy().x+90:
                            GAME.projectiles.remove_proj(projectile)
                            GAME.exp_sound.play()
                            GAME.game_stats.add_to_score(20)
                            GAME.exp_timer.start()
                            GAME.exp_count = 0
                            if GAME.exp_count >= 5:
                                pass
                            else:
                                GAME.explosion_set[GAME.exp_count].draw(canvas, self.pos.getP(), (60,56))
                            self.hp -= 5


# PLAYER CLASS - player object
class Player:
    def __init__(self,pos, current_player_settings):
        ## PLAYER CONFIG ##
        self.pos = pos
        self.vel = Vector()
        self.right_limit_vec = Vector(1460, 750)
        self.left_limit_vec = Vector(40, 750)
        self.neutral_vel = Vector()
        self.x_right_limit = 1472
        self.x_left_limit = 28
        self.player_vel = Vector(current_player_settings[0],0)
        self.player_vel_neg = Vector(current_player_settings[0]*-1,0)
        self.player_center_source = (30,28)
        self.player_width_height_dest = (60,56)
    ## METHOD TO DRAW PLAYER ##
    def draw_player(self, canvas):
        GAME.image_drawer(canvas, GAME.player_img, self.player_center_source, self.pos.getP(), self.player_width_height_dest)
    ## METHOD TO UPDATE PLAYER POSITION ##
    def update(self):
        if self.boundaryReached() == "right":
            self.pos = self.right_limit_vec
            self.vel = self.neutral_vel
        elif self.boundaryReached() == "left":
            self.pos = self.left_limit_vec
            self.vel = self.neutral_vel
        else:
            self.pos.add(self.vel)
    ## METHOD TO CHECK IF PLAYER HAS REACHED A BOUNDARY ##
    def boundaryReached(self):
        x = self.pos.getP()[0]
        limit = None
        if x >= self.x_right_limit:
            limit = "right"
        elif x <= self.x_left_limit:
            limit = "left"
        return limit
    ## METHOD TO RESET PLAYER TO START POS ##
    def reset_player(self):
        self.pos = Vector(750,750)
    ## METHOD TO CHECK IF PLAYER HAS BEEN HIT ##
    def check_collisions(self, canvas, projectiles):
        for projectile in projectiles:
            if ((projectile.pos.copy().y + projectile.radius) >= self.pos.copy().y) and (projectile.pos.copy().x >= self.pos.copy().x - 30) and (projectile.pos.copy().x <= self.pos.copy().x +30):
                GAME.projectiles.remove_proj(projectile)
                GAME.exp_sound.play()
                GAME.game_stats.add_to_score(-50)
                GAME.exp_timer.start()
                GAME.exp_count = 0
                if GAME.exp_count >= 5:
                    pass
                else:
                    GAME.explosion_set[GAME.exp_count].draw(canvas, self.pos.getP(), (60,56))
                GAME.game_stats.minus_life()
                if GAME.game_stats.lives < 0:
                    GAME.current_screen = "game_over"


# GAME STATS CLASS - in game stats (lives, score, level)
class GameStats:
    def __init__(self):
        self.score = 0
        # score frame position
        self.score_pos = (32,20)
        self.level = 0
        # level frame position
        self.level_pos = (700,20)
        self.lives = 3
        # font settings
        self.font_colour = "Red"
        self.font_size = 25
    # LEVEL METHODS
    def change_level(self, level):
        self.level = level
    def reset_level(self):
        self.level = 1
    def draw_level(self, canvas):
        levelboard = "Level "+str(self.level)
        canvas.draw_text(levelboard, [self.level_pos[0],self.level_pos[1]], self.font_size, self.font_colour)
    # SCORE METHODS
    def add_to_score(self, points):
        self.score += points
    def reset_score(self):
        self.score = 0
    def draw_score(self, canvas):
        scoreboard = "Score: "+str(self.score)
        canvas.draw_text(scoreboard, [self.score_pos[0],self.score_pos[1] ], self.font_size, self.font_colour)
    # LIVES METHODS
    def minus_life(self):
        self.lives -= 1
    def out_of_lives(self):
        if self.lives < 0:
            return True
        else:
            return False
    def reset_lives(self):
        self.lives = 3
    def draw_lives(self, canvas):
        base = -40
        for i in range(0,self.lives):
            GAME.image_drawer(canvas, GAME.heart_img, (16,16), (1484+base, 16), (32,32))
            base -= 40


# INPUT HANDLER CLASS - handles all user inputs
class InputHandler:
    def __init__(self):
        pass
    # KEY DOWN HANDLER
    def keydown(self, key):
        # LEVEL 1
        if GAME.current_screen == "in_game":
            if key == simplegui.KEY_MAP['right'] or key == simplegui.KEY_MAP['left']: # Avoid player getting stuck in boundaries
                if GAME.player.pos.getP()[0] > 1400:
                        GAME.player.pos.add(Vector(-50,0))
                if GAME.player.pos.getP()[0] < 60:
                    GAME.player.pos.add(Vector(50,0))
            # move player right
            if key == simplegui.KEY_MAP['right']:
                        GAME.player.vel = GAME.player.player_vel
            # move player lefft
            if key == simplegui.KEY_MAP['left']:
                GAME.player.vel = GAME.player.player_vel_neg
            # Player shoot (only allow x bullets on screen)
            if key == simplegui.KEY_MAP['space']:
                if len(GAME.projectiles.player_projectiles) == GAME.current_player_settings[1]:
                    pass
                else:
                    GAME.shoot_sound.play()
                    pos = GAME.player.pos.copy().add(Vector(0,-28))
                    GAME.projectiles.add_proj(Projectile("player", pos, Vector(0,-4)))
        # LEVEL 2 HANDLER
        if GAME.current_screen == "level_2":
            if key == simplegui.KEY_MAP['right'] or key == simplegui.KEY_MAP['left']:
                if GAME.player.pos.getP()[0] > 1400:
                        GAME.player.pos.add(Vector(-50,0))
                if GAME.player.pos.getP()[0] < 60:
                    GAME.player.pos.add(Vector(50,0))
            # move player right
            if key == simplegui.KEY_MAP['right']:
                        GAME.player.vel = GAME.player.player_vel
            # move player lefft
            if key == simplegui.KEY_MAP['left']:
                GAME.player.vel = GAME.player.player_vel_neg
            # Player shoot (only allow 4 bullets on screen)
            if key == simplegui.KEY_MAP['space']:
                if len(GAME.projectiles.player_projectiles) == 4:
                    pass
                else:
                    GAME.shoot_sound.play()
                    pos = GAME.player.pos.copy().add(Vector(0,-28))
                    GAME.projectiles.add_proj(Projectile("player", pos, Vector(0,-4)))
        ## PAUSE HANDLER ##
        if GAME.game_running:
            if key == simplegui.KEY_MAP['p']:
                GAME.paused_screen = GAME.current_screen
                GAME.current_screen = "pause"
        if not GAME.game_running and GAME.current_screen != "game_over":
            if key == simplegui.KEY_MAP['p']:
                GAME.current_screen = GAME.paused_screen
        if GAME.current_screen == "pause":
            if key == simplegui.KEY_MAP['r']:
                GAME.new_game()
                GAME.current_screen = "in_game"
            if key == simplegui.KEY_MAP['q']:
                GAME.new_game()
                GAME.current_screen = "menu"
        # Game over key handler
        if GAME.current_screen == "game_over":
            if key == simplegui.KEY_MAP['r']:
                GAME.new_game()
                GAME.current_screen = "in_game"
            if key == simplegui.KEY_MAP['q']:
                GAME.new_game()
                GAME.current_screen = "menu"
        # VICTORY SCREEN HANDLER
        if GAME.current_screen == "victory":
            if key == simplegui.KEY_MAP['r']:
                GAME.new_game()
                GAME.current_screen = "in_game"

            if key == simplegui.KEY_MAP['q']:
                GAME.new_game()
                GAME.current_screen = "menu"
    ## KEY UP HANDLER ##
    def keyup(self, key):
        # Stop playing from moving when key release
        if key == simplegui.KEY_MAP['right'] and key != simplegui.KEY_MAP['left'] :
                     GAME.player.vel = Vector()
        elif key == simplegui.KEY_MAP['left'] and key != simplegui.KEY_MAP['right']:
            GAME.player.vel = Vector()
    ## MOUSE HANDLER ##
    def mouse_handler(self, position):
        ## MENU SCREEN MOUSE HANDLER ##
        if GAME.current_screen == "menu":
            # Switch to start screen
            if position[0] >= 665 and position[0] <= 825 and position[1] >= 350 and position[1] <= 395:
                GAME.start_game()
                GAME.new_game()
                GAME.current_screen = "in_game"
            # Switch to Instructions screen
            if position[0] >= 575 and position[0] <= 920 and position[1] >= 430 and position[1] <= 470:
                GAME.current_screen = "instructions"
            # Switch to settings screen
            if position[0] >= 630 and position[0] <= 865 and position[1] >= 510 and position[1] <= 555:
                GAME.settings.launch()
                GAME.current_screen = "settings"
            # exit
            if position[0] >= 680 and position[0] <= 815 and position[1] >= 590 and position[1] <= 632:
                GAME.current_screen = "quit"
        ## INSTRUCTIONS SCREEN MOUSE HANDLER ##
        if GAME.current_screen == "instructions":
            # Switch to start screen
            if position[0] >= 25 and position[0] <= 117 and position[1] >= 39 and position[1] <= 109:
                GAME.current_screen = "menu"
            # Switch to game screen
            if position[0] >= 1370 and position[0] <= 1470 and position[1] >= 41 and position[1] <= 113:
                GAME.start_game()
                GAME.new_game()
                GAME.current_screen = "in_game"

# PROJECTILE CLASS - creates projectile objects
class Projectile():
    def __init__(self, type_of_proj , position, trajectory):
        # projectile attributes
        self.type_of_proj = type_of_proj
        self.pos = position
        self.trajectory = trajectory
        self.radius = 5
        if self.type_of_proj == "enemy":
            self.colour = "blue"
        elif self.type_of_proj == "player":
            self.colour = "red"
    ## METHOD TO DRAW PROJECTILE ##
    def draw(self, canvas):
        canvas.draw_circle(self.pos.getP(),self.radius,1,'black',self.colour)
        self.update()
    ## METHOD TO UPDATE PROJECTILE POSITION ##
    def update(self):
        self.pos.add(self.trajectory)


# PROJECTILES CLASS - handler for all projectiles
class Projectiles():
    def __init__(self):
        # LISTS TO HOLD PLAYER AND ENEMY PROJECTILES
        self.player_projectiles = []
        self.enemy_projectiles = []
    ## METHOD TO ADD PROJECTILES TO THEIR RESPECTIVE LISTS ##
    def add_proj(self, projectile):
        if projectile.type_of_proj == "enemy":
            self.enemy_projectiles.append(projectile)
        elif projectile.type_of_proj == "player":
            self.player_projectiles.append(projectile)
    ## METHOD TO REMOVE PROJECTILE FROM THEIR RESPECTIVE LIST ##
    def remove_proj(self, projectile):
        if projectile.type_of_proj == "enemy":
            if (projectile in self.enemy_projectiles):
                self.enemy_projectiles.remove(projectile)
        elif projectile.type_of_proj == "player":
            if (projectile in self.player_projectiles):
                self.player_projectiles.remove(projectile)
    ## METHOD TO ANIMATE ALL PROJECTILES IN THEIR RESPECTIVES LISTS ON CANVAS ##
    def animate(self, canvas):
        for projectile in self.player_projectiles:
            if projectile.pos.y >= 800 or projectile.pos.y <= 0:
                self.remove_proj(projectile)
            else:
                projectile.draw(canvas)
        for projectile in self.enemy_projectiles:
            if projectile.pos.y >= 800 or projectile.pos.y <= 0:
                self.remove_proj(projectile)
            else:
                projectile.draw(canvas)
     ## METHOD TO DELETE PROJECTILE IF THEY CROSS THE CANVAS BOUNDARY ##
    def boundary_check(self):
        for proj in self.enemy_projectiles:
            if proj.pos.copy().y >= 800:
                self.enemy_projectiles.remove(proj)
        for proj in self.player_projectiles:
            if proj.pos.copy().y >= 800:
                self.player_projectiles.remove(proj)


# LEVELS CLASS - draws and executes each level
class Levels:
    def __init__(self):
        pass
    
        # LEVELS
    def level_1(self, canvas):
        GAME.image_drawer(canvas, GAME.bg_img,GAME.screen_center_dest, GAME.screen_center_dest, GAME.screen_width_height_dest)
        GAME.game_stats.draw_lives(canvas)
        GAME.game_stats.draw_score(canvas)
        GAME.game_stats.draw_level(canvas)
        GAME.player.draw_player(canvas)
        GAME.player.update()
        GAME.fleet.draw_grid(canvas)
        GAME.fleet.update()
        GAME.projectiles.animate(canvas)
        GAME.enemy_shoot_timer.start()
        GAME.fleet.check_collisions(canvas, GAME.projectiles.player_projectiles)
        GAME.player.check_collisions(canvas, GAME.projectiles.enemy_projectiles)

        if GAME.fleet.dead == GAME.fleet.number_of_enemies:
            self.reset_level_1()
            GAME.current_screen = "level_2_cut"

    # LEVEL 2 SCREEN
    def level_2(self, canvas):
        GAME.image_drawer(canvas, GAME.level_2_img,GAME.screen_center_dest, GAME.screen_center_dest, GAME.screen_width_height_dest)
        GAME.game_stats.draw_lives(canvas)
        GAME.game_stats.draw_score(canvas)
        GAME.game_stats.draw_level(canvas)
        GAME.boss.draw(canvas)
        GAME.boss.update()
        GAME.projectiles.animate(canvas)
        GAME.boss_attack_timer.start()
        GAME.projectiles.boundary_check()
        GAME.player.draw_player(canvas)
        GAME.player.update()
        GAME.player.check_collisions(canvas, GAME.projectiles.enemy_projectiles)
        GAME.boss.check_collisions(canvas, GAME.projectiles.player_projectiles)
        if GAME.boss.hp == 0:
            GAME.current_screen = "victory"
            self.reset_level_2

    # LEVEL 2 CUTSCENE SCREEN
    def level_2_cutscene(self, canvas):
        global count
        GAME.image_drawer(canvas, GAME.level_2_cut_img,GAME.screen_center_dest, (750,400), GAME.screen_width_height_dest)
        GAME.game_stats.draw_lives(canvas)
        GAME.game_stats.draw_score(canvas)
        GAME.player.draw_player(canvas)
        forward = Vector(0,-1.5)
        GAME.player.pos.add(forward)
        GAME.player.update()
        GAME.exp_timer.start()
        if GAME.exp_count >= 5:
            pass
        else:
            c = 0
            for i in range(0, 15):
                GAME.exp_sound.play()
                GAME.explosion_set[GAME.exp_count].draw(canvas, (60+c,500), (60,56))
                c += 100
        if GAME.player.pos.y <= -28:
            GAME.game_stats.level = 2
            GAME.current_screen = "level_2"
            GAME.player.reset_player()

    # RESET LEVEL 1
    def reset_level_1(self):
        GAME.player.reset_player()
        GAME.enemy_shoot_timer.stop()

    # RESET LEVEL 2
    def reset_level_2(self):
        GAME.boss_attack_timer.stop()
        GAME.player.reset_player()
        for proj in GAME.projectiles.enemy_projectiles:
            GAME.projectiles.remove_proj(proj)
        for proj in GAME.projectiles.player_projectiles:
            GAME.projectiles.remove_proj(proj)


# SCREENS CLASS - draws and executes required screen
class Screens:
    def __init__(self):
        pass
    ## SCREENS ##

    def settings_screen(self, canvas):
        GAME.image_drawer(canvas, GAME.settings_img, GAME.screen_center_dest, GAME.screen_center_dest, GAME.screen_width_height_dest)
    # ERROR SCREEN
    def error(self, canvas):
        GAME.image_drawer(canvas, GAME.error_img, GAME.screen_center_dest, GAME.screen_center_dest, GAME.screen_width_height_dest)
    # MENU SCREEN
    def menu(self, canvas):
        GAME.image_drawer(canvas, GAME.menu_img, GAME.screen_center_dest, GAME.screen_center_dest, GAME.screen_width_height_dest)
    # PAUSE SCREEN
    def pause(self, canvas):
        GAME.image_drawer(canvas, GAME.pause_img, GAME.screen_center_dest, GAME.screen_center_dest, GAME.screen_width_height_dest)
    # INSTRUCTIONS SCREEN
    def insts(self, canvas):
        GAME.image_drawer(canvas, GAME.insts_img, GAME.screen_center_dest, GAME.screen_center_dest, GAME.screen_width_height_dest)
    # GAME OVER SCREEN
    def game_over(self, canvas):
        GAME.image_drawer(canvas, GAME.game_over_img, GAME.screen_center_dest, GAME.screen_center_dest, GAME.screen_width_height_dest)
    # VICTORY SCREEN
    def victory(self, canvas):
        GAME.image_drawer(canvas, GAME.victory_img, GAME.screen_center_dest, GAME.screen_center_dest, GAME.screen_width_height_dest)
    # IN GAME SCREEN
    def in_game(self, canvas):
        GAME.levels.level_1(canvas)

    
# SETTINGS CLASS - allows user to change game settings
class Settings:
    def __init__(self):
        self.enemy_config_names = []
        self.player_config_names = []
        self.apply = None
        self.default = None

    def launch(self):
        self.settings_frame = simplegui.create_frame("Settings", 0, 500)
        enemy_config = self.settings_frame.add_label('ENEMY CONFIG')
        self.enemy_config_names.append(self.settings_frame.add_input('Number of enemies:',lambda args:self.enemy_config_handler(0), 50))
        self.enemy_config_names.append(self.settings_frame.add_input('Number of rows:', lambda args:self.enemy_config_handler(1), 50))
        self.enemy_config_names.append(self.settings_frame.add_input('Enemy speed:', lambda args:self.enemy_config_handler(2), 50))

        player_config = self.settings_frame.add_label('PLAYER CONFIG')
        self.player_config_names.append(self.settings_frame.add_input('Player speed:', lambda args:self.player_config_handler(0), 50))
        self.player_config_names.append(self.settings_frame.add_input('Player shoot frequency:', lambda args:self.player_config_handler(1), 50))

        self.apply = self.settings_frame.add_button('APPLY', self.apply_settings)
        self.default = self.settings_frame.add_button('RESET TO DEFAULT', self.default_settings)
        self.menu_but = self.settings_frame.add_button('MENU', self.change_to_menu)
        self.current_settings()
        self.settings_frame.start()

    def change_to_menu(self):
        GAME.current_screen = "menu"
        self.settings_frame.stop()
        self.enemy_config_names = []
        self.player_config_names = []
    
    def current_settings(self):
        for i in range(0,3):
            self.enemy_config_names[i].set_text(GAME.current_enemy_settings[i])
        for i in range(0,2):
            self.player_config_names[i].set_text(GAME.current_player_settings[i])


    def enemy_config_handler(self, index):
        user_input = int(self.enemy_config_names[index].get_text())
        if self.validate_enemy(index, user_input):
            GAME.current_enemy_settings[index] = user_input
        else:
            return

    def player_config_handler(self, index):
        user_input = int(self.player_config_names[index].get_text())
        if self.validate_player(index, user_input):
            GAME.current_player_settings[index] = user_input
        else:
            return

    def validate_enemy(self, index, user_input):
        if index == 0:
            if user_input >= 1 and user_input <= 12:
                return True
            else:
                return False

        if index == 1:
            if user_input >= 1 and user_input <= 4:
                return True
            else:
                return False

        if index == 2:
            if user_input >= 0.5 and user_input <= 10:
                return True
            else:
                return False

    def validate_player(self, index, user_input):
        if index == 0:
            if user_input >= 0.5 and user_input <= 10:
                return True
            else:
                return False

        if index == 1:
            if user_input >= 1 and user_input <= 3:
                return True
            else:
                return False

    def apply_settings(self):
        for i in range(0,3):
            user_input = int(self.enemy_config_names[i].get_text())
            if self.validate_enemy(i, user_input):
                GAME.current_enemy_settings[i] = user_input
            else:
                continue
        return

        for i in range(0,2):
            user_input = int(self.player_config_names[i].get_text())
            if self.validate_player(i, user_input):
                GAME.current_player_settings[i] = user_input
            else:
                continue
        return

    def default_settings(self):
        for i in range(0,3):
            GAME.current_enemy_settings[i] = GAME.default_enemy_settings[i]
        for i in range(0,2):
            GAME.current_player_settings[i] = GAME.default_player_settings[i]
        self.current_settings()


# GAME CLASS - contoller for enitre game
class Game:
    def __init__(self):
        # LOAD RESOURCES
        self.load_resources()
        # SET DEAFULT SETTINGS
        self.set_default_settings()
        # LOAD EXPLOSION ANIMATION
        self.load_explosion()
        # CONFIGURE SCREEN SETTINGS
        self.config_screen()
        # CONFIGURE FRAME SETTINGS
        self.config_frame()
        # SET GAME CONSTANTS
        self.set_constants()
        # INSTANSTIATE GAME OBJECTS
        self.create_objects()
        # LAUNCH GAME
        self.launch_game()


    def load_resources(self):
        # IMAGES
        self.menu_img = simplegui.load_image("https://i.ibb.co/7JYmxhg/menu.png")
        self.bg_img = simplegui.load_image("https://i.ibb.co/6D832Z5/space.png")
        self.game_over_img = simplegui.load_image("https://i.ibb.co/7zmyC4T/game-over.png")
        self.pause_img = simplegui.load_image("https://i.ibb.co/YdDLGKb/puase-screen.png")
        self.insts_img = simplegui.load_image("https://i.ibb.co/fCjNJXC/instructions.png")
        self.heart_img = simplegui.load_image("https://i.ibb.co/WgjP1Pv/heart.png")
        self.player_img =simplegui.load_image("https://i.ibb.co/JB00V5Z/player.png")
        self.level_2_cut_img = simplegui.load_image("https://i.ibb.co/N93z6jb/level-2-cutscene.png")
        self.error_img = simplegui.load_image("https://i.ibb.co/zSZdCn9/error.png")
        self.level_2_img = self.bg_img
        self.boss_img = simplegui.load_image("https://i.ibb.co/ZJ5Qy0v/boss.png")
        self.victory_img = simplegui.load_image("https://i.ibb.co/0K9wdCh/victory.png")
        self.settings_img = simplegui.load_image("https://i.ibb.co/RSs4dYp/settings.png")
        self.sprite_sheet = simplegui.load_image("https://i.ibb.co/dpbqJnw/New-Piskel-clone-3.png")
        self.exp_img = simplegui.load_image("https://i.ibb.co/bNx7ZGr/regular-Explosion01.png")
        # SOUNDS
        self.theme = simplegui.load_sound("https://jukehost.co.uk/api/audio/11200f2749f2e1b802acbc92d695a276811c7beb/2f2a0e8359b")
        self.shoot_sound = simplegui.load_sound("https://jukehost.co.uk/api/audio/11200f2749f2e1b802acbc92d695a276811c7beb/4eb68341d34")
        self.exp_sound = simplegui.load_sound("https://jukehost.co.uk/api/audio/11200f2749f2e1b802acbc92d695a276811c7beb/74588971107")
        
    def set_default_settings(self):
        self.default_enemy_settings = [9,4,2] # order [No_of_enemies, no_of_rows, enmey_speed, enemy_shoot_freq] *Could use Dict
        self.default_player_settings = [4, 1] # order [player_speed, player_shoot_freq]
        self.current_enemy_settings = [self.default_enemy_settings[0],self.default_enemy_settings[1],self.default_enemy_settings[2]]
        self.current_player_settings = [self.default_player_settings[0], self.default_player_settings[1]]
        # set volume
        self.theme.set_volume(0.05)
        self.shoot_sound.set_volume(0.5)
        self.exp_sound.set_volume(0.1)

    def load_explosion(self):
        self.explosion_fIndex = [(0,0), (1,0), (2,0), (0,1), (1,1), (2,1)]
        self.explosion_set = []
        for i in range(0,6):
            self.explosion_set.append(Sprite(self.exp_img, 3,2,self.explosion_fIndex[i]))


    def start_game(self):
        self.game_stats = GameStats()
        self.fleet = AlienFleet(self.sprite_sheet, self.current_enemy_settings)
        self.fleet.setup_grid()
        self.boss = Boss(self.boss_img)
        self.projectiles = Projectiles()
        self.player = Player(self.player_start_pos, self.current_player_settings)

    def config_screen(self):
        self.screen_center_dest = (750,400)
        self.screen_width_height_dest = (1500,800)
        self.game_running = False
        self.paused_screen = None
        self.current_screen = "menu"

    def config_frame(self):
        self.frame_width = 1500
        self.frame_height = 800
        self.centre_of_frame = Vector(self.frame_width/2,self.frame_width/2)
        self.frame = simplegui.create_frame("Home", self.frame_width , self.frame_height)
        # SET FRAME HANDLERS
        self.frame.set_draw_handler(self.draw_handler)
        self.input = InputHandler()
        self.frame.set_keydown_handler(self.input.keydown)
        self.frame.set_keyup_handler(self.input.keyup)
        self.frame.set_mouseclick_handler(self.input.mouse_handler)
        # SET TIME HANDLERS
        self.exp_timer = simplegui.create_timer(200, self.exp_timer_handler)
        self.enemy_shoot_timer = simplegui.create_timer(1000, self.enemy_shoot)
        self.boss_attack_timer = simplegui.create_timer(2500, self.boss_shoot)
    
    def set_constants(self):
        self.player_start_pos = self.centre_of_frame
        self.exp_count = 0
        self.boss_timer_call = 3000
        self.boss_count = 0

    def create_objects(self):
        self.screens = Screens()
        self.levels = Levels()
        self.settings = Settings()

    ## METHOD TO START NEW GAME ##
    def new_game(self):
        self.enemy_shoot_timer.stop()
        self.game_stats.reset_level()
        self.game_stats.reset_score()
        self.game_stats.reset_lives()
        self.fleet.restart()
        self.player.reset_player()
        self.levels.reset_level_2()
        for proj in self.projectiles.enemy_projectiles:
            self.projectiles.remove_proj(proj)
        for proj in self.projectiles.player_projectiles:
            self.projectiles.remove_proj(proj)

    # TIME HANDLER FOR EXPLOSIONS
    def exp_timer_handler(self):
        if self.exp_count > 5:
            self.exp_timer.stop()
        else:
            self.exp_count += 1
    
    # TIME HANDLER FOR ENEMY SHOOTING
    def enemy_shoot(self):
        front = self.fleet.front_row()
        alien = random.choice(front)
        index = (random.randint(0,3), random.randint(0,8))
        pos = alien.pos.copy().add(Vector(0,29))
        self.projectiles.add_proj(Projectile("enemy",pos, Vector(0,4)))
    
    # TIME HANDLER FOR BOSS LEVEL SHOOTING
    def boss_shoot(self):
        if self.boss_count % 2 == 0:
            self.boss.attack_seq_1()
        else:
            self.boss.attack_seq_2()
        self.boss_count += 1

    # GAME TOOLS

    ## METHOD TO DRAW IMAGE ON CANVAS ##
    def image_drawer(self, canvas, image, center_source, center_dest, width_height_dest):
        canvas.draw_image(
                image, # image URL
                (center_source[0],center_source[1]), # center_source
                (width_height_dest[0],width_height_dest[1]), # width_height_source
                (center_dest[0], center_dest[1]), # center_dest
                (width_height_dest[0], width_height_dest[1]) # width_height_dest
            )

    ## DRAW HANDLER FOR CANVAS ## - SWITCHES BETWEEN SCREENS
    def draw_handler(self, canvas):
        if self.current_screen == "menu":
            self.game_running = False
            self.screens.menu(canvas)
        if self.current_screen == "in_game":
            self.game_running = True
            self.screens.in_game(canvas)
        if self.current_screen == "level_2_cut":
            self.game_running = True
            self.levels.level_2_cutscene(canvas)
        if self.current_screen == "level_2":
            self.game_running = True
            self.levels.level_2(canvas)
        if self.current_screen == "pause":
            self.game_running = False
            self.screens.pause(canvas)
        if self.current_screen == "instructions":
            self.game_running = False
            self.screens.insts(canvas)
        if self.current_screen == "settings":
            self.game_running = False
            self.screens.settings_screen(canvas)
        if self.current_screen == "game_over":
            self.game_running = False
            self.screens.game_over(canvas)
        if self.current_screen == "error":
            self.game_running = False
            self.screens.error(canvas)
        if self.current_screen == "victory":
            self.game_running = False
            self.screens.victory(canvas)
        if self.current_screen == "quit":
            self.game_running = False
            quit()

    def launch_game(self):
        self.frame.start()
        self.theme.play()


# LAUNCH GAME        
if __name__ == "__main__":
    GAME = Game()
