import random
import pyglet
from pyglet.window import key, FPSDisplay
from pyglet.resource import image

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

pyglet.resource.path = ['../resources']
pyglet.resource.reindex()

head_image = image('head.png')
body_image = image('body.png')
food_image = image('food.png')
images = [head_image, body_image, food_image]

# Center anchor of images
for img in images:
    img.width, img.height = 20, 20
    img.anchor_x = img.width / 2
    img.anchor_y = img.width / 2

window = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT, caption="Snake")
pyglet.gl.glClearColor(0.129, 0.129, 0.129, 1)
object_batch = pyglet.graphics.Batch()
fps = FPSDisplay(window)


class Game:
    def __init__(self):
        self.game_running = True
        self.score = 0
        self.lb_score = pyglet.text.Label(
            text="Score: 0",
            font_name="Roboto",
            font_size=20,
            bold=True,
            color=(117, 117, 117, 255),
            x=WINDOW_WIDTH-25, y=WINDOW_HEIGHT-20,
            anchor_x="right", anchor_y="top",
            batch=object_batch)

        self.lb_outcome = pyglet.text.HTMLLabel(
            width=600,
            anchor_x="center", anchor_y="center",
            x=WINDOW_WIDTH//2, y=WINDOW_HEIGHT//2,
            multiline=True,
            batch=object_batch
        )
        self.lb_outcome.visible = False

        self.snake_head = SnakeHead(
            img=head_image,
            x=random.randint(0, WINDOW_WIDTH),
            y=random.randint(0, WINDOW_HEIGHT),
            batch=object_batch)

        self.food = Food(
            img=food_image,
            x=random.randint(0, WINDOW_WIDTH),
            y=random.randint(0, WINDOW_HEIGHT),
            batch=object_batch)

    def bump_score(self):
        """ Update score label """
        self.score += 1
        self.lb_score.text = "Score: " + str(self.score)

    def food_alive(self):
        """ Check if food is eaten by comparing the distance between them to
        the margin: 20 units. To improve performance, the square root function
        is avoid by square the the distance -> 20^2 = 400
        """
        distance = (self.snake_head.x - self.food.x) ** 2 + \
                   (self.snake_head.y - self.food.y) ** 2
        return distance > 400

    def game_end(self):
        print(SnakeBody.bodies)
        self.game_running = False
        self.lb_score.delete()
        self.snake_head.delete()
        for body in SnakeBody.bodies:
            body.delete()
        self.food.delete()

        self.lb_outcome.text = """\
            <center>
                <h1>You lose</h1><br>
                <h3>Score: {}</h3>
            </center>""".format(str(self.score))
        self.lb_outcome.font_name = "Roboto"
        self.lb_outcome.color = (255, 255, 255, 255)
        self.lb_outcome.visible = True


class SnakeHead(pyglet.sprite.Sprite):
    VELOCITY = 210

    def __init__(self, *args, **kwargs):
        super(SnakeHead, self).__init__(*args, **kwargs)
        self.direction = 'RIGHT'
        self.trail = []

    def update(self, dt):
        """ Move snake head base on current direction and append the new
        location for the bodies to follow. """
        if self.direction == 'FORWARD':
            self.y += int(SnakeHead.VELOCITY * dt)
            self.rotation = 0
        elif self.direction == 'BACKWARD':
            self.y -= int(SnakeHead.VELOCITY * dt)
            self.rotation = 180
        elif self.direction == 'RIGHT':
            self.x += int(SnakeHead.VELOCITY * dt)
            self.rotation = 90
        elif self.direction == 'LEFT':
            self.x -= int(SnakeHead.VELOCITY * dt)
            self.rotation = 270

        self.check_bounds()
        self.trail.append((self.x, self.y))

    def new_body(self):
        """ Initiate a new body """
        tail_offset = - (SnakeBody.num_of_bodies + 2)
        SnakeBody.bodies.append(
            SnakeBody(
                img=body_image,
                x=self.trail[tail_offset][0],
                y=self.trail[tail_offset][1],
                batch=object_batch
            )
        )

    def check_bounds(self):
        """ Check if the head is out of the window boundary, wrap it to the
        other side if needed.
        """
        if self.x > WINDOW_WIDTH:
            self.x = 0
        elif self.x < 0:
            self.x = WINDOW_WIDTH

        if self.y > WINDOW_HEIGHT:
            self.y = 0
        elif self.y < 0:
            self.y = WINDOW_HEIGHT


class SnakeBody(pyglet.sprite.Sprite):
    num_of_bodies = 0
    bodies = []

    def __init__(self, *args, **kwargs):
        super(SnakeBody, self).__init__(*args, **kwargs)
        SnakeBody.num_of_bodies += 1

    def update(self, dt, pos_x, pos_y):
        """ Move body to the next position in the trail of the head """
        self.x = pos_x
        self.y = pos_y


class Food(pyglet.sprite.Sprite):
    def __init__(self, *args, **kwargs):
        super(Food, self).__init__(*args, **kwargs)

    def eaten(self):
        """ Translate food to a new random location """
        self.x = random.randint(0, 800)
        self.y = random.randint(0, 600)


game = Game()


@window.event
def on_draw():
    window.clear()
    object_batch.draw()
    fps.draw()


@window.event
def on_key_press(symbol, modifier):
    if symbol == key.UP:
        game.snake_head.direction = 'FORWARD'
    elif symbol == key.DOWN:
        game.snake_head.direction = 'BACKWARD'
    elif symbol == key.RIGHT:
        game.snake_head.direction = 'RIGHT'
    elif symbol == key.LEFT:
        game.snake_head.direction = 'LEFT'

    elif symbol == key.SPACE:
        game.game_end()


def update(dt):
    if game.game_running:
        game.snake_head.update(dt)
        for index, snake_body in enumerate(SnakeBody.bodies):
            body_offset = - (index + 2)
            snake_body.update(
                dt,
                game.snake_head.trail[body_offset][0],
                game.snake_head.trail[body_offset][1]
            )

        if not game.food_alive():
            game.food.eaten()
            game.snake_head.new_body()
            game.bump_score()


if __name__ == "__main__":
    pyglet.clock.schedule_interval(update, 1/10)
    pyglet.app.run()
