import pygame
import math

pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("EID")
clock = pygame.time.Clock()
running = True

#jugador
img_jugador = pygame.image.load("assets/jugador.png").convert_alpha()
img_jugador = pygame.transform.scale(img_jugador, (40, 60))

jugador_x = 400
jugador_y = 400
jugador_rect = pygame.Rect(jugador_x, jugador_y, 40, 60)

aceleracion = 2
friccion = 0.8
vel_x = 0
vel_y = 0

#Ataques

#basico
balas = []
vel_bala = 10
cooldown_disparo = 0
espera_disparo = 15

#espadazo parabolico
espadazos = []
cooldown_parabolico = 0
espera_parabolica = 300

# sierra orbital
sierras = []  # Lista para guardar la sierra activa
cooldown_sierra = 0
espera_sierra = 600     # 10 segundos de cooldown (600 frames)
duracion_sierra = 300   # 5 segundos activa (300 frames)

fuente_hud = pygame.font.SysFont("Arial", 20, bold=True)

# Loop principal
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed() # para acortar codigo, es para checkear que una tecla esta presionada

    #Movimiento del jugador
    if keys[pygame.K_LEFT]:
        vel_x -= aceleracion
    if keys[pygame.K_RIGHT]:
        vel_x += aceleracion
    if keys[pygame.K_UP]:
        vel_y -= aceleracion
    if keys[pygame.K_DOWN]:
        vel_y += aceleracion

    vel_x *= friccion
    vel_y *= friccion

    if abs(vel_x) < 0.15: 
        vel_x = 0
    if abs(vel_y) < 0.15: 
        vel_y = 0
    
    jugador_rect.x += vel_x
    jugador_rect.y += vel_y
    
    #Disparo etc

    #Basico
    if cooldown_disparo > 0:
        cooldown_disparo -= 1

    teclas = pygame.key.get_pressed()
    mouse = pygame.mouse.get_pressed()

    if (teclas[pygame.K_z]) and cooldown_disparo == 0:
        nueva_bala = pygame.Rect(jugador_rect.centerx - 2, jugador_rect.top, 5, 10)
        
        balas.append(nueva_bala)
        
        cooldown_disparo = espera_disparo

    for bala in balas[:]:
        bala.y -= vel_bala  
    
        if bala.bottom < 0:
            balas.remove(bala)

    #Espadazo parabolico
    if cooldown_parabolico > 0:
        cooldown_parabolico -= 1
    if keys[pygame.K_c] and cooldown_parabolico == 0:
        # Parametros para la parabola x = a*(y - k)^2 + h
        # k es la altura donde estará el "doblez" de la curva (un poco más arriba de la nave)
        k_vertice = jugador_rect.centery - 75 
        h_vertice = jugador_rect.centerx - 150  # Qué tan a la izquierda llega el doblez
        a_param = 0.05  # Controla la apertura de la curva

        # Guardamos la bala con su estado inicial
        nueva_bala_p = {
            'rect': pygame.Rect(jugador_rect.centerx, jugador_rect.top, 12, 12),
            'k': k_vertice,
            'h': h_vertice,
            'a': a_param
        }
        espadazos.append(nueva_bala_p)
        cooldown_parabolico = espera_parabolica
        
    for b in espadazos[:]:
        # 1. La bala sube en Y
        b['rect'].y -= 5
            
        # 2. Calculamos X en base a Y usando la ecuación x = a*(y - k)^2 + h
        y_actual = b['rect'].y
        x_calculado = b['a'] * ((y_actual - b['k']) ** 2) + b['h']
            
        # 3. Asignamos la nueva X
        b['rect'].x = int(x_calculado)
            
        # Si sale de la pantalla por arriba o por la derecha, la borramos
        if b['rect'].bottom < 0 or b['rect'].left > 800:
            espadazos.remove(b)

    if cooldown_sierra > 0:
        cooldown_sierra -= 1
    # Activar sierra con la tecla x
    if keys[pygame.K_SPACE] and cooldown_sierra == 0 and len(sierras) == 0:
        sierra = {
            'rect': pygame.Rect(0, 0, 24, 24),  # Tamaño de la sierra
            'angulo': 0.0,                      # Ángulo inicial (theta)
            'radio_a': 100,                       # Ancho de la elipse
            'radio_b': 50,                       # Alto de la elipse
            'velocidad_giro': 0.2,              # Qué tan rápido rota
            'tiempo_vida': duracion_sierra       # Duración activa
        }
        sierras.append(sierra)
        cooldown_sierra = espera_sierra

    for s in sierras[:]:
        # 1. Aumentar el ángulo para que gire
        s['angulo'] += s['velocidad_giro']
        
        # 2. Calcular la posición (X, Y) con la fórmula de la elipse
        cx = jugador_rect.centerx + s['radio_a'] * math.cos(s['angulo'])
        cy = jugador_rect.centery + s['radio_b'] * math.sin(s['angulo'])
        
        # 3. Asignar el centro del Rect
        s['rect'].centerx = int(cx)
        s['rect'].centery = int(cy)
        
        # 4. Restar tiempo de vida y eliminar cuando se acabe
        s['tiempo_vida'] -= 1
        if s['tiempo_vida'] <= 0:
            sierras.remove(s)

    screen.fill((20,0,20))
    screen.blit(img_jugador, jugador_rect)

    # Convertir frames a segundos redondeados hacia arriba
    seg_parabolico = math.ceil(cooldown_parabolico / 60)
    seg_sierra = math.ceil(cooldown_sierra / 60)

    texto_basico = fuente_hud.render("Disparo Básico (Z): ∞", True, (255, 255, 0))  # Amarillo
    
    # Texto Espadazo (C)
    if seg_parabolico > 0:
        texto_z = fuente_hud.render(f"Espadazo (C): {seg_parabolico}s", True, (255, 80, 80))  # Rojo cuando recarga
    else:
        texto_z = fuente_hud.render("Espadazo (C): LISTO", True, (0, 255, 255))               # Cian cuando está listo

    # Texto Sierra (C)
    if seg_sierra > 0:
        texto_c = fuente_hud.render(f"Sierra (Espacio): {seg_sierra}s", True, (255, 80, 80))     # Rojo cuando recarga
    else:
        texto_c = fuente_hud.render("Sierra (Espacio): LISTO", True, (255, 0, 128))               # Fucsia cuando está listo

    # Dibujar los textos en la esquina superior izquierda
    screen.blit(texto_basico, (10, 10))
    screen.blit(texto_z, (10, 35))
    screen.blit(texto_c, (10, 60))

    for bala in balas:
        pygame.draw.rect(screen, (255, 255, 0), bala)  # Balas amarillas
    for b in espadazos:
        pygame.draw.rect(screen, (0, 255, 255), b['rect'])  # Balas cyan/azul claro
    for s in sierras:
        pygame.draw.rect(screen, (255, 0, 128), s['rect'])  # Cuadrado/Sierra fucsia brillante

    pygame.display.flip()
    clock.tick(60)
    
pygame.quit()