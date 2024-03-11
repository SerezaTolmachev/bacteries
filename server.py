import socket
import pygame
import time
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker

engine = create_engine("postgresql+psycopg2://postgres:0610@localhost/postgres")

Base = declarative_base()

Base.metadata.create_all(engine)
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



class Player(Base):
    __tablename__ = "gamers"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(250))
    address = Column(String)
    x = Column(Integer, default=500)
    y = Column(Integer, default=500)
    size = Column(Integer, default=50)
    errors = Column(Integer, default=0)
    abs_speed = Column(Integer, default=1)
    speed_x = Column(Integer, default=0)
    speed_y = Column(Integer, default=0)
    color = Column(String(250))

    def __init__(self, name, address):
        self.name = name
        self.address = address


class LocalPlayer:
    def __init__(self, id, name, sock, addr):
        #self.color = color
        self.id = id
        self.db: Player = session.get(Player, self.id)
        self.sock = sock
        self.name = name
        self.address = addr
        self.x = 500
        self.y = 500
        self.size = 50
        self.errors = 0
        self.abs_speed = 1
        self.speed_x = 0
        self.speed_y = 0

    def update(self):
        self.x += self.speed_x
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


while run:
    clock.tick(220)
    try:
        player_socket, ip = main_socket.accept()
        player_socket.setblocking(False)
        player = Player('name', ip)
        session.merge(player)
        session.commit()
        ip = f'({ip[0]},{ip[1]})'
        data = session.query(Player).filter(Player.address == ip).all()
        for user in data:
            local_player = LocalPlayer(user.id, user.name, player_socket, ip)
            players[user.id] = local_player
    except BlockingIOError:
        pass

    for id in list(players):
        try:
            data = players[id].sock.recv(1024).decode()
            print(data)
            players[id].change_speed(data)
        except:
            pass

    for id in list(players):
        try:
            players[id].sock.send('test'.encode())

        except:
            players[id].sock.close()
            del players[id]

            session.query(Player).filter(Player.id == id).delete()
            session.commit()
            print('Cокет закрыт.')

    for event in pygame.event.get():
        if event == pygame.QUIT:
            print(1)
            run = False

    screen.fill('black')

    for id in list(players):
        player = players[id]
        x = player.x * WIDTH_SERVER // WIDTH_GAME
        y = player.y * HEIGHT_SERVER // HEIGHT_GAME
        size = player.size* WIDTH_SERVER // WIDTH_GAME
        pygame.draw.circle(screen, 'white', (x, y), size)

    for id in list(players):
        players[id].update()

    pygame.display.update()

pygame.quit()
main_socket.close()
session.query(Player).delete()
session.commit()
