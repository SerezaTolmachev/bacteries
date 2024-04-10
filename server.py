import random
import socket
import pygame
from russian_names import RussianNames
import math
import time
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker

engine = create_engine("postgresql+psycopg2://postgres:0610@localhost/postgres")

Base = declarative_base()

Session = sessionmaker(engine)
session = Session()

main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
main_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

main_socket.bind(('localhost', 10000))
main_socket.setblocking(False)
main_socket.listen(13)


pygame.init()

WIDTH_SERVER = 300
HEIGHT_SERVER = 300

WIDTH_GAME = 4000
HEIGHT_GAME = 4000

screen = pygame.display.set_mode((WIDTH_SERVER, HEIGHT_SERVER))
pygame.display.set_caption('Server')

clock = pygame.time.Clock()

players = {}

COLORS = ['Maroon', 'DarkRed', 'FireBrick', 'Red', 'Salmon', 'Tomato', 'Coral', 'OrangeRed', 'Chocolate', 'SandyBrown',
          'DarkOrange', 'Orange', 'DarkGoldenrod', 'Goldenrod', 'Gold', 'Olive', 'Yellow', 'YellowGreen', 'GreenYellow',
          'Chartreuse', 'LawnGreen', 'Green', 'Lime', 'Lime Green', 'SpringGreen', 'MediumSpringGreen', 'Turquoise',
          'LightSeaGreen', 'MediumTurquoise', 'Teal', 'DarkCyan', 'Aqua', 'Cyan', 'Dark Turquoise', 'DeepSkyBlue',
          'DodgerBlue', 'RoyalBlue', 'Navy', 'DarkBlue', 'MediumBlue']


class Player(Base):
    __tablename__ = "gamers"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(250))
    address = Column(String)
    x = Column(Integer, default=500)
    y = Column(Integer, default=500)
    size = Column(Integer, default=50)
    errors = Column(Integer, default=0)
    abs_speed = Column(Integer, default=3)
    speed_x = Column(Integer, default=0)
    speed_y = Column(Integer, default=0)
    color = Column(String(250))
    x_vision = Column(Integer, default=800)
    y_vision = Column(Integer, default=600)

    def __init__(self, name, address):
        self.name = name
        self.address = address

Base.metadata.create_all(engine)

class LocalPlayer:
    def __init__(self, id, name, sock, addr, color):
        self.color = color
        self.id = id
        self.db: Player = session.get(Player, self.id)
        self.sock = sock
        self.name = name
        self.address = addr
        self.x = 500
        self.y = 500
        self.size = 50
        self.errors = 0
        self.abs_speed = 4
        self.speed_x = 0
        self.speed_y = 0
        self.x_vision = 800
        self.y_vision = 600

    def update(self):
        if self.x - self.size < 0:
            if self.speed_x > 0:
                self.x += self.speed_x
        elif self.x + self.size >= WIDTH_GAME:
            if self.speed_x < 0:
                self.x += self.speed_x
        else:
            self.x += self.speed_x

        if self.y - self.size < 0:
            if self.speed_y > 0:
                self.y += self.speed_y
        elif self.y + self.size >= WIDTH_GAME:
            if self.speed_y < 0:
                self.y += self.speed_y
        else:
            self.y += self.speed_y

    def change_speed(self, vector):
        vector = vector_filter(vector)
        if vector[0] == 0.0 and vector[1] == 0.0:
            self.speed_x = 0
            self.speed_y = 0
            print(1)
        else:
            self.speed_x = vector[0] * self.abs_speed
            self.speed_y = vector[1] * self.abs_speed


    def sync(self):
        self.db.size = self.size
        self.db.abs_speed = self.abs_speed
        self.db.speed_x = self.speed_x
        self.db.speed_y = self.speed_y
        self.db.errors = self.errors
        self.db.x = self.x
        self.db.y = self.y
        self.db.color = self.color
        self.db.w_vision = self.x_vision
        self.db.h_vision = self.y_vision
        session.merge(self.db)
        session.commit()

    def load(self):
        self.size = self.db.size
        self.abs_speed = self.db.abs_speed
        self.speed_x = self.db.speed_x
        self.speed_y = self.db.speed_y
        self.errors = self.db.errors
        self.x = self.db.x
        self.y = self.db.y
        self.color = self.db.color
        self.x_vision = self.db.x_vision
        self.y_vision = self.db.y_vision
        return self

run = True


def vector_filter(vector):
    a = None
    b = None
    for i in range(len(vector)):
        if vector[i] == '<':
            a = i
        if vector[i] == '>' and a is not None:
            b = i
            result = vector[a + 1:b]
            result = result.split(',')
            result = float(result[0]), float(result[1])
            return result
    return ''


def color_filter(vector):
    a = None
    b = None
    for i in range(len(vector)):
        if vector[i] == '<':
            a = i
        if vector[i] == '>' and a is not None:
            b = i
            result = vector[a + 1:b]
            result = result.split(',')
            return result
    return ''


bots = 30
bot_name = RussianNames(count=bots*3, patronymic=False, surname=False, rare=True)
bot_name = list(set(bot_name))
print(bot_name)
for i in range(bots):
    bot = Player(bot_name[i], None)
    bot.color = random.choice(COLORS)
    bot.x = random.randint(0, WIDTH_GAME)
    bot.y = random.randint(0, HEIGHT_GAME)
    bot.speed_x = random.randint(-1 , 1)
    bot.speed_y = random.randint(-1 , 1)
    bot.size = random.randint(10, 100)
    session.add(bot)
    session.commit()
    local_bot = LocalPlayer(bot.id, bot.name, None, None, bot.color).load()
    players[bot.id] = local_bot

tick = -1

while run:
    clock.tick(60)
    tick += 1
    try:
        player_socket, ip = main_socket.accept()
        player_socket.setblocking(False)
        player = Player('name', ip)
        login = player_socket.recv(1024).decode()
        if login.startswith('color'):
            a = color_filter(login)
            print(a)
            player.name, player.color = a
        session.merge(player)
        session.commit()
        ip = f'({ip[0]},{ip[1]})'
        data = session.query(Player).filter(Player.address == ip).all()
        for user in data:
            local_player = LocalPlayer(user.id, user.name, player_socket, ip, user.color).load()
            players[user.id] = local_player
    except BlockingIOError:
        pass

    for id in list(players):
        if players[id].sock != None:
            try:
                data = players[id].sock.recv(1024).decode()
                print(data)
                players[id].change_speed(data)
            except:
                pass
        else:
            if tick % 300 == 0:
                vector = f"<{random.randint(-1, 1)},{random.randint(-1, 1)}>"
                players[id].change_speed(vector)


    visible_players = {}
    for id in list(players):
        visible_players[id] = []

    pairs = list(players.items())
    for i in range(len(pairs)):
        for j in range(i+1, len(pairs)):
            player1 = pairs[i][1]
            player2 = pairs[j][1]
            dist_x = round(abs(player2.x - player1.x))
            dist_y = round(abs(player2.y - player1.y))
            if dist_x <= player1.x_vision//2+player2.size and dist_y <= player1.y_vision//2+player2.size:
                data = f"{dist_x} {dist_y} {player2.size} {player2.color}"
                visible_players[player1.id].append(data)
                dist = math.sqrt(dist_x**2+dist_y**2)
                if dist < player1.size and player1.size > player2.size*1.1:
                    player2.size = 0
                    player2.speed_x = 0
                    player2.speed_y = 0
            if dist_x <= player2.x_vision//2+player1.size and dist_y <= player2.y_vision//2+player1.size:
                data = f"{-dist_x} {-dist_y} {player1.size} {player1.color}"
                visible_players[player2.id].append(data)
                dist = math.sqrt(dist_x ** 2 + dist_y ** 2)
                if dist < player2.size and player2.size > player1.size*1.1:
                    player1.size = 0
                    player1.speed_x = 0
                    player1.speed_y = 0
    for id in list(players):
        if players[id].sock != None:
            visible_players[id] = '<'+','.join(visible_players[id]) + '>'
            print(visible_players[id])

    for id in list(players):
        if players[id].sock != None:
            try:
                players[id].sock.send(visible_players[id].encode())

            except:
                players[id].sock.close()
                del players[id]

                session.query(Player).filter(Player.id == id).delete()
                session.commit()
                print('Cокет закрыт.')
    for id in list(players):
        if players[id].size == 0:
            if players[id].sock != None:
                players[id].sock.close()
            session.query(Player).filter(Player.id == id).delete()
            session.commit()
            del players[id]
            print('...')
    for event in pygame.event.get():
        if event == pygame.QUIT:
            print(1)
            run = False

    screen.fill('black')

    for id in list(players):
        player = players[id]
        x = player.x * WIDTH_SERVER // WIDTH_GAME
        y = player.y * HEIGHT_SERVER // HEIGHT_GAME
        size = player.size * WIDTH_SERVER // WIDTH_GAME
        pygame.draw.circle(screen, player.color, (x, y), size)

    for id in list(players):
        players[id].update()

    pygame.display.update()

pygame.quit()
main_socket.close()
session.query(Player).delete()
session.commit()
