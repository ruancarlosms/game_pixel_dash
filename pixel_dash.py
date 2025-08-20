import pgzrun
import random
import math
from pygame import Rect

# GAME SETTINGS
# All game settings are here for easy modification.
WIDTH = 800
HEIGHT = 600
TITLE = "Pixel Dash" # Nome do jogo alterado

# Physics and gameplay parameters
GRAVITY = 0.6
PLAYER_SPEED = 4
JUMP_POWER = 12
LEVEL_LENGTH = 8000
TOTAL_COINS = 30

# GLOBAL GAME STATE VARIABLES 
# These variables control the current state of the game.
game_state = "tutorial"
camera_x = 0
music_on = True
sounds_on = True
score = 0
all_coins_collected = False
coins = []
level_blocks = []
coin_animation_timer = 0

# Dictionaries to organize enemies, making them easier to manage.
enemies = {
    "walkers": [],
    "flyers": [],
    "jumpers": [],
    "swoopers": [],
    "spikes": []
}

# PLAYER 
# Initial setup for our hero
player = Actor("hero_idle_1", (150, 300))
player.vy = 0  # Vertical velocity for jumps and falls
player.on_ground = False
player.jumps_left = 2  # Counter for the double jump mechanic

# Player sprite animations
player_frames = {
    "idle": ["hero_idle_1", "hero_idle_2"],
    "run": ["hero_idle_1", "hero_idle_2"],
    "jump": ["hero_idle_1"]
}
player.animation_timer = 0
player.frame_idx = 0

# ANIMATED FINAL FLAG
# The flag that marks the end of the level, with its simple animation.
flag_actor = Actor("flag_1", (LEVEL_LENGTH - 300, 0))
flag_frames = ["flag_1", "flag_2"]
flag_timer = 0
flag_frame_idx = 0

# INTERFACE BUTTONS
# A class for menu buttons, making them reusable.
class Button:
    # A Button class that only uses pygame.Rect, as allowed.
    def __init__(self, rect, text, action, scale=1.5):
        self.rect = rect
        self.text = text
        self.action = action
        # The scale functionality is removed to comply with the rules.
        # It's assumed the button sprite 'botao.png' is pre-scaled to the desired size.
        self.image = images.botao
        self.scaled_image = images.botao

    def draw(self):
        img_rect = self.scaled_image.get_rect(center=self.rect.center)
        screen.surface.blit(self.scaled_image, img_rect.topleft)
        screen.draw.text(self.text, center=self.rect.center, color="black",
                         fontname="vcr_osd_mono", fontsize=40)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# Instantiating the menu buttons
start_button = Button(Rect(0, 0, 220, 50), "Start Game", "start")
start_button.rect.center = (WIDTH // 2, HEIGHT // 2 - 100)
quit_button = Button(Rect(0, 0, 220, 50), "Quit", "quit")
quit_button.rect.center = (WIDTH // 2, HEIGHT // 2 + 100)
music_button = Button(Rect(0, 0, 220, 50), "Music: ON", "music_toggle")
music_button.rect.center = (WIDTH // 2, HEIGHT // 2)
sounds_button = Button(Rect(0, 0, 220, 50), "Sounds: ON", "sounds_toggle")
sounds_button.rect.center = (WIDTH // 2, HEIGHT // 2 + 50)

# GENERAL CONTROL FUNCTIONS
def play_background_music():
    """Plays the background music if enabled."""
    global music_on
    if music_on:
        try:
            music.play("background_music")
            music.set_volume(0.04)
        except AttributeError:
            print("WARNING: Background music file not found.")

def stop_background_music():
    """Stops the background music."""
    global music_on
    music.stop()

def reset_game():
    """Resets all game state variables for a new game session."""
    global player, camera_x, score, all_coins_collected, coin_animation_timer
    score = 0
    player.image = "hero_idle_1"
    player.pos = (150, HEIGHT - 100)
    player.vy = 0
    player.on_ground = True
    player.jumps_left = 2
    camera_x = 0
    all_coins_collected = False
    coin_animation_timer = 0
    
    # Reload the level, enemies, and coins from scratch.
    create_level_blocks()
    spawn_enemies()
    create_level_coins()


# LEVEL CREATION FUNCTIONS
def ground_top_y():
    """Calculates the Y position of the top of the ground sprite."""
    return HEIGHT - images.ground.get_height()

def create_level_coins():
    """Places all coins in predefined, logical positions."""
    global coins
    coins.clear()
    ground_y = ground_top_y()
    
    # Adding coins in sections for a more intentional design.
    coins.extend([
        Actor("coin_1", (400, ground_y - 120)), Actor("coin_1", (600, ground_y - 200)),
        Actor("coin_1", (1300, ground_y - 120)), Actor("coin_1", (1550, ground_y - 200)),
        Actor("coin_1", (1800, ground_y - 270)), Actor("coin_1", (2500, ground_y - 200)),
        Actor("coin_1", (2800, ground_y - 250)), Actor("coin_1", (3100, ground_y - 200)),
        Actor("coin_1", (4750, ground_y - 150)), Actor("coin_1", (4900, ground_y - 200)),
        Actor("coin_1", (5050, ground_y - 250)), Actor("coin_1", (5800, ground_y - 200)),
        Actor("coin_1", (6000, ground_y - 250)), Actor("coin_1", (6200, ground_y - 300)),
        Actor("coin_1", (6800, ground_y - 120)), Actor("coin_1", (7000, ground_y - 200)),
        Actor("coin_1", (7200, ground_y - 280))
    ])
    
    for i in range(8):
        coins.append(Actor("coin_1", (3600 + i * 100, ground_y - 150)))
    for i in range(5):
        coins.append(Actor("coin_1", (7500 + i * 100, ground_y - 120)))

def create_level_blocks():
    """Defines the position of all blocks and spikes in the level.
    The placement is manual to ensure all platforms are reachable.
    """
    global level_blocks, enemies, flag_actor
    level_blocks.clear()
    enemies["spikes"].clear()
    
    ground_y = ground_top_y()
    spike_height = images.enemy_spike.get_height()
    
    # Section 1: Start and warm-up
    block_x = 400
    ground_width = images.ground.get_width()
    for i in range(5):
        level_blocks.append(Actor("ground", (block_x + i * ground_width, ground_y)))
    enemies["spikes"].append(Actor("enemy_spike", (block_x + 3 * ground_width, ground_y - spike_height / 2)))
    level_blocks.append(Actor("platform_small", (block_x + 6 * ground_width, ground_y - 50)))

    # Section 2: Platform climb
    climb_x = 1200
    level_blocks.extend([
        Actor("platform_large", (climb_x, ground_y - 100)),
        Actor("platform_medium", (climb_x + 250, ground_y - 180)),
        Actor("platform_small", (climb_x + 500, ground_y - 250)),
        Actor("platform_medium", (climb_x + 700, ground_y - 200))
    ])
    enemies["spikes"].append(Actor("enemy_spike", (climb_x + 250, ground_y - 180 - spike_height / 2)))

    # Section 3: Abyss
    abyss_y = ground_y - 150
    level_blocks.extend([
        Actor("platform_small", (2400, abyss_y)),
        Actor("platform_small", (2700, abyss_y + 50)),
        Actor("platform_small", (3000, abyss_y)),
        Actor("platform_medium", (3300, abyss_y - 50))
    ])

    # Section 4: Block bridge
    bridge_x = 3600
    bridge_y = ground_y - 100
    for i in range(8):
        platform_type = "platform_medium" if i % 2 == 0 else "platform_large"
        level_blocks.append(Actor(platform_type, (bridge_x + i * 100, bridge_y)))
    enemies["spikes"].extend([
        Actor("enemy_spike", (bridge_x + 250, ground_y - spike_height / 2)),
        Actor("enemy_spike", (bridge_x + 650, ground_y - spike_height / 2))
    ])

    # Section 5: Elevated platforms
    elevate_x = 5600
    level_blocks.extend([
        Actor("platform_large", (elevate_x, ground_y - 150)),
        Actor("platform_small", (elevate_x + 400, ground_y - 200)),
        Actor("platform_medium", (elevate_x + 700, ground_y - 250))
    ])
    enemies["spikes"].append(Actor("enemy_spike", (elevate_x + 100, ground_y - spike_height / 2)))

    # Section 6: Spikes challenge
    final_x = 7000
    level_blocks.extend([
        Actor("platform_small", (final_x - 300, ground_y - 100)),
        Actor("platform_small", (final_x - 150, ground_y - 180)),
        Actor("platform_medium", (final_x + 50, ground_y - 250))
    ])
    enemies["spikes"].extend([
        Actor("enemy_spike", (final_x + 250, ground_y - spike_height / 2)),
        Actor("enemy_spike", (final_x + 350, ground_y - spike_height / 2)),
        Actor("enemy_spike", (final_x + 450, ground_y - spike_height / 2))
    ])

    for i in range(5):
        level_blocks.append(Actor("ground", (final_x + 550 + i * images.ground.get_width(), ground_y)))
    final_block = Actor("ground", (LEVEL_LENGTH, ground_y))
    level_blocks.append(final_block)
    flag_actor.pos = (final_block.x, final_block.y - final_block.height / 2 - flag_actor.height / 2)

def spawn_enemies():
    """Creates and positions all enemies for the start of the level."""
    global enemies
    enemies["walkers"].clear(); enemies["flyers"].clear(); enemies["jumpers"].clear(); enemies["swoopers"].clear()

    enemies["walkers"].extend([
        {"actor": Actor("enemy_walk_1", (700, ground_top_y() - 20)), "left": 600, "right": 800, "dir": 1, "frames": ["enemy_walk_1", "enemy_walk_2"], "frame_idx": 0, "timer": 0},
        {"actor": Actor("enemy_walk_1", (2600, ground_top_y() - 20)), "left": 2500, "right": 2700, "dir": -1, "frames": ["enemy_walk_1", "enemy_walk_2"], "frame_idx": 0, "timer": 0},
        {"actor": Actor("enemy_walk_1", (4000, ground_top_y() - 200)), "left": 3800, "right": 4200, "dir": 1, "frames": ["enemy_walk_1", "enemy_walk_2"], "frame_idx": 0, "timer": 0},
        {"actor": Actor("enemy_walk_1", (6800, ground_top_y() - 20)), "left": 6600, "right": 7000, "dir": -1, "frames": ["enemy_walk_1", "enemy_walk_2"], "frame_idx": 0, "timer": 0}
    ])
    enemies["flyers"].extend([
        {"actor": Actor("enemy_fly_1", (1600, HEIGHT - 180)), "left": 1400, "right": 1800, "dir": 1, "frames": ["enemy_fly_1", "enemy_fly_2", "enemy_fly_3"], "frame_idx": 0, "timer": 0, "speed": 2},
        {"actor": Actor("enemy_fly_1", (3200, HEIGHT - 120)), "left": 3000, "right": 3400, "dir": -1, "frames": ["enemy_fly_1", "enemy_fly_2", "enemy_fly_3"], "frame_idx": 0, "timer": 0, "speed": 1.5},
        {"actor": Actor("enemy_fly_1", (5200, HEIGHT - 200)), "left": 5000, "right": 5400, "dir": 1, "frames": ["enemy_fly_1", "enemy_fly_2", "enemy_fly_3"], "frame_idx": 0, "timer": 0, "speed": 2.5}
    ])
    enemies["jumpers"].extend([
        {"actor": Actor("enemy_jump", (1000, ground_top_y() - 25)), "jump_timer": 0, "jump_delay": 0, "jump_count": 0, "pause_timer": 0, "y_start": ground_top_y() - 25, "jumping": False, "fall_speed": 0},
        {"actor": Actor("enemy_jump", (4400, ground_top_y() - 25)), "jump_timer": 20, "jump_delay": 0, "jump_count": 0, "pause_timer": 0, "y_start": ground_top_y() - 25, "jumping": False, "fall_speed": 0},
        {"actor": Actor("enemy_jump", (6200, ground_top_y() - 25)), "jump_timer": 60, "jump_delay": 0, "jump_count": 0, "pause_timer": 0, "y_start": ground_top_y() - 25, "jumping": False, "fall_speed": 0}
    ])
    enemies["swoopers"].extend([
        {"actor": Actor("enemy_swoop_1", (2000, HEIGHT - 300)), "speed": 2.5, "dir": 1, "frames": ["enemy_swoop_1", "enemy_swoop_2", "enemy_swoop_3"], "frame_idx": 0, "anim_timer": 0, "x_start": 2000, "y_start": HEIGHT - 300, "amplitude": 120, "frequency": 0.05},
        {"actor": Actor("enemy_swoop_1", (5800, HEIGHT - 250)), "speed": 2, "dir": -1, "frames": ["enemy_swoop_1", "enemy_swoop_2", "enemy_swoop_3"], "frame_idx": 0, "anim_timer": 0, "x_start": 5800, "y_start": HEIGHT - 250, "amplitude": 80, "frequency": 0.04}
    ])


# GAME LOGIC AND UPDATE FUNCTIONS
def update():
    """Main game update function, called 60 times per second."""
    global game_state, camera_x, all_coins_collected, score
    
    if game_state != "playing":
        return

    # --- Player logic ---
    moving = False
    if keyboard.a or keyboard.left:
        player.x -= PLAYER_SPEED
        moving = True
    if keyboard.d or keyboard.right:
        player.x += PLAYER_SPEED
        moving = True
        
    player.vy += GRAVITY
    player.y += player.vy
    
    top_y = ground_top_y()
    if player.bottom >= top_y:
        player.bottom = top_y
        player.vy = 0
        player.on_ground = True
        player.jumps_left = 2
    
    check_collisions()
    update_all_enemies()
    animate_coins()

    player.animation_timer = (player.animation_timer + 1) % 10
    if player.on_ground:
        player.image = player_frames["run"][player.animation_timer % len(player_frames["run"])] if moving else player_frames["idle"][player.animation_timer % len(player_frames["idle"])]
    else:
        player.image = player_frames["jump"][0]
        
    camera_x = max(0, player.x - WIDTH * 0.4)

    if hit_any_lethal_enemy():
        game_state = "game_over"
        stop_background_music()
        if sounds_on:
            try:
                sounds.game_over.set_volume(0.2)
                sounds.game_over.play()
            except AttributeError:
                print("WARNING: 'game_over.wav' sound file not found!")

    if player.x >= LEVEL_LENGTH and game_state == "playing":
        all_coins_collected = (score == TOTAL_COINS)
        game_state = "complete"
        stop_background_music()
        if sounds_on:
            try:
                sounds.victory.set_volume(0.2)
                sounds.victory.play()
            except AttributeError:
                print("WARNING: 'victory.wav' sound file not found!")

def check_collisions():
    """Checks for all player collisions with blocks, enemies, and coins."""
    global score, player
    
    for block in level_blocks:
        if player.colliderect(block):
            if player.vy >= 0 and player.bottom <= block.y + 10:
                player.bottom = block.top
                player.vy = 0
                player.on_ground = True
                player.jumps_left = 2
            elif player.vy < 0 and player.top >= block.bottom - 10:
                player.top = block.bottom
                player.vy = 0
    
    for enemy_list in [enemies['walkers'], enemies['flyers'], enemies['jumpers'], enemies['swoopers']]:
        for enemy_data in list(enemy_list):
            enemy_actor = enemy_data["actor"]
            if player.colliderect(enemy_actor):
                if player.vy > 0 and player.bottom <= enemy_actor.y + 10:
                    enemy_list.remove(enemy_data)
                    player.vy = -JUMP_POWER * 0.7
                    if sounds_on:
                        try:
                            sounds.squish.set_volume(0.2)
                            sounds.squish.play()
                        except AttributeError:
                            print("WARNING: 'squish.wav' sound file not found!")

    for coin in list(coins):
        if player.colliderect(coin):
            coins.remove(coin)
            score += 1
            if sounds_on:
                try:
                    sounds.coin_sound.set_volume(0.2)
                    sounds.coin_sound.play()
                except AttributeError:
                    print("WARNING: 'coin_sound.wav' sound file not found!")

def update_all_enemies():
    """Updates the position and animation of all enemies."""
    global flag_timer, flag_frame_idx, enemies
    
    # Update walkers
    for w in enemies["walkers"]:
        w["actor"].x += w["dir"] * 1.4
        if w["actor"].x < w["left"] or w["actor"].x > w["right"]:
            w["dir"] *= -1
        w["timer"] = (w["timer"] + 1) % 10
        if w["timer"] == 0:
            w["frame_idx"] = (w["frame_idx"] + 1) % len(w["frames"])
            w["actor"].image = w["frames"][w["frame_idx"]]
    
    # Update flyers
    for f in enemies["flyers"]:
        f["actor"].x += f["dir"] * f["speed"]
        if f["actor"].x < f["left"] or f["actor"].x > f["right"]:
            f["dir"] *= -1
        f["timer"] = (f["timer"] + 1) % 8
        if f["timer"] == 0:
            f["frame_idx"] = (f["frame_idx"] + 1) % len(f["frames"])
            f["actor"].image = f["frames"][f["frame_idx"]]
    
    # Update jumpers
    for j in enemies["jumpers"]:
        actor = j["actor"]
        if j["pause_timer"] > 0:
            j["pause_timer"] -= 1
        elif not j["jumping"]:
            j["jumping"] = True
            j["fall_speed"] = -8
            j["jump_count"] += 1
        
        if j["jumping"]:
            actor.y += j["fall_speed"]
            j["fall_speed"] += GRAVITY * 0.6
            if actor.y >= j["y_start"]:
                actor.y = j["y_start"]
                j["jumping"] = False
                if j["jump_count"] >= 2:
                    j["jump_count"] = 0
                    j["pause_timer"] = 60
        actor.x += 1
        
    # Update swoopers (with sinusoidal movement)
    for s in enemies["swoopers"]:
        actor = s["actor"]
        actor.x += s["speed"] * s["dir"]
        actor.y = s["y_start"] + s["amplitude"] * math.sin((actor.x - s["x_start"]) * s["frequency"])
        s["anim_timer"] = (s["anim_timer"] + 1) % 8
        if s["anim_timer"] == 0:
            s["frame_idx"] = (s["frame_idx"] + 1) % len(s["frames"])
            actor.image = s["frames"][s["frame_idx"]]
            
    # Animate the final flag
    flag_timer = (flag_timer + 1) % 15
    if flag_timer == 0:
        flag_frame_idx = (flag_frame_idx + 1) % len(flag_frames)
        flag_actor.image = flag_frames[flag_frame_idx]

def hit_any_lethal_enemy():
    """Checks if the player has a lethal collision.
    Only spikes are unconditionally lethal. Other enemy collisions are lethal
    only if they are not stomps.
    """
    global enemies, player
    for spike in enemies["spikes"]:
        if player.colliderect(spike):
            return True
            
    for enemy_list in [enemies['walkers'], enemies['flyers'], enemies['jumpers'], enemies['swoopers']]:
        for enemy_data in enemy_list:
            enemy_actor = enemy_data["actor"]
            if player.colliderect(enemy_actor):
                if not (player.vy > 0 and player.bottom <= enemy_actor.y + 10):
                    return True
            
    return False

def animate_coins():
    """Handles the animation logic for all coins."""
    global coin_animation_timer, coins
    coin_animation_timer += 1
    if coin_animation_timer >= 10:
        coin_animation_timer = 0
        if coins:
            current_frame = coins[0].image
            for coin in coins:
                coin.image = "coin_2" if current_frame == "coin_1" else "coin_1"


# DRAWING FUNCTIONS
def draw():
    """Main game drawing function."""
    if game_state == "tutorial":
        draw_tutorial()
    elif game_state == "menu":
        draw_menu()
    elif game_state == "playing":
        draw_game()
    elif game_state == "game_over":
        draw_game_over()
    elif game_state == "complete":
        draw_complete()

def draw_background():
    """Draws the background with a parallax effect."""
    try:
        bg = images.background_game
        bw = bg.get_width()
        offset = int(camera_x * 0.2) % bw
        screen.blit("background_game", (-offset, 0))
        screen.blit("background_game", (-offset + bw, 0))
    except KeyError:
        screen.fill((135, 206, 235))

def draw_ground():
    """Draws the infinite scrolling ground."""
    tile = images.ground
    tw = tile.get_width()
    y = ground_top_y()
    start_i = int((camera_x - 50) // tw)
    end_i = int((camera_x + WIDTH) // tw) + 2
    for i in range(start_i, end_i):
        screen.blit("ground", (i * tw - camera_x, y))

def draw_game():
    """Draws all game elements to the screen."""
    draw_background()
    draw_ground()
    
    for block in level_blocks:
        screen.blit(block.image, (block.x - camera_x, block.y))
    
    for enemy_list in enemies.values():
        for enemy in enemy_list:
            actor = enemy["actor"] if isinstance(enemy, dict) and "actor" in enemy else enemy
            screen.blit(actor.image, (actor.x - camera_x, actor.y))

    for coin in coins:
        screen.blit(coin.image, (coin.x - camera_x, coin.y))

    screen.blit(player.image, (player.x - camera_x, player.y))
    screen.blit(flag_actor.image, (flag_actor.x - camera_x, flag_actor.y))

    screen.draw.text(f"Score: {score}", topright=(WIDTH - 20, 10),
                     color="white", fontname="vcr_osd_mono", fontsize=30)

def draw_tutorial():
    """Draws the tutorial screen."""
    draw_background()
    screen.draw.text("Bem-vindo ao Pixel Dash!", center=(WIDTH // 2, HEIGHT // 2 - 150),
                     fontsize=32, color="white", fontname="vcr_osd_mono")
    screen.draw.text("Controles:", center=(WIDTH // 2, HEIGHT // 2 - 50),
                     fontsize=32, color="yellow", fontname="vcr_osd_mono")
    screen.draw.text("W ou Seta para Cima para Pular", center=(WIDTH // 2, HEIGHT // 2),
                     fontsize=24, color="white", fontname="vcr_osd_mono")
    screen.draw.text("Aperte a tecla de pulo novamente no ar para Pulo Duplo.", center=(WIDTH // 2, HEIGHT // 2 + 30),
                     fontsize=24, color="white", fontname="vcr_osd_mono")
    screen.draw.text("A ou Seta para Esquerda para mover para a Esquerda", center=(WIDTH // 2, HEIGHT // 2 + 60),
                     fontsize=24, color="white", fontname="vcr_osd_mono")
    screen.draw.text("D ou Seta para Direita para mover para a Direita", center=(WIDTH // 2, HEIGHT // 2 + 90),
                     fontsize=24, color="white", fontname="vcr_osd_mono")
    screen.draw.text("Pressione qualquer tecla para continuar...", center=(WIDTH // 2, HEIGHT // 2 + 200),
                     fontsize=28, color="red", fontname="vcr_osd_mono")

def draw_menu():
    """Draws the main menu screen."""
    draw_background()
    draw_ground()
    start_button.draw()
    quit_button.draw()
    music_button.text = f"Music: {'ON' if music_on else 'OFF'}"
    music_button.draw()
    sounds_button.text = f"Sounds: {'ON' if sounds_on else 'OFF'}"
    sounds_button.draw()

def draw_game_over():
    """Draws the 'Game Over' screen."""
    draw_background()
    draw_ground()
    screen.draw.text("GAME OVER", center=(WIDTH // 2, HEIGHT // 2 - 60),
                     fontsize=72, color="red", fontname="vcr_osd_mono")
    screen.draw.text("Clique para reiniciar", center=(WIDTH // 2, HEIGHT // 2 + 10),
                     fontsize=36, color="white", fontname="vcr_osd_mono")

def draw_complete():
    """Draws the 'Level Complete' screen."""
    draw_background()
    draw_ground()
    if all_coins_collected:
        screen.draw.text("Level Completo. Parabéns!",
                         center=(WIDTH // 2, HEIGHT // 2 - 30),
                         fontsize=30, color="yellow", fontname="vcr_osd_mono")
        screen.draw.text("Você conseguiu coletar todas as moedas!",
                         center=(WIDTH // 2, HEIGHT // 2 + 10),
                         fontsize=30, color="yellow", fontname="vcr_osd_mono")
    else:
        screen.draw.text("LEVEL COMPLETO", center=(WIDTH // 2, HEIGHT // 2 - 40),
                         fontsize=72, color="yellow", fontname="vcr_osd_mono")
        screen.draw.text(f"Sua pontuação: {score}", center=(WIDTH // 2, HEIGHT // 2 + 40),
                         fontsize=40, color="yellow", fontname="vcr_osd_mono")

def on_key_down(key):
    """Handles keyboard events."""
    global game_state
    if game_state == "tutorial":
        game_state = "menu"
        return
        
    if game_state != "playing":
        return
        
    if key in (keys.W, keys.UP, keys.SPACE) and player.jumps_left > 0:
        player.vy = -JUMP_POWER
        player.jumps_left -= 1
        if sounds_on:
            try:
                sounds.jump.set_volume(0.2)
                sounds.jump.play()
            except AttributeError:
                print("WARNING: 'jump.wav' sound file not found!")

def on_mouse_down(pos):
    """Handles mouse click events."""
    global game_state, music_on, sounds_on
    if game_state == "menu":
        if start_button.is_clicked(pos):
            reset_game()
            game_state = "playing"
            play_background_music()
        elif quit_button.is_clicked(pos):
            exit()
        elif music_button.is_clicked(pos):
            music_on = not music_on
            if music_on:
                play_background_music()
            else:
                stop_background_music()
        elif sounds_button.is_clicked(pos):
            sounds_on = not sounds_on
    elif game_state == "game_over" or game_state == "complete":
        game_state = "menu"

reset_game()
pgzrun.go()