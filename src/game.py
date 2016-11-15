import random
import pyglet
from pyglet.window import key

pyglet.resource.path = ['../resources']
pyglet.resource.reindex()

window = pyglet.window.Window(800, 600)
pyglet.gl.glClearColor(0.129, 0.129, 0.129, 1)  # Primary text color

object_batch = pyglet.graphics.Batch()

head_image = pyglet.resource.image('head.png')
body_image = pyglet.resource.image('body.png')
food_image = pyglet.resource.image('food.png')

images = [head_image, body_image, food_image]

for image in images:
    image.width, image.height = 20, 20
    image.anchor_x = image.width / 2
    image.anchor_y = image.width / 2


class SnakeHead(pyglet.sprite.Sprite):
    MOVE_SPEED = 210
    score = 0

    def __init__(self, *args, **kwargs):
        super(SnakeHead, self).__init__(*args, **kwargs)
        self.direction = 'RIGHT'
        self.past_location = []

    def update(self, dt):
        if self.direction == 'FORWARD':
            self.y += int(SnakeHead.MOVE_SPEED * dt)
        elif self.direction == 'BACKWARD':
            self.y -= int(SnakeHead.MOVE_SPEED * dt)
        elif self.direction == 'RIGHT':
            self.x += int(SnakeHead.MOVE_SPEED * dt)
        elif self.direction == 'LEFT':
            self.x -= int(SnakeHead.MOVE_SPEED * dt)

        self.past_location.append((self.x, self.y))


class SnakeBody(pyglet.sprite.Sprite):
    id = 0

    def __init__(self, *args, **kwargs):
        super(SnakeBody, self).__init__(*args, **kwargs)
        self.id = SnakeBody.id + 1

    def update(self, dt, pos_x, pos_y):
        self.x, self.y = pos_x, pos_y


class Food(pyglet.sprite.Sprite):
    def __init__(self, *args, **kwargs):
        super(Food, self).__init__(*args, **kwargs)

    def eaten(self):
        self.x = random.randint(0, 800)
        self.y = random.randint(0, 600)

lb_score = pyglet.text.Label(text="Score: 0", x=10, y=10, batch=object_batch)
snake_head = SnakeHead(img=head_image,
                       x=random.randint(0, window.width),
                       y=random.randint(0, window.height),
                       batch=object_batch)
food = Food(img=food_image, x=random.randint(0, 800),
            y=random.randint(0, 600), batch=object_batch)

snake_bodies = []


def collision(obj1_x, obj1_y, obj2_x, obj2_y, margin):
    distance = (obj2_x - obj1_x) ** 2 + (obj2_y - obj1_y) ** 2
    return distance < margin ** 2


@window.event
def on_draw():
    window.clear()
    object_batch.draw()


@window.event
def on_key_press(symbol, modifier):
    if symbol == key.UP:
        snake_head.direction = 'FORWARD'
    elif symbol == key.DOWN:
        snake_head.direction = 'BACKWARD'
    elif symbol == key.RIGHT:
        snake_head.direction = 'RIGHT'
    elif symbol == key.LEFT:
        snake_head.direction = 'LEFT'

    # Debug keys
    elif symbol == key.SPACE:
        snake_bodies.append(
            SnakeBody(img=body_image,
                      x=snake_head.past_location[-SnakeBody.id-2][0],
                      y=snake_head.past_location[-SnakeBody.id-2][1],
                      batch=object_batch
                      )
        )
    elif symbol == key.C:
        food.eaten()


def update(dt):
    snake_head.update(dt)
    for index, body in enumerate(snake_bodies):
        body.update(dt,
                    snake_head.past_location[-index-2][0],
                    snake_head.past_location[-index-2][1])

    if collision(snake_head.x, snake_head.y, food.x, food.y, 20):
        food.eaten()
        snake_bodies.append(
            SnakeBody(img=body_image,
                      x=snake_head.past_location[-SnakeBody.id-2][0],
                      y=snake_head.past_location[-SnakeBody.id-2][1],
                      batch=object_batch
                      )
        )
        snake_head.score += 1
        lb_score.text = "Score: " + str(snake_head.score)


if __name__ == "__main__":
    pyglet.clock.schedule_interval(update, 1/10)
    pyglet.app.run()
