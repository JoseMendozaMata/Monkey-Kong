"""
Instituto Tecnológico de Costa Rica
Ingeniería en Computadores

Creador: José Fabián Mendoza Mata

"""

from tkinter import *       # Tkinter para la ventana de configuracion
import pygame           # Pygame para la ventana de juego
from pygame.locals import *    
import random       # Para eventos aleatorios con los barriles
import time     # Para esperar a que cargue la pantalla despues de perder una vida
import os       # Para acceder a directorios
from tkinter import messagebox          # Cuadros dde advertencia e información

# Iniciar Pygame
pygame.init()

# Definir colores
MAGENTA = (255,0,255)
BLACK = (0,0,0)
WHITE = (255,255,255)

font = pygame.font.SysFont(None, 25)        # Cargar fuente (letras)
screen_text = font.render("Ganaste", True, WHITE)             # Mensaje para cuando el jugador gana un nivel

# Cargar las imagenes

playerImage = os.path.join("Imagenes","ninja_standing.png")
playerR1 = os.path.join("imagenes", "ninja_run_1.png")

obsImage = os.path.join("Imagenes","barrel.png")
ladImage = os.path.join("Imagenes", "lader.png")
platformImage = os.path.join("Imagenes", "platform.png")
baseImage = os.path.join("Imagenes", "base.png")
princessImage = os.path.join("Imagenes","princesa.png")
monkeyImage = os.path.join("Imagenes", "monkey 1.png")
background = os.path.join("Imagenes","fondo.png")

anim = [pygame.image.load(r"Imagenes/anim_1.png"),pygame.image.load(r"Imagenes/anim_2.png"),pygame.image.load(r"Imagenes/anim_3.png")]      # Imagenes del splash animado

icono = pygame.image.load(os.path.join("Imagenes", "icono.ico"))

FPS = 34

all_sprites = pygame.sprite.Group()

# Clase del personaje en el splash animado

class Mario(pygame.sprite.Sprite):

    def __init__(self,x,y):

        pygame.sprite.Sprite.__init__(self)
        
        self.image = anim[0]
        self.image.set_colorkey(WHITE)
        self.image = pygame.transform.scale(self.image,(60,75))
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (x,y)
        self.count = 0

    def draw(self):

        if 0 <= self.count < 10:
            self.image = anim[1]
            self.image = pygame.transform.scale(self.image,(60,75))
            self.image.set_colorkey(WHITE)
        elif 10 <= self.count < 20:
            self.image = anim[0]
            self.image = pygame.transform.scale(self.image,(60,75))
            self.image.set_colorkey(WHITE)
        elif 20 <= self.count < 30:
            self.image = anim[2]
            self.image = pygame.transform.scale(self.image,(60,75))
            self.image.set_colorkey(WHITE)
        else:
            self.count = 0

        self.rect = self.rect.move(3,0)
        self.count += 1

# Guias para poder actualizar o salir de la ventana de juego

class Gamewindow:

    def __init__(self):
        self.salir = False
        self.updatewindow = False

# Mono, el enemigo en el juego

class Monkey(pygame.sprite.Sprite):

    def __init__(self,x,y):

        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.image.load(monkeyImage)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (x,y)

# Princesa, objetivo final del juego

class Princess(pygame.sprite.Sprite):

    def __init__(self,x,y):

        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.image.load(princessImage)
        self.image.set_colorkey(MAGENTA)
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (x,y)

# Jugador, en este caso el personaje es un ninja, tiene todos sus movimientos, restricciones y aspecto definidos

class Player(pygame.sprite.Sprite):

    def __init__(self,x,y):
        
        pygame.sprite.Sprite.__init__(self)     # Iniciar clase padre de Sprite
        self.image = pygame.image.load(playerImage).convert()
        self.image = pygame.transform.flip(self.image, True, False)
        self.image.set_colorkey(WHITE)       # Para que no se vea el fondo
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.state = "waiting"
        self.gravity = True
        self.direction = "none"
        self.jumping = False
        self.midAir = False
        self.jumpCounter = 0
        self.collidelader = False
        self.collideplatform = False
        self.walkcount = 0
        self.points = 0
        self.arriveprinces  = 0
        self.leavegame = 0
        self.win = False

        try:
            self.dificult = int(getConfig()[0])
            self.lifes = int(getConfig()[1])
            self.sound = int(getConfig()[2])
        except:
            self.dificult = int(setDefault()[0])
            self.lifes = int(setDefault()[1])
            self.sound = int(setDefault()[2])
        
    def update(self):

        # Movimiento
        if self.state == "moving":
            if self.direction == "left" and self.rect.left >= 0:
                self.rect = self.rect.move(-3,0)

            if self.direction == "right" and self.rect.right <= 600:
                self.rect = self.rect.move(3,0)

            if self.direction == "up" and self.collidelader:            
                self.rect = self.rect.move(0,-1)
                self.gravity = False

            if self.direction == "down" and self.collidelader and not self.collideplatform:
                self.rect = self.rect.move(0, 1)
                self.gravity = False
                
        # Saltos y gravedad
        if self.jumping and not self.midAir:
            self.gravity = False
            if self.jumpCounter < 15:
                self.rect = self.rect.move(0,-2)
                self.jumpCounter += 1
            else:
                self.jumpCounter = 0
                self.jumping = False
                
                self.gravity = True 

        if self.collidelader:
            self.gravity = False

        if self.gravity:
            self.rect = self.rect.move(0,2)

        # Sprites

        if self.state == "standing":
            if self.direction == "right":
                self.image = pygame.image.load(playerImage).convert()
                self.image.set_colorkey(WHITE)
            elif self.direction == "left":
                self.image = pygame.image.load(playerImage).convert()
                self.image.set_colorkey(WHITE)
                self.image = pygame.transform.flip(self.image, True, False)
                

        else:
            if self.direction == "left":
                self.image = pygame.image.load(playerR1).convert()
                self.image.set_colorkey(WHITE)
                self.image = pygame.transform.scale(self.image, (15,25))
                self.image = pygame.transform.flip(self.image,True, False)

            if self.direction == "right":
                self.image = pygame.image.load(playerR1).convert()
                self.image.set_colorkey(WHITE)
                self.image = pygame.transform.scale(self.image, (15,25))
        

# Clase obstáculo, entorpecen el avance del jugador, si colisiona con el jugador la cantidad de vidas se disminuye y se refresca la pantalla de juego

class Obstacle(pygame.sprite.Sprite):

    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(obsImage).convert()
        self.image.set_colorkey(MAGENTA)
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.direction = "right"
        self.gravity = True
        self.activate = False
        self.aiming = "right"
        self.scored = False
        self.sensor = pygame.Rect(self.rect.topright[0],self.rect[1] - 25, 2, 35)   # Sensor para colision, pone puntos
                
    def update(self):
        
        # Movimiento
        if self.direction == "right":
            self.rect = self.rect.move(2,0)
            self.sensor = self.sensor.move(2,0)
        elif self.direction == "left":
            self.rect = self.rect.move(-2,0)
            self.sensor = self.sensor.move(-2,0)

        # Gravedad
        if self.gravity:
            self.rect = self.rect.move(0,2)
            self.sensor = self.sensor.move(0,2)

# Clase escalera, permite al jugador pasar de plataforma en plataforma

class Lader(pygame.sprite.Sprite):

    def __init__(self,x,y):

        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.image.load(ladImage).convert()
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.midtop = (x,y)

# Clase plataforma

class Platform(pygame.sprite.Sprite):

    def __init__(self,x,y):

        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.image.load(platformImage).convert()
        self.image.set_colorkey((255,255,255))
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.scored = False

# Placa base del juego

class Base(pygame.sprite.Sprite):

        def __init__(self):

            pygame.sprite.Sprite.__init__(self)

            self.image = pygame.image.load(baseImage).convert()
            self.image.set_colorkey((255,255,255))
            self.rect = self.image.get_rect()
            self.rect.topleft = (0,680)

# main, aqui se ejecuta todo lo relacionado al programa, la creacion de las clases y revisión de éstas, también revisa eventos de teclado.

def main():

    global all_sprites

    window = Gamewindow()
    pantalla = pygame.display.set_mode((600,700))
    pygame.display.set_icon(icono)
    pygame.display.set_caption('Ventana de Juego')
    fondo = pygame.image.load(background)
    fondo_rect = fondo.get_rect()     # Para saber donde poner el fondo
    jugador = Player(550,650)
    all_sprites.add(jugador)
    reloj = pygame.time.Clock()
    pantalla.fill((0,0,0))
    base = Base()
    all_sprites.add(base)
    
    if jugador.sound == 1:      # Si el jugador quiere sonido se ejecutará esta función
        Suene(True)

    while not window.salir:     # No se cierra la ventana

        obstaculos = []             # Formas de ordenar los datos del juego
        plataformas = []
        base = Base()
        escaleras = []
        puntos = 0
        plat_posy = 610
        plat_posx = 0
        guia_izq = True
        all_sprites.add(base)

        if jugador.dificult == 0:         # Sirve para conocer la dificultad en la que quiere jugar
            cant_plat = 3

        elif jugador.dificult == 1:
            cant_plat = 5

        else:
            cant_plat = 7
    
        for x in range(0,cant_plat):        # Para crear las plataformas, pueden crearse las que quiera
        
            if guia_izq == True:
                plat_posx = 220
            else:
                plat_posx = 380
        
            plataforma = Platform(plat_posx,plat_posy)  # Creación de las plataformas
            plataformas.append(plataforma)
            all_sprites.add(plataforma)

            plat_posy -= 70
            guia_izq = not guia_izq

        guia_izq = True         # Esto es para saber si las plataformas se ubicarán en la izq o der de la pantalla
        
        guia_izq = not True
        cont = 1
        
        for cont in range(len(plataformas)):    # Para crear las escaleras
                
            if not guia_izq:
                escalera = Lader(plataformas[cont].rect.topright[0] + 10,plataformas[cont].rect.topright[1])        # Guia para saber donde se posicionarán las ventanas
                escaleras.append(escalera)
                all_sprites.add(escalera)
                
            else:
                escalera = Lader(plataformas[cont].rect.topleft[0] - 10,plataformas[cont].rect.topleft[1])
                escaleras.append(escalera)
                all_sprites.add(escalera)
                
            guia_izq = not guia_izq
            
        if x % 2 == 0:      # Crea al mono (Monkey)
            mono =Monkey(plataformas[-1].rect.x,plataformas[-1].rect.y - 30)
        else:
            mono = Monkey(480, plataformas[-1].recty - 30)

        all_sprites.add(mono)       # Añador al grupo de sprite para que se dibuje
        plat_princesa = Platform(mono.rect.x + 50, mono.rect.y - 20)  # Plataforma de la princesa
        escalera = Lader(plat_princesa.rect.topright[0] - 15, plat_princesa.rect.topright[1])   # Escalera para llegar a la princesa
        escaleras.append(escalera)
        all_sprites.add(escaleras)                  # Importante para que se actualice el sprite
        all_sprites.add(plat_princesa)          # Importante para que se actualice el sprite

        plataformas.append(plat_princesa)           # Mete la plataforma de la princesa para que se comporte como las demás
        princesa = Princess(plat_princesa.rect.center[0], plat_princesa.rect.center[1])
        all_sprites.add(princesa)

        while not window.updatewindow:      # Si no se requiere reiniciar el nivel por vidas

            pantalla.blit(fondo, fondo_rect) # Para actualizar la ventana

            for plat in plataformas:        # Para dibujar las plataformas

                if jugador.rect.top < plat.rect.bottom and not plat.scored:     # Evento de puntos cuando sube plataforma
                    
                    jugador.points += 150
                    plat.scored = True

            if jugador.rect.collidelist(plataformas) == -1 and not jugador.rect.colliderect(base.rect):     # Si el jugador no colisiona con plataformas
                jugador.gravity = True
                jugador.collideplatform = False
                
            else:                               # Si el jugador colisiona con plataformas
                jugador.gravity = False
                jugador.midAir = False
                jugador.collideplatform = True

            if jugador.dificult == 0:        # Setear la probabilidad de que salgan barriles
                numRandom = random.randint(0,75)
            elif jugador.dificult == 1:
                numRandom = random.randint(0,50)
            else:
                numRandom = random.randint(0,25)
            
            if numRandom == 5:     # Evento random para spawnear obstaculos
                if x % 2 == 0:
                    
                    nuevo_obstaculo = Obstacle(mono.rect.topright[0], mono.rect.topright[1])
                    obstaculos.append(nuevo_obstaculo)
                    nuevo_obstaculo.direction = "right"
                    all_sprites.add(nuevo_obstaculo)
                    
                else:
                    nuevo_obstaculo = Obstacle(mono.rect.topleft[0], mono.rect.topleft[1])
                    obstaculos.append(nuevo_obstaculo)
                    nuevo_obstaculo.direction = "left"
                    all_sprites.add(nuevo_obstaculo)
                    
            jugador.collidelader = False
            for esc in escaleras:           # Detectar si el jugador está en una escalera o no
                if esc.rect.colliderect(jugador.rect):
                    jugador.collidelader = True
                    jugador.gravity = False
                    break

            if jugador.rect.colliderect(princesa.rect):
                if not jugador.win:
                    jugador.arriveprincess = time.time()
                    jugador.win = not jugador.win
                    
                pantalla.blit(screen_text, (450,40))
                
                if jugador.leavegame > 2:
                    Suene(0)
                    window.salir = True

            points = font.render("Vidas: " + str(jugador.lifes)+"      Puntos: " + str(jugador.points), True, WHITE)
            pantalla.blit(points, (50,40))
            
            if jugador.win:
                jugador.leavegame += 0.5
                
            for obs in obstaculos:
                
                if obs.rect.collidelist(plataformas) == -1:     # Si el obstaculo no colisiona con plataformas
                    obs.gravity = True
                else:
                    obs.gravity = False

                if obs.sensor.colliderect(jugador.rect) and not obs.scored:         # Cuando se suman puntos por saltar obstaculos
                    if obs.scored == False:    
                        jugador.points += 100
                        obs.scored = True

                if obs.rect.colliderect(base):            # Si colisiona con la base
                    obs.gravity = False

                if obs.rect.right >= 590:
                    obs.direction = "left"

                elif obs.rect.left <= 10:
                    obs.direction = "right"

                if obs.rect.colliderect(jugador.rect):       # Cuando colisiona con un rect pierde
                                            
                    jugador.lifes -= 1          # Para ir bajando las vidas que tiene el jugador
                    window.updatewindow = True          # Para que se limpie la pantalla
                
                    if jugador.lifes < 0 :
                        window.salir = True     # Cuando se le acaban las vidas
    
            for event in pygame.event.get():        # Recorre los eventos de pygame
                if event.type == pygame.QUIT:
                    window.salir = True
                    config_file = open("Archivos/configuracion.txt","w")        # Para limpiar el archivo de texto
                    config_file.close()
                    all_sprites.empty()     # Eliminar los sprites
                    config_file.close()
                    Suene(0)        
                    break
                
                if event.type == pygame.KEYDOWN:
                 
                    tecla = pygame.key.name(event.key)  # Determina la tecla presonada o soltada
                    
                    if tecla == "right":
                        jugador.direction = "right"
                        jugador.state = "moving"
                    elif tecla == "left":
                        jugador.direction = "left"
                        jugador.state = "moving"

                    elif tecla == "space" and not jugador.jumping and not jugador.midAir:
                        jugador.jumping = True
                        jugador.midAir = True

                    if jugador.collidelader and tecla == "up":
                        
                        jugador.direction = "up"
                        jugador.state = "moving"
                        jugador.gravity = False
            
                    elif jugador.collidelader and tecla == "down" and not jugador.collideplatform:
                     
                        jugador.direction = "down"
                        jugador.state = "moving"
                        jugador.gravity = False
                        
                if event.type == pygame.KEYUP:
                    tecla = pygame.key.name(event.key)  # Determina la tecla presonada o soltada
                    if tecla == "right" or tecla == "left" or tecla == "up" or tecla == "down":
                        jugador.state = "standing"
                        
            if window.salir == True:
                break

            all_sprites.update()
            all_sprites.draw(pantalla)
            pygame.display.flip()
            reloj.tick(FPS)

        if not window.salir:
            all_sprites.empty()     # Eliminar los sprites
            jugador.rect.center = (550,650) # Para devolver al rect a la posición del spawn
            all_sprites.add(jugador)
            base = Base()
            all_sprites.add(base)
                    
            time.sleep(2)
            window.updatewindow = False

    all_sprites.empty()     # Eliminar los sprites
    pygame.display.quit()
    main_window()

# Pantalla de Inicio, da las opciones de jugar o modificar la configuración del juego

def main_window():

    ventana = Tk()
    ventana.geometry("300x300")
    ventana.title("Proyecto Monkey Kong")
    ventana.iconbitmap(r"Imagenes/icono.ico")  #Icono de la ventana

    canvas = Canvas(ventana, width = 300, height = 300)
    canvas.place(x = 0, y = 0)

    imagen = PhotoImage(file = r"Imagenes/fondo_main.png")
    fondo = canvas.create_image(0,0, image = imagen, anchor = NW)
    
    configBut = Button(ventana, text = "Configuración", highlightcolor = "blue", bg = "black", fg = "white", command = lambda:pasar_ventanas(ventana,config_window))
    configBut.place(x = 200, y = 260)

    gameBut = Button(ventana, text = "Jugar", highlightcolor = "blue", bg = "black", fg = "white", command = lambda:pasar_ventanas(ventana,main))
    gameBut.place(x = 20, y = 260)

    ventana.mainloop()

# Ventana de configuración, permite cambiar los parámetros del juego

def config_window():

    ventana = Tk()
    ventana.geometry("300x300")
    ventana.title("Configuración")
    ventana.iconbitmap(r"Imagenes/icono.ico")  #Icono de la ventana

    canvas = Canvas(ventana, width = 300, height = 300)
    canvas.place(x = 0, y = 0)

    imagen = PhotoImage(file = r"Imagenes/config_bg.png")
    fondo = canvas.create_image(0,0, image = imagen, anchor = NW)

    fuente = ("Lucida Handwriting", 12)

    dif = IntVar()
    dif.set(0)

    vidas = IntVar()
    vidas.set(2)

    sonido = IntVar()
    sonido.set(1)

    labelSound = Label(ventana, text = "Sonido", font = fuente)
    labelSound.place(x = 10, y = 10)

    conSonido = Radiobutton(ventana, text = "Sí", font = fuente, variable = sonido, value = 1 )
    conSonido.place(x = 110, y = 10)
    conSonido.select()

    sinSonido = Radiobutton(ventana, text = "No", font = fuente, variable = sonido, value = 0)
    sinSonido.place(x = 110, y = 40)

    labelVidas = Label(ventana, text = "Vidas: ", font = fuente)
    labelVidas.place(x = 10, y = 100)

    vidasEntry = Entry(ventana, font = ("Tahoma", 12))
    vidasEntry.place(x = 110, y = 100)
    
    labelDificultad = Label(ventana, text = "Dificultad", font = fuente)
    labelDificultad.place(x = 10, y = 150)

    facil = Radiobutton(ventana, variable = dif, value = 0, font = ("Tahoma", 8), text = "Facil - 3 plataformas")
    facil.place(x = 120, y = 150)

    intermedio = Radiobutton(ventana, variable = dif,value = 1, font = ("Tahoma", 8), text = "Intermedio - 5 plataformas")
    intermedio.place(x = 120, y = 170)
    intermedio.select()

    dificil = Radiobutton(ventana, variable = dif, value = 2, font = ("Tahoma", 8), text = "Difícil - 7 plataformas")
    dificil.place(x = 120, y = 190)

    prinBut = Button(ventana, text  = "Volver al Menú Principal", bg = "black", fg = "white", command = lambda:saveConfig(ventana,main_window,dif.get(), vidasEntry.get(), sonido.get()))
    prinBut.place(x = 20, y = 260)

    ventana.mainloop()

# Guarda la configuración del juego en un archivo de texto
# E: ventana (para luego destruirla), destino (función destino), dificultad, vidas, sonido
# R: Vidas debe ser un entero mayor que 0, si no se ponen vidas se ponen en 3 por defecto

def saveConfig(ventana,destino,dificultad,vidas,sonido):

    config_file = open("Archivos/configuracion.txt","w")

    try:        # Verificar que digite un número

        if vidas == "" or int(vidas) >= 0:        # Por si no digita nada, las vidas por defecto son 3
            if vidas == "":
                vidas = 3
        
            config_file.write("[" + str(dificultad) + "," + str(vidas) + "," + str(sonido) + "]")
            config_file.close()
            pasar_ventanas(ventana,destino)
        else:
            messagebox.showerror("Error", "Cantidad de vidas debe ser mayor o igual que 0")
    except:
        messagebox.showerror("Error", "Digite una cantidad de vidas válida")

# Permite cargar la configuración del jugador, retorna la configuración en una lista

def getConfig():

    config_file= open("Archivos/configuracion.txt","r")         #Crea la variable del archivo de configuración y lo abre en modo lectura
    config=eval(config_file.readline())          #Lee la primer línea que contiene una lista con la configuracion
    config_file.close()
    return config

# Simplemente pasa de una ventana a otra, ejecuta la función por medio de la dirección de memoria

def pasar_ventanas(ventana, destino):

    ventana.destroy()
    destino()

# Configuración default del juego, esto si a la hora de entrar no se producen cambios en la configuracion del juego

def setDefault():

    return ["1","3","0"]

# Función que se ejecuta si el jugador quiere sonido

def Suene(opc):
    if opc:
        pygame.mixer.init()     # Inicia el reproductor
        pygame.mixer.music.load("Musica/musica_fondo.mid")      # Carga la cancion
        pygame.mixer.music.play(-1)         # La reproduce, el argumento -1 es para que sea un bucle infinito de la cancion
    else:
        pygame.mixer.quit()
    
pygame.mixer.init()         # Iniciar el mixer

# Pantalla de animación principal, es una pantalla de pygame con el persinaje de mario moviéndose por su mundo

def animacion():            # Pantalla de animación inicial

    ventana = pygame.display.set_mode((500,500))
    pygame.display.set_icon(icono)
    pygame.display.set_caption(r"Ventana Animación")
    salir = False
    fondo = pygame.image.load(os.path.join(r"Imagenes","fondo_anim.jpg")).convert()
    fondo = pygame.transform.scale(fondo, (500,500))
    fondo_rect = fondo.get_rect()     # Para saber donde poner el fondo
    nombre = pygame.image.load(os.path.join(r"Imagenes","nombre.png")).convert()
    nombre = pygame.transform.scale(nombre, (350,100))
    nombre.set_colorkey(WHITE)
    clock = pygame.time.Clock()
    mario = Mario(-50,440)
    inicia = time.time()    # Se usa para medir el tiempo que se muestra la animacion
    
    while not salir:        # Ciclo para mostrar la pantalla

        ventana.blit(fondo, fondo_rect)
        ventana.blit(mario.image, mario.rect.topright)
        ventana.blit(nombre, (80,40))
        
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                salir = True

        finaliza = time.time()      # Se usa para medir el tiempo que se muestra la animacion
        
        if finaliza - inicia >= 5.0:    #Condición para salir de la animación
            salir = True

        mario.draw()        # Dibujar a mario

        clock.tick(FPS)
        pygame.display.flip()

    pygame.display.quit()
    main_window()

animacion()
