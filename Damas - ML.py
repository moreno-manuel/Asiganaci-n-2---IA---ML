import pygame
import copy
import numpy as np
import random
import json
import os
import ast

#convierte las tuplas a claves de string para guardar en el archivo json
def convert_keys_to_strings(d):
    if isinstance(d, dict):
        return {str(k): convert_keys_to_strings(v) for k, v in d.items()}
    elif isinstance(d, list):
        return [convert_keys_to_strings(i) for i in d]
    else:
        return d

#convierte las claves de string a tuplas para cargar la q-table
def convert_keys_from_strings(d):
    if isinstance(d, dict):
        return {ast.literal_eval(k): convert_keys_from_strings(v) for k, v in d.items()}
    elif isinstance(d, list):
        return [convert_keys_from_strings(i) for i in d]
    else:
        return d

#guarda los datos de q-table en el archivo json
def save_qtable_to_file(qtable, filename):
    try:
        qtable_converted = convert_keys_to_strings(qtable)
        with open(filename, 'w') as file:
            json.dump(qtable_converted, file, indent=4)
    except Exception as e:
        print(f"Error al guardar la tabla Q: {e}")

#carga los datos del archivo json a la q-table
def load_qtable_from_file(filename):
    if not os.path.exists(filename):
        print("El archivo no existe.")
        return {}
    try:
        with open(filename, 'r') as file:
            qtable_loaded = json.load(file)
        qtable_converted = convert_keys_from_strings(qtable_loaded)
        return qtable_converted
    except Exception as e:
        print(f"Error al cargar la tabla Q: {e}")
        return {}

# evalua el estado del tablero
def evaluate_board(matrix):
    human_score = 0
    ai_score = 0
    for row in matrix:
        for cell in row:
            if cell == "H" or cell == "HH":
                human_score += 1
            elif cell == "IA":
                ai_score += 1
    return ai_score - human_score

# posibles movimientos de un jugador
def get_all_moves(matrix, player):
    moves = []
    for row in range(4):
        for col in range(4):
            if matrix[row][col] == player:
                possible_moves = get_possible_moves(matrix, row, col)
                for move in possible_moves:
                    moves.append((row, col, move[0], move[1]))
    return moves

# posibles movimientos de un jugador
def get_possible_moves(matrix, row, col):
    moves = []
    directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    for dr, dc in directions:
        new_row, new_col = row + dr, col + dc
        if 0 <= new_row < 4 and 0 <= new_col < 4 and matrix[new_row][new_col] == "N":
            moves.append((new_row, new_col))
        elif 0 <= new_row < 4 and 0 <= new_col < 4 and matrix[new_row][new_col] != matrix[row][col]:
            jump_row, jump_col = new_row + dr, new_col + dc
            if 0 <= jump_row < 4 and 0 <= jump_col < 4 and matrix[jump_row][jump_col] == "N":
                moves.append((jump_row, jump_col))
    return moves

# movimiento de fichas
def make_move(matrix, move):
    start_row, start_col, end_row, end_col = move
    matrix[end_row][end_col] = matrix[start_row][start_col]
    matrix[start_row][start_col] = "N"
    if abs(start_row - end_row) == 2:  # si come alguna ficha
        mid_row, mid_col = (start_row + end_row) // 2, (start_col + end_col) // 2
        matrix[mid_row][mid_col] = "N"
    if abs(start_row - end_row) == 3: #mueve tres espacios si es reina
        if((start_row == 0 and start_col == 0) or (start_row == 3 and start_col == 3)): #diagonal principal
            for position in range(1,3):
                    matrix[position][position] = "N"
    return matrix

# comprueba si el juego termino y determina el ganador
def game_over(matrix):
    if len(get_all_moves(matrix, "H")) == 0:
        if len(get_all_moves(matrix, "HH")) == 0:
            return "IA"
    if len(get_all_moves(matrix, "IA")) == 0:
        return "H"

#crea los botones
def createButton(frame,button,name):
    if button.collidepoint(pygame.mouse.get_pos()): # si el foco esta en el boton el color es azul
        pygame.draw.rect(frame,"blue",button,0)
    else:
        pygame.draw.rect(frame,"black",button,0)
    
    text = font.render(name,True,"white") 
    screen.blit(text,(button.x + (button.width - text.get_width())/2, #posicion del 
                      button.y + (button.height - text.get_height())/2)) # texto

# valida los movimientos
def move_validate(matrix,row_select,col_select, new_row , new_col):
    if matrix[new_row][new_col] == "N":
        if abs(row_select - new_row) == 1 and abs(col_select - new_col) == 1:#si recorre un espacio
            return True
        elif abs(row_select - new_row) == 2 and abs(col_select - new_col) == 2:#si recorre dos espacios
            mid_row, mid_col = (row_select + new_row) // 2, (col_select + new_col) // 2
            if( matrix[mid_row][mid_col] == "IA" or matrix[row_select][col_select] == "HH"):
                return True
        elif abs(row_select - new_row) == 3 and abs(col_select - new_col) == 3:#si recorre tres espacios <solo reinas> HH
            if(matrix[row_select][col_select] == "HH"):
                return True

# el juego comienza
def createMatrix():
    #tablero
    matrix = [
        ["IA", " ", "IA", " "],
        [" ", "N", " ", "N"],
        ["N", " ", "N", " "],
        [" ","H", " ", "H"]
    ]
    
    #tamaño de celdas del tablero
    cellSize = 400 // 4
    piece_select = None
    running = True
    playing = 0
    message = None
    while running:
        screen.fill("gray")
        #dibuja el tablero
        for row in range(4):
            for col in range(4):
                color = "black" if (row + col) % 2 == 0 else "white" 
                pygame.draw.rect(screen, color, (col * cellSize, row * cellSize, cellSize, cellSize))
    
                piece = matrix [row][col]
                #dibuja piezas del humano
                if piece == "IA":
                    pygame.draw.circle(screen, "red" ,(col * cellSize + cellSize // 2, row * cellSize + cellSize // 2), 
                                   cellSize // 2 - 5)
                
                #dibuja piezas de la ia
                elif piece == "H" or piece =="HH": 
                    pygame.draw.circle(screen, "white" ,(col * cellSize + cellSize // 2, row * cellSize + cellSize // 2), 
                                   cellSize // 2 - 5)
        # marca la pieza seleccionada con un circulo verde
        if piece_select: 
            row, col = piece_select
            pygame.draw.circle(screen, "green" ,(col * cellSize + cellSize // 2, row * cellSize + cellSize // 2), 
                                cellSize // 2 - 5,3)
        
        
        pygame.display.flip() #actualiza la pantalla
        #eventos discretos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                message = None
                player = None
            #captura la posicion de la ficha seleccionada
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = event.pos
                col = mouse_x // cellSize
                row = mouse_y // cellSize
                if (matrix[row][col] == "H" or matrix[row][col] == "HH") and not piece_select:
                    piece_select = (row, col)
                elif piece_select:
                    row_select, col_select = piece_select
                    #posibles movimientos Humano
                    if move_validate(matrix, row_select, col_select, row, col):
                        matrix = make_move(matrix, (row_select, col_select, row, col))
                        if(row == 0) and matrix[row][col] != "HH":
                            matrix[row][col] = "HH"
                        piece_select = None
                        
                        # Turno de la IA
                        matrix= q_learning_move(matrix)
                        
                        playing = playing + 2


        if playing == 64:
            message = "Empate"
            player = None
            running = False
            
        if game_over(matrix) == "IA":
            message = "Gana IA"
            player = "IA"
            running = False
        
        if game_over(matrix) == "H":
            message = "Gana Humano"
            player = "H"
            running = False
        
    return message,player

#mensaje final del juego
def dialog(message,player):
    screen.fill("white")
    label = font2.render(message, True, "black")
    if player == "H":
        screen.blit(label, (110, 140))
    elif player == "IA":
        screen.blit(label, (140, 140))
    else:
        screen.blit(label, (150, 140))


# Q-Learning movimiento para la IA
def q_learning_move(matrix):
    state = tuple(tuple(row) for row in matrix)
    actions = get_all_moves(matrix, "IA")
    if not actions:
        return matrix
    
    if state not in Q_table:
        Q_table[state] = {action: 0 for action in actions}
    
    if random.uniform(0, 1) < epsilon:
        action = random.choice(actions)
    else:
        action = max(Q_table[state], key=Q_table[state].get)
    
    next_matrix = make_move(copy.deepcopy(matrix), action)
    reward = evaluate_board(next_matrix) #recompensa
    
    next_state = tuple(tuple(row) for row in next_matrix)
    next_actions = get_all_moves(next_matrix, "IA")
    if next_state not in Q_table:
        Q_table[next_state] = {next_action: 0 for next_action in next_actions}
    
    max_next_action = max(Q_table[next_state], key=Q_table[next_state].get)
    
    #algoritmo Q-Learning
    Q_table[state][action] = Q_table[state][action] + alpha * (reward + gamma * Q_table[next_state][max_next_action]) - Q_table[state][action]
    
    return next_matrix



if __name__ == "__main__":
    #configuracion de interfaz
    pygame.init()
    screen = pygame.display.set_mode((400, 400))
    pygame.display.set_caption("Damas con Q-Learning")
    clock = pygame.time.Clock()
    
    #fuentes para label
    font = pygame.font.SysFont("arial", 20)
    font2 = pygame.font.SysFont("arial", 35)
    #rectangulos para botones
    init = pygame.Rect(50, 240, 100, 40)
    quit = pygame.Rect(250, 240, 100, 40)
    play = False
    running = True
    message = None
    
    # Q-Learning parametros
    alpha = 0.1 #tasa de aprendizaje
    gamma = 0.95 #descuento
    epsilon = 0.2 #permite la exploracion en el entrenamiento
    
    # Cargar la Q_table desde el archivo si no esta vacio
    if os.path.getsize('Q-table.json') != 0:
        Q_table = load_qtable_from_file('Q-table.json')
    else:
        Q_table = {}
    
    while running:
        
        #eventos discretos
        for event in pygame.event.get():
            #click en quit del frame
            if event.type == pygame.QUIT:
                running = False
            #click en salir
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if quit.collidepoint(pygame.mouse.get_pos()):
                    if not play:
                        running = False
                #click en iniciar
                if init.collidepoint(pygame.mouse.get_pos()):
                    play = True
        
        if message != None:
            dialog(message,player)
            quit = pygame.Rect(150, 240, 100, 40)
            createButton(screen, quit, "Salir")
            play = False
        #inicio del juego
        elif play:
            message , player = createMatrix()
            if message == None:
                running = False
        #menu 
        else:
            screen.fill("white")
            label = font2.render("Juego de Damas", True, "black")
            label2 = font.render("Humano VS IA (Q-Learning)", True, "black")
            screen.blit(label, (90, 72))
            screen.blit(label2, (100, 114))
            createButton(screen, init, "Iniciar")
            createButton(screen, quit, "Salir")
        pygame.display.flip()#atualiza pantalla
        clock.tick(60)#60 fps
    
    # Guarda la Q_table después de la partida
    save_qtable_to_file(Q_table, 'Q-table.json')
    pygame.quit()












