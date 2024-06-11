import pygame
from sys import exit
from random import randint, choice

# File handling functions
def load_scores():
    try:
        with open('scores.txt', 'r') as file:
            lines = file.readlines()
            last_score = int(lines[0].strip())
            high_score = int(lines[1].strip())
    except FileNotFoundError:
        last_score = 0
        high_score = 0
    return last_score, high_score

def save_scores(last_score, high_score):
    with open('scores.txt', 'w') as file:
        file.write(f"{last_score}\n")
        file.write(f"{high_score}\n")

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        try:
            player_walk_1 = pygame.image.load('graphics/player/player_walk_1.png').convert_alpha()
            player_walk_2 = pygame.image.load('graphics/player/player_walk_2.png').convert_alpha()
            self.player_walk = [player_walk_1, player_walk_2]
            self.player_index = 0
            self.player_jump = pygame.image.load('graphics/player/jump.png').convert_alpha()

            self.image = self.player_walk[self.player_index]
            self.rect = self.image.get_rect(midbottom=(80, 300))
            self.gravity = 0

            self.jump_sound = pygame.mixer.Sound('audio/jump.mp3')
            self.jump_sound.set_volume(0.5)
        except pygame.error as e:
            print(f"Error loading player resources: {e}")
            pygame.quit()
            exit()

    def player_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and self.rect.bottom >= 300:
            self.gravity = -20
            self.jump_sound.play()

    def apply_gravity(self):
        self.gravity += 1
        self.rect.y += self.gravity
        if self.rect.bottom >= 300:
            self.rect.bottom = 300

    def animation_state(self):
        if self.rect.bottom < 300:
            self.image = self.player_jump
        else:
            self.player_index += 0.1
            if self.player_index >= len(self.player_walk): self.player_index = 0
            self.image = self.player_walk[int(self.player_index)]

    def update(self):
        self.player_input()
        self.apply_gravity()
        self.animation_state()

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, type):
        super().__init__()
        try:
            if type == 'fly':
                fly_1 = pygame.image.load('graphics/fly/fly1.png').convert_alpha()
                fly_2 = pygame.image.load('graphics/fly/fly2.png').convert_alpha()
                self.frames = [fly_1, fly_2]
                y_pos = 210
            else:
                snail_1 = pygame.image.load('graphics/snail/snail1.png').convert_alpha()
                snail_2 = pygame.image.load('graphics/snail/snail2.png').convert_alpha()
                self.frames = [snail_1, snail_2]
                y_pos = 300

            self.animation_index = 0
            self.image = self.frames[self.animation_index]
            self.rect = self.image.get_rect(midbottom=(randint(900, 1100), y_pos))
        except pygame.error as e:
            print(f"Error loading obstacle resources: {e}")
            pygame.quit()
            exit()

    def animation_state(self):
        self.animation_index += 0.1
        if self.animation_index >= len(self.frames): self.animation_index = 0
        self.image = self.frames[int(self.animation_index)]

    def update(self):
        self.animation_state()
        self.rect.x -= 6
        self.destroy()

    def destroy(self):
        if self.rect.x <= -100:
            self.kill()

def display_score():
    current_time = int(pygame.time.get_ticks() / 1000) - start_time
    score_surf = test_font.render(f'Score: {current_time}', False, (64, 64, 64))
    score_rect = score_surf.get_rect(center=(400, 50))
    screen.blit(score_surf, score_rect)
    return current_time

def collision_sprite():
    if pygame.sprite.spritecollide(player.sprite, obstacle_group, False):
        obstacle_group.empty()
        return False
    else:
        return True

pygame.init()
screen = pygame.display.set_mode((800, 400))
pygame.display.set_caption('Jump Mania')
clock = pygame.time.Clock()

try:
    test_font = pygame.font.Font('font/Pixeltype.ttf', 50)
    bg_music = pygame.mixer.Sound('audio/music.wav')
    bg_music.play(loops=-1)
except pygame.error as e:
    print(f"Error loading font or background music: {e}")
    pygame.quit()
    exit()

# Groups
player = pygame.sprite.GroupSingle()
player.add(Player())

obstacle_group = pygame.sprite.Group()

try:
    sky_surface = pygame.image.load('graphics/Sky.png').convert()
    ground_surface = pygame.image.load('graphics/ground.png').convert()

    # Intro screen
    player_stand = pygame.image.load('graphics/player/player_stand.png').convert_alpha()
    player_stand = pygame.transform.rotozoom(player_stand, 0, 2)
    player_stand_rect = player_stand.get_rect(center=(400, 200))

    game_name = test_font.render('Jump Mania', False, (111, 196, 169))
    game_name_rect = game_name.get_rect(center=(400, 80))

    game_message = test_font.render('Press space to run', False, (111, 196, 169))
    game_message_rect = game_message.get_rect(center=(400, 330))
except pygame.error as e:
    print(f"Error loading graphics: {e}")
    pygame.quit()
    exit()

# Timer
obstacle_timer = pygame.USEREVENT + 1
pygame.time.set_timer(obstacle_timer, 1500)

game_active = False
start_time = 0
score = 0

# Load scores
last_score, high_score = load_scores()

while True:
    try:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if game_active:
                if event.type == obstacle_timer:
                    obstacle_group.add(Obstacle(choice(['fly', 'snail', 'snail', 'snail'])))

            else:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    game_active = True
                    start_time = int(pygame.time.get_ticks() / 1000)

        if game_active:
            screen.blit(sky_surface, (0, 0))
            screen.blit(ground_surface, (0, 300))
            score = display_score()

            player.draw(screen)
            player.update()

            obstacle_group.draw(screen)
            obstacle_group.update()

            game_active = collision_sprite()

            if not game_active:
                last_score = score
                if score > high_score:
                    high_score = score
                save_scores(last_score, high_score)

        else:
            screen.fill((94, 129, 162))
            screen.blit(player_stand, player_stand_rect)

            score_message = test_font.render(f'Your score: {score}', False, (111, 196, 169))
            score_message_rect = score_message.get_rect(center=(400, 330))
            screen.blit(game_name, game_name_rect)

            last_score_message = test_font.render(f'Last score: {last_score}', False, (111, 196, 169))
            last_score_message_rect = last_score_message.get_rect(center=(200, 180))

            high_score_message = test_font.render(f'High score: {high_score}', False, (111, 196, 169))
            high_score_message_rect = high_score_message.get_rect(center=(200, 140))

            screen.blit(high_score_message, high_score_message_rect)
            screen.blit(last_score_message, last_score_message_rect)

            if score == 0:
                screen.blit(game_message, game_message_rect)
            else:
                screen.blit(score_message, score_message_rect)

        pygame.display.update()
        clock.tick(60)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        pygame.quit()
        exit()
