import socket
import pygame
import math
import sys
import time


WIDTH = 500
HEIGHT = 500

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

client_socket.connect(('localhost', 10000))

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Бактерии')

font = pygame.font.Font(None, 20)
text = font.render("Player", True, 'white')
place = text.get_rect(center=(250, 250))




radius = 25
CENTER = WIDTH//2, HEIGHT//2

vector2 = 0, 0

run = True


while run:
    for event in pygame.event.get():
        if event == pygame.QUIT:
            run = False

    if pygame.mouse.get_focused():
        mouse_coord = pygame.mouse.get_pos()
        vector = mouse_coord[0]-CENTER[0], mouse_coord[1]-CENTER[1]
        vector_len = math.sqrt(vector[0] ** 2 + vector[1] ** 2)
        if vector_len != 0:
            vector = vector[0]/vector_len, vector[1]/vector_len
        if vector_len < radius:
            vector = 0, 0
        if vector2 != vector:
            vector2 = vector
            f_vector = f'<{vector[0]}, {vector[1]}>'
            client_socket.send(f_vector.encode())


    #data = client_socket.recv(1024).decode()
    #print(data)


    #client_socket.send('test'.encode())

    screen.fill("white")
    pygame.draw.circle(screen, 'black', CENTER, radius)
    screen.blit(text, place)
    pygame.display.flip()
    pygame.display.update()

pygame.quit()