import sys, logging, open_color, arcade, datetime, random

version = (3, 7)
assert sys.version_info >= version, "This script requires at least Python {0}.{1}".format(version[0], version[1])

logging.basicConfig(format='[%(filename)s:%(lineno)d] %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Set constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Space Shooter" 
ENEMY_COLOR_DIFFICULTIES = ["Blue", "Green", "Red", "Black"] # The colors of enemies based on their difficulty (index).

PLAYER_BULLET_DAMAGE = 10
PLAYER_HP = 200
PLAYER_FIRING_RATE = 350 # 1 shot per interval (Measured in milliseconds)
BASE_ENEMY_HP = 30
BASE_ENEMY_BULLET_DAMAGE = 5
BASE_ENEMY_FIRING_RATE = 4000 # 1 shot per interval (Measured in milliseconds)
ENEMY_MAX_SPEED = 3 # Movement speed of enemy.
BULLET_SPEED = 8

ENEMY_LOWER_BOUNDARY = SCREEN_HEIGHT / 3 # Enemies cannot cross the lower boundary
PLAYER_UPPER_BOUNDARY = SCREEN_HEIGHT / 4 # Player cannot cross the upper boundary

HIT_SCORE = 5 # Points awarded for landing a hit.
BASE_KILL_SCORE = 100 # Points awarded for killing an enemy.

#################################

class Player(arcade.Sprite):
    def __init__(self):
        """Initializes the player."""
        super().__init__("assets/players/playerShip1_blue.png", 0.5)
        
        (self.center_x, self.center_y) = (SCREEN_WIDTH / 2, PLAYER_UPPER_BOUNDARY / 2)
        self.hp = PLAYER_HP

        # List of all bullets fired by the player.
        self.bullet_list = arcade.SpriteList()

        # Time since last fired shot.
        self.time_last_shot_fired = datetime.datetime.now()

        # Toggle for if the player is shooting.
        self.is_shooting = False

    def fire_bullet(self):
        """Shoot only if the player is shooting and if enough time has elapsed since last shot."""
        if (self.is_shooting and (datetime.datetime.now() - self.time_last_shot_fired).total_seconds() * 1000 >= PLAYER_FIRING_RATE):
            self.bullet_list.append(Player_Bullet((self.center_x, self.center_y + self.width / 2), BULLET_SPEED, PLAYER_BULLET_DAMAGE))
            self.time_last_shot_fired = datetime.datetime.now() # Update time since last shot.

    def set_shooting(self, boolean):
        """Toggles whether not the player is shooting."""
        self.is_shooting = boolean

    def update(self):
        """Attempts to fire a bullet and moves all the bullets in the list."""
        self.fire_bullet()
        self.bullet_list.update()

    def move(self, x, y):
        """Moves the player to the given coordinates."""
        self.center_x = x
        self.center_y = min(y, PLAYER_UPPER_BOUNDARY - self.height / 2) # Player must remain below the upper boundary.
#################################

class Player_Bullet(arcade.Sprite):
    def __init__(self, position, velocity, damage):
        """Initializes a player bullet."""
        super().__init__("assets/bullets/green_bullet.png")

        (self.center_x, self.center_y) = position
        self.velocity = velocity
        self.damage = damage

    def update(self):
        """Moves the bullet."""
        self.center_y += self.velocity

        # Kill the bullet if it leaves the screen.
        if (self.center_y > SCREEN_HEIGHT):
            self.kill()

#################################

class Enemy(arcade.Sprite):
    def __init__(self, difficulty, position):
        """Initializes the enemy."""

        # The difficulty must be valid.
        if (difficulty > 4 or difficulty < 1):
            raise ValueError("Not a valid difficulty.")

        super().__init__("assets/enemies/enemy{}.png".format(ENEMY_COLOR_DIFFICULTIES[difficulty - 1]), 0.5)
        
        (self.center_x, self.center_y) = position
        (self.dx, self.dy) = (0, 0)

        self.hp = BASE_ENEMY_HP * difficulty # enemy hp is equal to the base hp multiplied by the difficulty.
        self.bullet_damage = BASE_ENEMY_BULLET_DAMAGE * difficulty # enemy bullet dmg is the base multiplied by the difficulty.
        self.score = BASE_KILL_SCORE * difficulty / 2 # how many points this enemy is worth when killed.

        self.firing_rate = BASE_ENEMY_FIRING_RATE / difficulty # in milliseconds and shrinks as difficulty increases.
        self.velocity_change_rate = 1000 # time in milliseconds how often to change velocity
        
        self.bullet_list = arcade.SpriteList() # List of all bullets fired by this enemy

        
        self.time_last_velocity_change = datetime.datetime.now() # Time of last update to enemy velocity.
        self.time_last_shot_fired = datetime.datetime.now() # Time of last shot fired by enemy.

    def update(self):
        """Moves the enemy randomly and attempts to fire bullets and move them."""
        self.update_velocity()
        self.fire_bullet()
        self.move()
        self.bullet_list.update()

    def update_velocity(self):
        """Updates the enemy velocity if enough time has passed since last update."""
        if ((datetime.datetime.now() - self.time_last_velocity_change).total_seconds() * 1000 >= self.velocity_change_rate):
            # Randomly generate the dx and dy speeds.
            self.dx = random.randint(0, ENEMY_MAX_SPEED) * (1 if (random.randint(0, 1) == 0) else -1)
            self.dy = random.randint(0, ENEMY_MAX_SPEED) * (1 if (random.randint(0, 1) == 0) else -1)

            # If the enemy is against a border, make sure the enemy moves away from the border by adjusting velocity.
            if (self.center_x == SCREEN_WIDTH - self.width / 2):
                self.dx =  abs(self.dx) * -1
            elif (self.center_x == self.width / 2):
                self.dx = abs(self.dx)

            if (self.center_y == SCREEN_HEIGHT - self.height / 2):
                self.dy = abs(self.dy) * -1
            elif (self.center_y == ENEMY_LOWER_BOUNDARY + self.height / 2):
                self.dy = abs(self.dy)

            # Update the time of the last velocity change
            self.time_last_velocity_change = datetime.datetime.now()

    def move(self):
        """Moves the enemy based on velocity."""
        self.center_x += self.dx
        self.center_y += self.dy

        # Ensure the enemy does not go out of its bounds.
        self.center_x = min(self.center_x, SCREEN_WIDTH - self.width / 2)
        self.center_x = max(self.center_x, self.width / 2)

        self.center_y = min(self.center_y, SCREEN_HEIGHT - self.height / 2)
        self.center_y = max(self.center_y, ENEMY_LOWER_BOUNDARY + self.height / 2)
       
    def fire_bullet(self):
        """Fires a bullet if enough time has passed."""
        if ((datetime.datetime.now() - self.time_last_shot_fired).total_seconds() * 1000 >= self.firing_rate):
            self.bullet_list.append(Enemy_Bullet((self.center_x, self.center_y - self.width / 2), -1 * BULLET_SPEED, self.bullet_damage))
            self.time_last_shot_fired = datetime.datetime.now() # Update time of last fired bullet.
        

#################################

class Enemy_Bullet(arcade.Sprite):
    def __init__(self, position, velocity, damage):
        """Iniitializes the bullet."""
        super().__init__("assets/bullets/red_bullet.png", 1)

        (self.center_x, self.center_y) = position
        self.velocity = velocity
        self.damage = damage

    def update(self):
        """Moves the bullet."""
        self.center_y += self.velocity

        # Kill the bullet if it leaves the screen.
        if (self.center_y < 0):
            self.kill()

#################################

class Window(arcade.Window):
    def __init__(self, width, height, title):
        # Call super class init function.
        super().__init__(width, height, title)

        # Make mouse disappear when it's over the window.
        self.set_mouse_visible(False)

        # Set background color of window.
        arcade.set_background_color(open_color.black)

    def setup(self):
        """Set up required sprites and data."""

        # List of all the enemies.
        self.enemy_list = arcade.SpriteList()

        # Create the player.
        self.player = Player()
        self.score = 0

        # Boolean that tracks if the game is over or not.
        self.game_over = False

        # Keeps track of where hit markers are.
        self.hit_list = arcade.SpriteList()
        self.last_clear_hit_list = datetime.datetime.now() # Time of the last time the hit_list was cleared.
        self.clear_hit_list_interval = 200 # Clear the list at this interval (measured in milliseconds).

        # Contains the background sprites
        self.background_list = arcade.SpriteList()
        self.background_speed = 5

        # Set up scrolling background.
        self.background_1 = arcade.Sprite("assets/background/space.png", 1)
        self.background_1.center_x = SCREEN_WIDTH / 2
        self.background_1.center_y = SCREEN_HEIGHT / 2
        self.background_1.change_y = -5 # Set scrolling speed.


        self.background_2 = arcade.Sprite("assets/background/space.png", 1)
        self.background_2.center_x = SCREEN_WIDTH / 2
        self.background_2.center_y = SCREEN_HEIGHT * 1.5
        self.background_2.change_y = -5 
        
        self.background_list.append(self.background_1)
        self.background_list.append(self.background_2)

        # Begin the game with 3 enemies.
        for i in range(0, 3):
            self.enemy_list.append(Enemy(random.randint(1, 4), (random.randint(0, SCREEN_WIDTH), 400)))


    def update(self, delta_time):
        """Updates the game as time passes."""

        # Only update if the game is not over.
        if (not self.game_over):

            # If the background reaches the end of its scroll, restart it back at the top.
            if (self.background_1.center_y == SCREEN_HEIGHT * -.5):
                self.background_1.center_y = SCREEN_HEIGHT * 1.5

            if (self.background_2.center_y == SCREEN_HEIGHT * -.5):
                self.background_2.center_y = SCREEN_HEIGHT * 1.5

            self.background_list.update() # Move the background.



            # If the number of enemies is less than or equal to 10, try chancing an enemy spawn.
            if (len(self.enemy_list) <= 10):
                if (random.randint(1, 1000) > 990 + len(self.enemy_list)): # The more enemies on the screen, the less likely a spawn.
                    self.enemy_list.append(Enemy(random.randint(1, 4), (random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT)))

            # Update both the enemies and player.
            self.enemy_list.update()
            self.player.update()

            # Go through each enemy, check for bullet collisions, and also see if that enemy's bullets hit the player.
            for e in self.enemy_list:
                # Check to see which of the player's bullets hit that enemy and deal damage appropriately.
                collided_bullets = e.collides_with_list(self.player.bullet_list)

                for b in collided_bullets:
                    e.hp -= b.damage
                    self.hit_list.append(arcade.Sprite("assets/bullets/green_hit.png", scale = 1, center_x = b.center_x, center_y = b.center_y)) # For every bullet, add a green hit marker.

                    # If the enemy dies, add the appropriate score and kill the enemy.
                    if (e.hp <= 0):
                        self.score += e.score
                        e.kill()
                        break
                    self.score += HIT_SCORE
                    b.kill() # Remove bullet so it does not continue dealing damage to the enemy.

                # Now check which of that enemy's bullets hit the player.
                collided_bullets = self.player.collides_with_list(e.bullet_list)

                for b in collided_bullets:
                    self.hit_list.append(arcade.Sprite("assets/bullets/red_hit.png", scale = 1, center_x = b.center_x, center_y = b.center_y)) # For every bullet, add a red hit marker.
                    self.player.hp -= b.damage
                    self.player.hp = max(self.player.hp, 0) # This is so that the HP label doesn't show an HP less than 0.

                    # If the enemy reaches 0 hp, end the game.
                    if (self.player.hp <= 0):
                        self.game_over = True
                        break

                    b.kill() # Remove the bullet so it does not continue dealing damage to the player.


    def on_draw(self):
        """Called when the window needs to be drawn."""
        arcade.start_render()

        # Draw the scrolling background.
        self.background_list.draw()         

        # Draw all the enemies and all of the bullets associated with that enemy.
        self.enemy_list.draw()
        for e in self.enemy_list:
            e.bullet_list.draw()

        # Draw the player and his bullets.
        self.player.draw()
        self.player.bullet_list.draw()

        # Write out the score and HP for the player.
        arcade.draw_text("Score: {}".format(int(self.score)), 10, SCREEN_HEIGHT - 40, open_color.white, 30)
        arcade.draw_text("HP: {}".format(self.player.hp), SCREEN_WIDTH - 150, 20, open_color.white, 30)
       
        # Draw all hit markers.
        self.hit_list.draw()

        # If enough time has passed since the last hit_list clear, clear the hit_list.
        if ((datetime.datetime.now() - self.last_clear_hit_list).total_seconds() * 1000 >= self.clear_hit_list_interval):
            self.hit_list = arcade.SpriteList()
            self.last_clear_hit_list = datetime.datetime.now()

        # If the game is over, draw the Game Over text.
        if (self.game_over):
            arcade.draw_text("GAME OVER!", SCREEN_WIDTH / 2 - 90, SCREEN_HEIGHT / 2 - 15, open_color.white, 30, bold = True)
            arcade.draw_text("Press R to restart.", SCREEN_WIDTH / 2 - 100, SCREEN_HEIGHT / 2 - 45, open_color.white, 24, bold = True)

    def on_mouse_motion(self, x, y, dx, dy):
        """Called to update our objects. Happens approximately 60 times per second."""
        # If the game is not over, move the player to where the mouse is.
        if (not self.game_over):
            self.player.move(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        """Called when the user pressed a mouse button."""
        # If the game is not over and the user pressed the left mouse button, toggle on the shooting.
        if (not self.game_over and button == arcade.MOUSE_BUTTON_LEFT):
            self.player.set_shooting(True)

    def on_mouse_release(self, x, y, button, modifiers):
        """Called when a user releases a mouse button."""
        # If the game is not over and the user pressed the left mouse button, toggle off the shooting.
        if (button == arcade.MOUSE_BUTTON_LEFT):
            self.player.set_shooting(False)

    def on_key_press(self, key, modifiers):
        if (self.game_over and key == arcade.key.R):
            self.setup()
            self.game_over = False
        

def main():
    window = Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
