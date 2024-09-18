# game_mechanics.py
import random
from PIL import Image as PILImage
from widgets import MovableImage


def load_and_split_image(game_screen):
    # Reiniciar el estado del juego
    game_screen.game_over = False
    game_screen.grid_layout.clear_widgets()
    game_screen.tiles = []
    game_screen.initial_positions = {}

    # Ruta de la imagen que quieres dividir
    image_path = game_screen.image_list[game_screen.current_image_index]['path']
    game_screen.image = PILImage.open(image_path).convert('RGBA')

    # Dividir la imagen en 4x4
    for row in range(4):
        for col in range(4):
            # Cortar cada cuadro de la imagen
            box = (col * (game_screen.image.width // 4), row * (game_screen.image.height // 4),
                   (col + 1) * (game_screen.image.width // 4), (row + 1) * (game_screen.image.height // 4))
            cropped_image = game_screen.image.crop(box)

            # Convertir el recorte a textura para usarlo en Kivy
            texture = game_screen.pil_image_to_texture(cropped_image)
            image_widget = MovableImage(texture=texture, size_hint=(None, None), game_screen=game_screen)

            # Asignar posición a la baldosa
            image_widget.pos_index = (row, col)

            # Asignar un índice único que representa la posición correcta
            image_widget.correct_index = len(game_screen.tiles)

            # Guardar la posición inicial en el diccionario
            game_screen.initial_positions[image_widget.correct_index] = (row, col)

            # Añadir la imagen a la grilla
            game_screen.grid_layout.add_widget(image_widget)
            game_screen.tiles.append(image_widget)
    # Convertir la primera baldosa en la baldosa blanca antes de hacer el shuffle
    game_screen.make_first_tile_white()
    

def shuffle_tiles(game_screen, shuffle_count=5):
    previous_move = None  # Variable para almacenar el movimiento anterior

    for _ in range(shuffle_count):
        # Obtener las posiciones adyacentes a la baldosa blanca
        adjacent_positions = get_adjacent_positions(game_screen.white_tile_index)
        
        # Filtrar movimientos que sean opuestos al movimiento anterior
        possible_moves = [
            pos for pos in adjacent_positions
            if pos != previous_move  # Evitar repetir el movimiento anterior
        ]
        
        if not possible_moves:
            possible_moves = adjacent_positions  # Si no hay movimientos posibles, usar los originales

        # Seleccionar una posición aleatoria entre las posiciones adyacentes
        selected_pos = random.choice(possible_moves)

        # Obtener la baldosa que está en la posición seleccionada
        selected_tile = None
        for tile in game_screen.tiles:
            if tile.pos_index == selected_pos:
                selected_tile = tile
                break

        # Realizar el swap con la baldosa seleccionada
        if selected_tile:
            # Guardar el movimiento actual antes de hacerlo
            previous_move = game_screen.white_tile_index
            game_screen.swap_tiles(selected_tile)


def get_adjacent_positions(white_index):
    adjacent_positions = []
    row, col = white_index

    if row > 0:
        adjacent_positions.append((row - 1, col))
    if row < 3:
        adjacent_positions.append((row + 1, col))
    if col > 0:
        adjacent_positions.append((row, col - 1))
    if col < 3:
        adjacent_positions.append((row, col + 1))

    return adjacent_positions


def is_adjacent(pos1, pos2):
    row1, col1 = pos1
    row2, col2 = pos2

    if row1 == row2 and abs(col1 - col2) == 1:
        return True

    if col1 == col2 and abs(row1 - row2) == 1:
        return True

    return False
