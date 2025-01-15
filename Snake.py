import pygame, random, sys, time, logging, Logger
from collections import deque

WIDTH = 600
HEIGHT = 600
FPS = 20        # 帧率(决定蛇的速度)
block_size = 10 # 方块大小

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

convert_direction = {pygame.K_UP: 0, pygame.K_RIGHT: 1, pygame.K_DOWN: 2, pygame.K_LEFT: 3}
dx = [0, 10, 0, -10]
dy = [-10, 0, 10, 0]

def init_logger():
    level = logging.INFO
    filter = logging.Filter()
    filter.filter = lambda record: record.levelno == logging.INFO
    logger = Logger.get_logger(level,filter)
    return logger

logger = init_logger()


class Snake:
    def __init__(self):
        x, y = WIDTH//2, HEIGHT//2
        self.body = deque([[x-10,y], [x,y], [x+10,y]])        # 蛇身, 多设置一个虚蛇尾, 方便去尾
        self.blocks = {(x-10,y), (x,y), (x+10,y)}             # 蛇身的坐标集合
        self.head = self.body[-1]
        self.tail = self.body[0]
        self.direction = None               # 方向, 初始不动
        self.die = False                    # 是否死亡

    def is_in_snake(self,x,y):                                  # 某块是否在蛇身内
        return True if (x,y) in self.blocks else False

    def __is_valid__(self, x, y):
        if (x,y) in self.blocks or x<0 or x>=WIDTH or y<0 or y>=HEIGHT:
            return False
        return True

    # 改变方向
    def change_direction(self, direction):
        direction = convert_direction[direction]
        logger.info('direction: '+str(direction))
        if self.direction == None or ((self.direction+direction)&1):         # 两个方向互相垂直
            if direction == 3 and self.direction == None:                   # 初始方向为左, 则翻转蛇身
                self.direction = 3
                self.body.reverse()
                self.head, self.tail = self.tail, self.head
            self.direction = direction


    # 更新蛇身, 并检查是否死亡
    def update(self, food:'Food'):
        if self.direction == None:
            return
        head_x = self.head[0] + dx[self.direction]
        head_y = self.head[1] + dy[self.direction]

        if not self.__is_valid__(head_x, head_y):
            self.die = True
            return

        self.body.append([head_x, head_y])
        self.blocks.add((head_x, head_y))
        self.head = self.body[-1]

        if not food.is_eat(self):                     # 没有吃到食物
            self.body.popleft()
            self.blocks.remove(tuple(self.tail))
        else:
            food.generate_pos(self)
        self.tail = self.body[0]


    # 画蛇身(只需要画头和尾)
    def draw(self, screen):
        logger.info('head: '+str(self.head))
        logger.info('tail: '+str(self.tail))
        logger.info('direction: '+str(self.direction))
        print('\n')
        pygame.draw.rect(screen, WHITE, [self.tail[0], self.tail[1], block_size, block_size])   # 去尾
        pygame.draw.rect(screen, BLACK, [self.head[0], self.head[1], block_size, block_size])   # 画头


class Food:
    def __init__(self):
        self.food_x = self.food_y = -1

    def generate_pos(self,snake:'Snake'):                               # 生成食物
        while True:
            food_x = random.randrange(0, WIDTH, block_size)
            food_y = random.randrange(0, HEIGHT, block_size)
            if not snake.is_in_snake(food_x,food_y):
                break
        self.food_x, self.food_y = food_x, food_y

    def draw(self,screen):
        pygame.draw.rect(screen, RED, [self.food_x, self.food_y, block_size, block_size])

    def is_eat(self,snake:'Snake'):
        return True if [self.food_x,self.food_y]==snake.head else False

# 显示信息
def message(s, screen, x, y, size=40):
    textfont = pygame.font.SysFont('comicsansms', size)
    textImage = textfont.render(s, True, BLACK)
    screen.blit(textImage, (x, y))
    pygame.display.flip()

# 运行游戏
def play_game(screen):
    clock = pygame.time.Clock()
    screen.fill(WHITE)
    pygame.display.flip()

    snake = Snake()
    food = Food()
    snake.draw(screen)
    food.generate_pos(snake)
    food.draw(screen)
    pygame.display.flip()

    while not snake.die:
        first_time = True                           # 第一次按键, 避免连续按键致死
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key in convert_direction and first_time:
                    first_time = False
                    snake.change_direction(event.key)

        snake.update(food)

        snake.draw(screen)
        food.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    message('Game Over', screen, WIDTH / 2 - 100, HEIGHT / 2 - 60)
    message('Score: ' + str(len(snake.body)-3), screen, WIDTH / 2 - 80, HEIGHT / 2 - 5)
    message('Press Esc to Quit or Space to Play Again', screen, WIDTH / 2 - 170, HEIGHT / 2 + 50,20)
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                elif event.key == pygame.K_SPACE:
                    return

def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Snake')

    while True:
        play_game(screen)

if __name__ == '__main__':
    main()