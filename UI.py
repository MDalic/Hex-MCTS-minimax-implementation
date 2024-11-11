import pygame
import math
import time
import threading
from GameState import GameState
moveInProgress = False
playersMoveUI = 0
def mainLoop(gameState,player1,player2):
    pygame.init()
    global moveInProgress
    global playersMoveUI
    WIDTH, HEIGHT = 1280, 720

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("HexGame")

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)

    HEX_RADIUS = 20
    HEX_WIDTH = HEX_RADIUS * math.sqrt(3)
    HEX_HEIGHT = HEX_RADIUS * 2
    BOARD_SIZE = gameState.size
    font = pygame.font.Font(None, 45)
    players = [player1,player2]

    def renderText(text, font, color):
        return font.render(text, True, color)
    def drawHexagon(surface, color, center):
        x, y = center
        points = [
            (x + HEX_RADIUS * math.cos(math.radians(angle)), y + HEX_RADIUS * math.sin(math.radians(angle)))
            for angle in range(30, 390, 60)
        ]
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, BLACK, points, 2)

    def addPaddingToCoordsForLines(coords,directionX,directionY):
        coords = list(coords)
        coords[0] = coords[0]+(HEX_RADIUS*2+5)*directionX
        coords[1] = coords[1]+(HEX_RADIUS*2+5)*directionY
        coords = tuple(coords)
        return coords


    def hexToPixel(q, r):
        x = WIDTH // 2 + HEX_WIDTH * (q + r / 2)
        y = HEIGHT // 2 + HEX_HEIGHT * 0.75 * r
        return (int(x), int(y))

    def playerMove(player, gameState):
        global moveInProgress
        global playersMoveUI
        player.makeTurn(gameState)
        moveInProgress = False
        playersMoveUI = (playersMoveUI + 1) % 2

    def pointInHexagon(point, hexCenter):
        px, py = point
        hx, hy = hexCenter
        dx = abs(px - hx) / HEX_RADIUS
        dy = abs(py - hy) / (HEX_HEIGHT / 2)
        if dx > 1 or dy > 1:
            return False
        return dx + dy <= 1

    running = True
    gameInProgress = False
    gameOver = False
    boardNeedUpdate = True
    #scuffed win condition borders
    topLeft = hexToPixel(-(BOARD_SIZE // 2),-(BOARD_SIZE // 2))
    topLeft = addPaddingToCoordsForLines(topLeft,-1.5,-1)
    bottomLeft = hexToPixel(-(BOARD_SIZE // 2),BOARD_SIZE - (BOARD_SIZE // 2))
    bottomLeft = addPaddingToCoordsForLines(bottomLeft,-1,0.5)
    topRight= hexToPixel(BOARD_SIZE - (BOARD_SIZE // 2),-(BOARD_SIZE // 2))
    topRight = addPaddingToCoordsForLines(topRight,0.1,-1)
    bottomRight = hexToPixel(BOARD_SIZE - (BOARD_SIZE // 2),BOARD_SIZE - (BOARD_SIZE // 2))
    bottomRight = addPaddingToCoordsForLines(bottomRight,0.4,0.5)
    while running:
        #board redraw
        screen.fill(WHITE)
        if gameInProgress == False:
            textSurface = renderText("Press Anywhere to start",font,BLACK)
            screen.blit(textSurface, (900, 50))
        if gameOver == 1:
            textSurface = renderText("Player 1 has won",font,RED)
            screen.blit(textSurface, (975, 50))
        if gameOver == 2:
            textSurface = renderText("Player 2 has won",font,BLUE)
            screen.blit(textSurface, (975, 50))
        if gameOver:
            textSurface = renderText("Press R to restart game",font,BLACK)
            screen.blit(textSurface, (925, 100))

        x = 0
        y = 0
        pygame.draw.line(screen,BLUE,topLeft,bottomLeft,5)
        pygame.draw.line(screen,RED,topLeft,topRight,5)
        pygame.draw.line(screen,RED,bottomLeft,bottomRight,5)
        pygame.draw.line(screen,BLUE,topRight,bottomRight,5)
        for q in range(-(BOARD_SIZE // 2), BOARD_SIZE - (BOARD_SIZE // 2)):
            for r in range(-(BOARD_SIZE // 2), BOARD_SIZE - (BOARD_SIZE // 2)):
                hex_center = hexToPixel(q, r)
                if gameState.board[r+(BOARD_SIZE // 2)][q+(BOARD_SIZE // 2)] == 1:
                    color = RED 
                elif gameState.board[r+(BOARD_SIZE // 2)][q+ (BOARD_SIZE // 2)] == 2:
                    color = BLUE
                else:
                    color = WHITE
                drawHexagon(screen, color, hex_center)
                y=y+1
            x=x+1
        boardNeedUpdate = False
        pygame.display.flip()
        #event handlers
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if gameOver and event.key == pygame.K_r:
                    gameState = GameState(gameState.size)
                    moveInProgress = False
                    gameOver = False
                    playersMoveUI = 0
                    gameInProgress = False
            if event.type == pygame.QUIT:
                running = False
            #change this to button VVVVVV
            if event.type == pygame.MOUSEBUTTONDOWN:
                gameInProgress = True
            #player moves
            if gameOver==False and boardNeedUpdate==False and event.type == pygame.MOUSEBUTTONDOWN and players[playersMoveUI].human ==True:
                mouse_pos = pygame.mouse.get_pos()
                print(mouse_pos)
                for q in range(-(BOARD_SIZE//2), BOARD_SIZE-(BOARD_SIZE//2)):
                    for r in range(-(BOARD_SIZE//2), BOARD_SIZE-(BOARD_SIZE//2)):
                        hex_center = hexToPixel(q, r)
                        if pointInHexagon(mouse_pos, hex_center):
                            if players[playersMoveUI].makeTurnUI(gameState,(q,r)):
                                playersMoveUI = (playersMoveUI + 1) % 2
                                boardNeedUpdate = True
                                gameOver = gameState.isGameOver()
        #AI moves
        if moveInProgress == False and gameInProgress==True:
            moveInProgress = True
            gameOver = gameState.isGameOver()
            if gameOver == False:
                threading.Thread(target=playerMove,args=(players[playersMoveUI],gameState)).start()

    pygame.quit()
