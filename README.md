AI Dungeon Master
Overview
AI Dungeon Master is a 2D roguelike dungeon crawler game built with Python and Pygame. Navigate a procedurally generated dungeon, avoid traps, battle enemies, collect treasures, and find the exit. Enemies use A* pathfinding to pursue the player, creating dynamic and challenging gameplay.
Features

Procedural Dungeon Generation: Each game generates a new dungeon with walls, treasures, traps, and enemies.
A Pathfinding: Enemies intelligently chase the player using the A algorithm.
Interactive HUD: Displays player health, treasure count, and in-game messages.
Game Over and Restart: Players can restart the game by pressing 'R' after a game over.
Visual Effects: Includes glowing effects for entities and a starry background for ambiance.

Requirements

Python 3.8+
Pygame 2.5.0+

Installation

Clone the Repository:
git clone https://github.com/yourusername/ai-dungeon-master.git
cd ai-dungeon-master


Install Dependencies:Ensure Python is installed, then install Pygame:
pip install pygame


Run the Game:
python ai_dungeon_master.py



Gameplay

Objective: Navigate to the green exit tile while collecting treasures (yellow tiles) and avoiding traps (red tiles) and enemies (red tiles).
Controls:
Arrow Keys: Move the player up, down, left, or right.
R: Restart the game after a game over.


Mechanics:
Health: Starts at 100. Traps deduct 10 health, enemy attacks deduct 20, and adjacent enemies deduct 10 periodically.
Treasures: Collecting treasures increases your score.
Enemies: Move toward the player every 15 frames using A* pathfinding.
Game Over: Occurs when health reaches 0. Press 'R' to restart.
Exit: Reaching the exit generates a new dungeon.



Code Structure

ai_dungeon_master.py: Main game file containing all game logic, rendering, and enemy AI.
Key Classes:
Enemy: Manages enemy movement and A* pathfinding.
AIDungeonMaster: Handles dungeon generation, player movement, enemy updates, and rendering.


Key Functions:
draw_tile: Renders dungeon tiles with visual effects.
draw_hud: Displays the heads-up display with health, treasure count, and messages.
main: Game loop handling input, updates, and rendering.




