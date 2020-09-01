import pygame, os, time, random

#==>init pygame:
pygame.font.init()
pygame.init()

#====================================Window Settings===============================================#
WIDTH, HEIGHT = 800, 800
WIN = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Space Invaders")
#==================================================================================================#

#=====================================Load assets==================================================#
#Loading ships
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets","pixel_ship_red_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets","pixel_ship_blue_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets","pixel_ship_green_small.png"))
#Loading Hero Ship
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets","pixel_ship_yellow.png"))

#Loading Lasers
RED_LASER = pygame.image.load(os.path.join("assets","pixel_laser_red.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets","pixel_laser_blue.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets","pixel_laser_green.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets","pixel_laser_yellow.png"))

#Loadign Back-ground image
BG = pygame.image.load(os.path.join("assets","background-black.png"))
BG_IMAGE = pygame.transform.scale(BG,(WIDTH,HEIGHT))
#==================================================================================================#

#===================================Game Classes===================================================#

#Laser class
class Laser:
	def __init__(self, x_pos, y_pos, img):
		self.x_pos = x_pos
		self.y_pos = y_pos
		self.img = img
		self.mask = pygame.mask.from_surface(self.img)

	def draw(self, window):
		window.blit(self.img, (self.x_pos, self.y_pos))

	#moving the laser across the map
	def move(self, vel):
		self.y_pos += vel

	#checking if the laser got off the map
	def off_screen(self, height):
		return not(self.y_pos <= height and self.y_pos >= 0)
		
	#Check if the leaser collides with an object
	def collision(self, obj):
		return collide(obj, self)

#Ship Class
class Ship:

	COOLDOWN = 30 # half a second 
	def __init__(self, x_pos, y_pos, health = 100):
		self.x_pos = x_pos
		self.y_pos = y_pos
		self.health = health
		self.ship_img = None
		self.laser_img = None
		self.lasers = []
		self.cool_down_counter = 0

	def draw(self, window):
		window.blit(self.ship_img, (self.x_pos,self.y_pos))
		for laser in self.lasers:
			laser.draw(window)

	def get_width(self):
		return self.ship_img.get_width()

	def get_height(self):
		return self.ship_img.get_height()

	def cooldown(self):
		if self.cool_down_counter >= self.COOLDOWN:
			self.cool_down_counter = 0
		elif self.cool_down_counter > 0:
			self.cool_down_counter += 1

	def shoot(self):
		if self.cool_down_counter == 0:
			laser = Laser(self.x_pos, self.y_pos, self.laser_img)
			self.lasers.append(laser)
			self.cool_down_counter = 1

	def move_lasers(self, vel, obj):
		self.cooldown()
		for laser in self.lasers:
			laser.move(vel)
			if laser.off_screen(HEIGHT):
				self.lasers.remove(laser)
			elif laser.collision(obj):
				obj.health -= 10
				self.lasers.remove(laser)

#Player class
class Player(Ship):
	def __init__(self, x_pos, y_pos, health = 100):
		super().__init__(x_pos, y_pos, health)
		self.ship_img = YELLOW_SPACE_SHIP
		self.laser_img = YELLOW_LASER
		self.mask = pygame.mask.from_surface(self.ship_img)
		self.max_health = health
	
	def move_lasers(self, vel, objs):
		self.cooldown()
		for laser in self.lasers:
			laser.move(vel)
			if laser.off_screen(HEIGHT):
				self.lasers.remove(laser)
			else:
				for obj in objs:
					if laser.collision(obj):
						objs.remove(obj)
						if laser in self.lasers:
							self.lasers.remove(laser)
							

	def draw(self, window):
		super().draw(window)
		self.health_bar(window)

	def health_bar(self, window):
		pygame.draw.rect(window, (255,0,0), (self.x_pos, self.y_pos + self.ship_img.get_height() + 10, self.ship_img.get_width(),10))
		pygame.draw.rect(window, (0,255,0), (self.x_pos, self.y_pos + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health),10))
#Enemy Class
class Enemy(Ship):
	COLOR_MAP = {
		"red"  : (RED_SPACE_SHIP,RED_LASER),
		"blue" : (BLUE_SPACE_SHIP,BLUE_LASER),
		"green": (GREEN_SPACE_SHIP,GREEN_LASER)
	}
	
	def __init__(self, x_pos, y_pos, color, health = 100):
		super().__init__(x_pos, y_pos, health)
		self.ship_img, self.laser_img = self.COLOR_MAP[color]
		self.mask = pygame.mask.from_surface(self.ship_img)

	def move(self, vel):
		self.y_pos += vel

	def shoot(self):
		if self.cool_down_counter == 0:
			laser = Laser(self.x_pos - 20, self.y_pos, self.laser_img)
			self.lasers.append(laser)
			self.cool_down_counter = 1



#==================================================================================================#

#===========================================Main===================================================#

#The collision methode
def collide(obj, laser_obj):
	offset_x = laser_obj.x_pos - obj.x_pos
	offset_y = laser_obj.y_pos - obj.y_pos
	return obj.mask.overlap(laser_obj.mask, (offset_x, offset_y)) != None

def main():
	run = True
	FPS = 60
	level = 0 
	lives = 5
	clock = pygame.time.Clock()
	main_font = pygame.font.SysFont("comicsans",50)

	lost_font = pygame.font.SysFont("comicsans",60)
	lost = False
	lost_count = 0 

	#enemies settings
	enemies = []
	wave_length = 5
	enemy_vel = 1

	#player settings
	player_vel = 4
	player = Player(340, 650)

	#Laser settings:
	laser_vel = 5

	def redraw_window():
		WIN.blit(BG_IMAGE, (0,0))#==>sticking bg to the screen

		#Text Rendering 
		lives_label = main_font.render(f"lives : {lives} ", 1, (255,255,255))
		level_label = main_font.render(f"level : {level} ", 1, (255,255,255))
		WIN.blit(lives_label, (10,10)) #==> sticking the lives text to the screen
		WIN.blit(level_label, (WIDTH - level_label.get_width()-10,10)) #==> sticking the level text to the screen

		for enemy in enemies:
			enemy.draw(WIN)

		player.draw(WIN)# ==> test subject

		if lost:# ==> showing the lost message
			lost_label = lost_font.render('You Lost !', 1, (255,255,255))
			WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width(), HEIGHT/2 - lost_label.get_height()))

		pygame.display.update() #==> updating the frames 


	while run:
		clock.tick(FPS)
		redraw_window()# ==> refresh frame

		#checking if we lost or not
		if lives <= 0 or player.health <= 0:
			lost = True
			lost_count += 1

		if lost:
			if lost_count > FPS * 3 :
				run = False
			else:
				continue
		
		if len(enemies) == 0:
			level += 1	# ==> going to the next level
			wave_length += 5 # ==> incrimenting the number of enemies per wave
			for i in range(wave_length):#==> spawning enemies
				enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500,-100), random.choice(['red','blue','green']))
				enemies.append(enemy)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False

		
		#--------------------------------------Controls-------------------------------------------#				
		keys = pygame.key.get_pressed()

		if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and player.x_pos + player_vel > 0 : #left
			player.x_pos -= player_vel
		if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and player.x_pos + player_vel + player.get_width() < WIDTH: #right
			player.x_pos += player_vel
		if (keys[pygame.K_w] or keys[pygame.K_UP]) and player.y_pos + player_vel > 0: #forward
			player.y_pos -= player_vel
		if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and player.y_pos + player_vel + player.get_height() + 20 < HEIGHT: #backward
			player.y_pos += player_vel
		if keys[pygame.K_SPACE]:
			player.shoot()
		#-------------------------------------------------------------------------------------------#
		
		#---------------------------------Enemies Controls-----------------------------------------#
		for enemy in enemies[:]:
			enemy.move(enemy_vel)
			enemy.move_lasers(laser_vel,player)

			if random.randrange(0, 2*60) == 1:
				enemy.shoot()

			#checking if the player collides with the enemy :
			if collide(player, enemy):
				player.health -= 10
				enemies.remove(enemy)

			if enemy.y_pos + enemy.get_height() > HEIGHT:
				lives -=1
				enemies.remove(enemy)

		#-------------------------------------------------------------------------------------------#

		#checking if the players laser hit the enemy:
		player.move_lasers(-laser_vel, enemies)

#==================================================================================================#

#=============================================Main_Menu============================================#
def main_menu():
    title_font = pygame.font.SysFont("comicsans", 70)
    run = True
    while run:
        WIN.blit(BG_IMAGE, (0,0))
        title_label = title_font.render("Press the mouse to begin...", 1, (255,255,255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 400))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


#==================================================================================================#
main_menu()#==> execute the game