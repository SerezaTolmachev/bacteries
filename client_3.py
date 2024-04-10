import socket
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox
import pygame
import math
import sys
import time

name = ''
color = ''

root = tk.Tk()
root.title('login')
root.geometry('300x200')
style = ttk.Style()
print(style.theme_names())
style.theme_use('clam')
colors = ['Maroon', 'DarkRed', 'FireBrick', 'Red', 'Salmon', 'Tomato', 'Coral', 'OrangeRed', 'Chocolate', 'SandyBrown',
          'DarkOrange', 'Orange', 'DarkGoldenrod', 'Goldenrod', 'Gold', 'Olive', 'Yellow', 'YellowGreen', 'GreenYellow',
          'Chartreuse', 'LawnGreen', 'Green', 'Lime', 'LimeGreen', 'SpringGreen', 'MediumSpringGreen', 'Turquoise',
          'LightSeaGreen', 'MediumTurquoise', 'Teal', 'DarkCyan', 'Aqua', 'Cyan', 'DarkTurquoise', 'DeepSkyBlue',
          'DodgerBlue', 'RoyalBlue', 'Navy', 'DarkBlue', 'MediumBlue']


def f1(event):
    global color
    color = combo.get()
    style.configure('TCombobox', fieldbackground=color, background=color)

def login():
    global name
    name = entry.get()
    if name != '' and color != '':
        root.destroy()
        root.quit()
    else:
        tk.messagebox.showerror('Error', 'Вы не ввели имя иди цвет.')

label1 = tk.Label(text='Введите никнейм')
label1.pack()

entry = tk.Entry(width=25)
entry.pack()

label2 = tk.Label(text='Выберите цвет')
label2.pack()

combo = ttk.Combobox(values=colors)
combo.pack()

combo.bind("<<ComboboxSelected>>", f1)

button = tk.Button(text="Войти", command=login)
button.pack()


def players_filter(players):
    a = None
    b = None
    for i in range(len(players)):
        if players[i] == '<':
            a = i
        if players[i] == '>' and a is not None:
            b = i
            result = players[a + 1:b]
            #result = result.split()
            return result
    return ''

def draw_players(players):
    for i in range(len(players)):
        player = players[i].split()
        x = int(player[0])+CENTER[0]
        y = int(player[1])+CENTER[1]
        size = int(player[2])
        color = player[3]
        print(color)
        pygame.draw.circle(screen, color, (x, y), size)



root.mainloop()

WIDTH = 500
HEIGHT = 500

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

client_socket.connect(('localhost', 10000))
client_socket.send(f'color:<{name},{color}>'.encode())

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Бактерии')

font = pygame.font.Font(None, 20)
text = font.render(name, True, 'white')
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


    data = client_socket.recv(1024).decode()
    data = players_filter(data).split(',')



    #client_socket.send('test'.encode())

    screen.fill("white")
    pygame.draw.circle(screen, color, CENTER, radius)
    screen.blit(text, place)
    if data != ['']:
        radius = int(data[0])
        draw_players(data[1:])
    pygame.display.flip()
    pygame.display.update()

pygame.quit()
