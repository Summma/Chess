import chess
import pygame
import sys

import Piece
import Engine
from Zobrist import Zobrist

board = chess.Board()  # fen="8/4pk2/8/1K6/8/8/8/8 b - - 0 1"
engine = Engine.Engine(board)
print(engine.zobrist.zobrist_hash)
zobrist = Zobrist()

zobrist.generate_numbers()
zobrist.init_hash(board)

WIDTH = 1200
HEIGHT = 800
DISPLAY = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)
FPS = 60
FONT_SIZE = 14

WHITE = (255, 255, 255)
GREY = (122, 122, 122)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
COLOR_ONE = (157, 217, 237)
COLOR_TWO = (230, 249, 255)

pieces = pygame.sprite.Group()


def draw_board():
    size = 54
    for i in range(8):
        for j in range(8):
            if (i + j) % 2 == 0:
                pygame.draw.rect(DISPLAY, COLOR_TWO, (50 + i * size, 50 + j * size, size, size))
            else:
                pygame.draw.rect(DISPLAY, COLOR_ONE, (50 + i * size, 50 + j * size, size, size))


# Look here if the game ever becomes too slow
def place_pieces():
    pieces.empty()
    fen = board.fen()
    count = 0
    pos = 0
    while fen[count] != " ":
        curr = fen[count]
        color = "l"
        if curr == '/':
            count += 1
            continue
        if curr.isdigit():
            pos += int(curr)
            count += 1
            continue
        if curr.islower():
            color = 'd'
        curr = curr.lower()

        img = f'Pieces/Chess_{curr}{color}t45.svg'
        pieces.add(Piece.Piece(img, 77 + pos % 8 * 54, 77 + pos // 8 * 54))

        count += 1
        pos += 1


# Coordinate to notation
# e.g. (54, 54) => b2 (Just an example, this may not be the correct conversion)
def c_to_n(x, y):
    n_to_a = {
        1: 'a',
        2: 'b',
        3: 'c',
        4: 'd',
        5: 'e',
        6: 'f',
        7: 'g',
        8: 'h'
    }

    if 50 <= x <= 482 and 50 <= y <= 482:
        return f'{n_to_a[(x+4)//54]}{(536-y)//54}'
    return 'i9'


def render_text(screen, strings, font, font_size, top_x, top_y, spacing=0):
    for i, text in enumerate(strings):
        line = font.render(text, True, BLACK)
        line_rect = line.get_rect()
        line_rect.x, line_rect.y = (top_x, top_y + (font_size + spacing) * i)

        screen.blit(line, line_rect)


def main():
    pygame.init()

    DISPLAY.fill(WHITE)

    font = pygame.font.Font('freesansbold.ttf', FONT_SIZE)

    clicked = False
    moved = Piece.Piece()
    spot = (0, 0)
    place_pieces()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                clicked = True

                pos = pygame.mouse.get_pos()
                clicked_piece = [s for s in pieces if s.rect.collidepoint(pos)]
                if len(clicked_piece) > 0:
                    spot = (clicked_piece[0].rect.x, clicked_piece[0].rect.y)
                    moved = clicked_piece[0]

            if event.type == pygame.MOUSEBUTTONUP:
                clicked = False
                pos = pygame.mouse.get_pos()

                # Used for mouse clicks outside board
                if c_to_n(*spot) == 'i9':
                    continue

                if c_to_n(*pos) == 'i9':
                    moved.rect.x = spot[0]
                    moved.rect.y = spot[1]
                    spot = (0, 0)
                    moved = Piece.Piece()

                if c_to_n(*spot) != c_to_n(*pos):
                    move = chess.Move.from_uci("".join([c_to_n(*spot), c_to_n(*pos)]))
                    move2 = chess.Move.from_uci("".join([c_to_n(*spot), c_to_n(*pos), 'q']))
                else:
                    move = chess.Move.from_uci('a8h5')
                    move2 = chess.Move.from_uci('a8h5q')

                if move in board.legal_moves or move2 in board.legal_moves:
                    moved.rect.x = (moved.rect.x + 27) // 54 * 54
                    moved.rect.y = (moved.rect.y + 27) // 54 * 54

                    if move2 in board.legal_moves:
                        engine.push(board, move2)
                    else:
                        engine.push(board, move)

                    # print(f"Table: {engine.table_score}")
                    # print(f"Real Table: {engine.init_table(board)}")
                    # print(f"Pieces: {engine.count_pieces(board)}")
                    # print(f"Total: {engine.evaluate(board)}\n\n")
                    # print(board.unicode())

                    place_pieces()
                else:
                    moved.rect.x = spot[0]
                    moved.rect.y = spot[1]
                    spot = (0, 0)
                    moved = Piece.Piece()

        DISPLAY.fill(GREY)

        draw_board()

        if clicked:
            moved.move_to(pygame.mouse.get_pos())

        render_text(DISPLAY, engine.get_diagnostics_as_list(), font, FONT_SIZE, WIDTH - 650, 77, 25)

        pieces.update()
        pieces.draw(DISPLAY)

        pygame.display.update()
        pygame.time.Clock().tick(FPS)

        # Bot Moves
        if board.turn == chess.BLACK:
            bot_move = engine.start(board)
            if bot_move is not None:
                engine.push(board, bot_move)
                place_pieces()


if __name__ == "__main__":
    main()
