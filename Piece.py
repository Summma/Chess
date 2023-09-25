import pygame


class Piece(pygame.sprite.Sprite):
    def __init__(self, image=None, x=0, y=0):
        pygame.sprite.Sprite.__init__(self)

        if image is None:
            image = 'Pieces/Chess_blt45.svg'
        self.image = pygame.image.load(image)
        self.name = image

        self.rect = self.image.get_rect(center=(x, y))

    def move_to(self, pos):
        self.rect.center = pos

    def __repr__(self):
        return f'{self.name}'
