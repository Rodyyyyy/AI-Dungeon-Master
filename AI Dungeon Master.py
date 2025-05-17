import pygame
import random
import math
from collections import deque
import heapq

pygame.init()
pygame.font.init()

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("AI Dungeon Master")

COLORS = {
    'background': (10, 5, 20),
    'dungeon_wall': (60, 40, 30),
    'dungeon_floor': (30, 25, 35),
    'corridor': (35, 30, 40),
    'player': (100, 200, 255),
    'enemy': (255, 80, 80),
    'treasure': (255, 215, 0),
    'trap': (255, 50, 50),
    'exit': (50, 255, 50),
    'health': (255, 60, 60),
    'text': (230, 230, 250),
    'highlight': (255, 165, 0),
    'shadow': (0, 0, 0, 150),
    'game_over': (255, 50, 50)
}

title_font = pygame.font.Font(None, 72)
header_font = pygame.font.Font(None, 48)
main_font = pygame.font.Font(None, 36)
hud_font = pygame.font.Font(None, 32)


def draw_tile(x, y, tile_type, size=40, offset_x=400, offset_y=200):
    rect = pygame.Rect(offset_x + x * size, offset_y + y * size, size, size)

    if tile_type in COLORS:
        pygame.draw.rect(screen, COLORS[tile_type], rect)
    elif tile_type == 'floor':
        pygame.draw.rect(screen, COLORS['dungeon_floor'], rect)
    elif tile_type == 'wall':
        pygame.draw.rect(screen, COLORS['dungeon_wall'], rect)

    if tile_type == 'wall':
        for _ in range(5):
            px = random.randint(rect.left, rect.right)
            py = random.randint(rect.top, rect.bottom)
            pygame.draw.circle(screen, (COLORS['dungeon_wall'][0] + random.randint(-20, 20),
                                        COLORS['dungeon_wall'][1] + random.randint(-20, 20),
                                        COLORS['dungeon_wall'][2] + random.randint(-20, 20)), (px, py), 1)

    if tile_type in ['player', 'enemy', 'treasure', 'trap', 'exit']:
        glow_surf = pygame.Surface((size + 10, size + 10), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*COLORS[tile_type], 50), (size // 2 + 5, size // 2 + 5), size // 2 + 5)
        screen.blit(glow_surf, (rect.x - 5, rect.y - 5))


def draw_hud(player_health, treasure_count, messages):
    hud_bg = pygame.Surface((SCREEN_WIDTH, 150), pygame.SRCALPHA)
    hud_bg.fill((20, 15, 30, 220))
    screen.blit(hud_bg, (0, SCREEN_HEIGHT - 150))

    health_text = hud_font.render(f"Health: {player_health}/100", True, COLORS['text'])
    screen.blit(health_text, (20, SCREEN_HEIGHT - 130))

    health_bar_bg = pygame.Rect(20, SCREEN_HEIGHT - 100, 200, 20)
    pygame.draw.rect(screen, (50, 50, 50), health_bar_bg)
    health_bar = pygame.Rect(20, SCREEN_HEIGHT - 100, player_health * 2, 20)
    pygame.draw.rect(screen, COLORS['health'], health_bar)

    treasure_text = hud_font.render(f"Treasures: {treasure_count}", True, COLORS['text'])
    screen.blit(treasure_text, (250, SCREEN_HEIGHT - 130))

    msg_text = hud_font.render("Messages:", True, COLORS['text'])
    screen.blit(msg_text, (500, SCREEN_HEIGHT - 130))

    for i, msg in enumerate(messages[-3:]):
        msg_surface = hud_font.render(msg, True, COLORS['text'])
        screen.blit(msg_surface, (500, SCREEN_HEIGHT - 100 + i * 25))


class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.health = 50
        self.attack_cooldown = 0

    def move_toward_player(self, dungeon, player_pos):
        path = self.a_star_search((self.x, self.y), player_pos, dungeon)
        if path and len(path) > 1:
            next_pos = path[1]
            if dungeon[next_pos[1]][next_pos[0]] != '#':
                self.x, self.y = next_pos

    def a_star_search(self, start, goal, dungeon):
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        neighbors = [(0, 1), (1, 0), (0, -1), (-1, 0)]

        close_set = set()
        came_from = {}
        gscore = {start: 0}
        fscore = {start: heuristic(start, goal)}
        oheap = []
        heapq.heappush(oheap, (fscore[start], start))

        while oheap:
            current = heapq.heappop(oheap)[1]

            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                path.reverse()
                return path

            close_set.add(current)
            for i, j in neighbors:
                neighbor = current[0] + i, current[1] + j

                if (0 <= neighbor[0] < len(dungeon[0]) and
                        0 <= neighbor[1] < len(dungeon) and
                        dungeon[neighbor[1]][neighbor[0]] != '#'):

                    tentative_g_score = gscore[current] + 1

                    if neighbor in close_set and tentative_g_score >= gscore.get(neighbor, 0):
                        continue

                    if tentative_g_score < gscore.get(neighbor, 0) or neighbor not in [i[1] for i in oheap]:
                        came_from[neighbor] = current
                        gscore[neighbor] = tentative_g_score
                        fscore[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                        heapq.heappush(oheap, (fscore[neighbor], neighbor))

        return []

class AIDungeonMaster:
    def __init__(self):
        self.dungeon_width = 20
        self.dungeon_height = 15
        self.dungeon = []
        self.player_pos = (1, 1)
        self.enemies = []
        self.traps = []
        self.treasures = []
        self.exit_pos = (self.dungeon_width - 2, self.dungeon_height - 2)
        self.player_health = 100
        self.treasure_count = 0
        self.messages = ["Welcome to the dungeon!"]
        self.game_over = False
        self.generate_open_dungeon()
        self.enemy_move_timer = 0

    def generate_open_dungeon(self):
        self.dungeon = []

        for y in range(self.dungeon_height):
            row = []
            for x in range(self.dungeon_width):
                if x == 0 or y == 0 or x == self.dungeon_width - 1 or y == self.dungeon_height - 1:
                    row.append('#')
                else:
                    row.append('.')
            self.dungeon.append(row)

        wall_count = int(self.dungeon_width * self.dungeon_height * 0.1)
        for _ in range(wall_count):
            x = random.randint(1, self.dungeon_width - 2)
            y = random.randint(1, self.dungeon_height - 2)
            if (x, y) != self.player_pos and (x, y) != self.exit_pos:
                self.dungeon[y][x] = '#'

        self.player_pos = (1, 1)
        self.dungeon[self.player_pos[1]][self.player_pos[0]] = '.'

        self.exit_pos = (self.dungeon_width - 2, self.dungeon_height - 2)
        self.dungeon[self.exit_pos[1]][self.exit_pos[0]] = '.'

        self.enemies = []
        for _ in range(5):
            while True:
                x = random.randint(1, self.dungeon_width - 2)
                y = random.randint(1, self.dungeon_height - 2)
                if (self.dungeon[y][x] == '.' and
                        (x, y) != self.player_pos and
                        (x, y) != self.exit_pos and
                        abs(x - self.player_pos[0]) + abs(y - self.player_pos[1]) > 5):
                    self.enemies.append(Enemy(x, y))
                    break

        self.treasures = []
        for _ in range(10):
            while True:
                x = random.randint(1, self.dungeon_width - 2)
                y = random.randint(1, self.dungeon_height - 2)
                if (self.dungeon[y][x] == '.' and
                        (x, y) != self.player_pos and
                        (x, y) != self.exit_pos and
                        not any((x, y) == (e.x, e.y) for e in self.enemies)):
                    self.treasures.append((x, y))
                    break

        self.traps = []
        for _ in range(8):
            while True:
                x = random.randint(1, self.dungeon_width - 2)
                y = random.randint(1, self.dungeon_height - 2)
                if (self.dungeon[y][x] == '.' and
                        (x, y) != self.player_pos and
                        (x, y) != self.exit_pos and
                        (x, y) not in self.treasures and
                        not any((x, y) == (e.x, e.y) for e in self.enemies)):
                    self.traps.append((x, y))
                    break

    def move_player(self, dx, dy):
        if self.game_over:
            return

        new_x = self.player_pos[0] + dx
        new_y = self.player_pos[1] + dy

        if new_x < 0 or new_x >= self.dungeon_width or new_y < 0 or new_y >= self.dungeon_height:
            self.messages.append("You can't go that way!")
            return

        if self.dungeon[new_y][new_x] == '#':
            self.messages.append("You bump into a wall.")
            return

        if (new_x, new_y) in self.traps:
            self.player_health -= 10
            self.traps.remove((new_x, new_y))
            self.messages.append("You triggered a trap! -10 health")
            if self.player_health <= 0:
                self.messages.append("You have died!")
                self.player_health = 0
                self.game_over = True

        if (new_x, new_y) in self.treasures:
            self.treasures.remove((new_x, new_y))
            self.treasure_count += 1
            self.messages.append("You found treasure!")

        for enemy in self.enemies[:]:
            if (new_x, new_y) == (enemy.x, enemy.y):
                self.player_health -= 20
                self.enemies.remove(enemy)
                self.messages.append("You were attacked by an enemy! -20 health")
                if self.player_health <= 0:
                    self.messages.append("You have died!")
                    self.player_health = 0
                    self.game_over = True

        if (new_x, new_y) == self.exit_pos:
            self.messages.append("Congratulations! You found the exit!")
            self.generate_open_dungeon()

        self.player_pos = (new_x, new_y)

    def update_enemies(self):
        if self.game_over:
            return

        self.enemy_move_timer += 1
        if self.enemy_move_timer >= 15:
            self.enemy_move_timer = 0
            for enemy in self.enemies:
                if abs(enemy.x - self.player_pos[0]) + abs(enemy.y - self.player_pos[1]) == 1:
                    self.player_health -= 10
                    self.messages.append("An enemy attacks you! -10 health")
                    if self.player_health <= 0:
                        self.messages.append("You have died!")
                        self.player_health = 0
                        self.game_over = True
                else:
                    enemy.move_toward_player(self.dungeon, self.player_pos)

    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        game_over_text = title_font.render("GAME OVER", True, COLORS['game_over'])
        restart_text = header_font.render("Press R to restart", True, COLORS['text'])

        screen.blit(game_over_text,
                    (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2,
                     SCREEN_HEIGHT // 2 - game_over_text.get_height() // 2))
        screen.blit(restart_text,
                    (SCREEN_WIDTH // 2 - restart_text.get_width() // 2,
                     SCREEN_HEIGHT // 2 + game_over_text.get_height()))

    def draw(self):
        screen.fill(COLORS['background'])

        for _ in range(100):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            brightness = random.randint(100, 255)
            pygame.draw.circle(screen, (brightness, brightness, brightness), (x, y), 1)

        dungeon_surface_width = self.dungeon_width * 40
        dungeon_surface_height = self.dungeon_height * 40
        offset_x = (SCREEN_WIDTH - dungeon_surface_width) // 2
        offset_y = (SCREEN_HEIGHT - dungeon_surface_height) // 2 - 50

        for y in range(self.dungeon_height):
            for x in range(self.dungeon_width):
                if self.dungeon[y][x] == '#':
                    draw_tile(x, y, 'wall', 40, offset_x, offset_y)
                else:
                    draw_tile(x, y, 'floor', 40, offset_x, offset_y)

        for treasure in self.treasures:
            draw_tile(treasure[0], treasure[1], 'treasure', 40, offset_x, offset_y)

        for trap in self.traps:
            draw_tile(trap[0], trap[1], 'trap', 40, offset_x, offset_y)

        for enemy in self.enemies:
            draw_tile(enemy.x, enemy.y, 'enemy', 40, offset_x, offset_y)

        draw_tile(self.exit_pos[0], self.exit_pos[1], 'exit', 40, offset_x, offset_y)
        draw_tile(self.player_pos[0], self.player_pos[1], 'player', 40, offset_x, offset_y)

        draw_hud(self.player_health, self.treasure_count, self.messages)

        title = header_font.render("AI Dungeon Master", True, COLORS['highlight'])
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 20))

        if self.game_over:
            self.draw_game_over()

        pygame.display.flip()


def main():
    clock = pygame.time.Clock()
    game = AIDungeonMaster()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    game.move_player(0, -1)
                elif event.key == pygame.K_DOWN:
                    game.move_player(0, 1)
                elif event.key == pygame.K_LEFT:
                    game.move_player(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    game.move_player(1, 0)
                elif event.key == pygame.K_r:
                    game = AIDungeonMaster()

        game.update_enemies()
        game.draw()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()