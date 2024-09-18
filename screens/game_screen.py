# game_screen.py
import os
import json
from PIL import Image as PILImage

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout  # Añadir esta línea
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics.texture import Texture
from kivy.uix.image import Image
from kivy.uix.relativelayout import RelativeLayout

from game.game_mechanics import shuffle_tiles, is_adjacent, load_and_split_image
from utils.file_utils import SAVE_FILE


class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Inicializar la lista de imágenes completa
        self.image_list = [
            {'path': 'perro.png', 'message': '¡Ganaste con el perro!'},
            {'path': 'img-2.png', 'message': '¡Ganaste con la segunda imagen!'},
            {'path': 'OIP.jpg', 'message': '¡Ganaste con la tercera imagen!'},
            {'path': 'imagen_final.png', 'message': '¡Felicidades! Has desbloqueado todos los cupones.'}  # Imagen final
        ]
        
        # Cargar el progreso guardado
        self.won_images = []
        self.tiles = []  # Inicializar self.tiles como una lista vacía
        self.load_game_progress()  # Cargar imágenes ganadas desde el archivo

        # Filtrar `image_list` para excluir las imágenes ganadas
        self.image_list = [img for img in self.image_list if img not in self.won_images]

        self.current_image_index = 0

        # Crear un FloatLayout para mayor control de posicionamiento
        self.main_layout = FloatLayout()
        self.add_widget(self.main_layout)

        # Crear el layout para la grilla de imágenes
        self.grid_layout = GridLayout(cols=4, rows=4, spacing=5, size_hint=(None, None))
        self.main_layout.add_widget(self.grid_layout)

        # Añadir el botón de retroceso
        self.back_button = Button(
            size_hint=(None, None),
            size=(50, 50),
            background_normal='flecha.png',
            pos_hint={'x': 0, 'top': 1}
        )
        self.back_button.bind(on_press=self.go_to_main_menu)
        self.main_layout.add_widget(self.back_button)

        # Ajustar el tamaño de la cuadrícula al cambiar el tamaño de la ventana
        Window.bind(on_resize=self.update_tile_sizes)

        # Cargar y dividir la imagen o mostrar la imagen final
        self.load_and_display_image()

        # Ajustar el tamaño de las baldosas
        Clock.schedule_once(self.adjust_initial_tile_sizes, 0)
    
    def go_to_main_menu(self, *args):
        # Cambiar la pantalla a 'main_menu'
        self.manager.current = 'main_menu'

    def load_and_display_image(self):
        # Verificar si la imagen actual es la imagen final
        if self.image_list[self.current_image_index]['path'] == 'imagen_final.png':
            # Mostrar la imagen final y el mensaje de felicitaciones
            self.show_final_message()
        else:
            # Reiniciar el estado del juego para cargar una nueva imagen
            self.reset_game_state()
            load_and_split_image(self)  # Cargar y dividir la imagen en la grilla

            # Ajustar las baldosas inmediatamente después de cargarlas
            Clock.schedule_once(lambda dt: self.update_tile_sizes(None, Window.width, Window.height), 0)

            # Convertir la primera baldosa en la baldosa blanca después de ajustar los tamaños
            Clock.schedule_once(lambda dt: self.make_first_tile_white(), 0)

    def show_final_message(self):
        # Limpiar la grilla y mostrar la imagen final
        self.grid_layout.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Crear un widget de imagen para mostrar la imagen final con transparencia
         # Crear un widget de imagen para mostrar la imagen final con tamaño aumentado
        image = Image(
            source='imagen_final.png',
            opacity=0.5,  # Agregar transparencia
            size_hint=(1, 2),  # Aumentar el tamaño de la imagen para ocupar más espacio
            allow_stretch=True,  # Permitir que la imagen se estire para llenar el espacio
            keep_ratio=True  # Mantener la relación de aspecto de la imagen
        )
        label = Label(text='¡Felicidades! Has desbloqueado todos los cupones.')
        btn_menu = Button(text='Volver al Menú', size_hint=(1, 0.2))

        layout.add_widget(image)
        layout.add_widget(label)
        layout.add_widget(btn_menu)

        # Añadir al layout principal
        self.main_layout.clear_widgets()
        self.main_layout.add_widget(layout)

        # Acción al presionar el botón "Volver al Menú"
        btn_menu.bind(on_release=self.go_to_main_menu)

    def go_to_main_menu(self, *args):
        # Cambiar la pantalla a 'main_menu'
        self.manager.current = 'main_menu'

    def load_game_progress(self):
        # Cargar el archivo de guardado si existe
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, 'r') as f:
                try:
                    saved_data = json.load(f)
                    # Marcar como ganadas las imágenes en saved_data
                    self.won_images = saved_data.get('won_images', [])
                except json.JSONDecodeError:
                    print("Error al leer el archivo de guardado.")
        else:
            # Si no existe el archivo, inicializar la lista de imágenes ganadas
            self.won_images = []

    def save_game_progress(self):
        # Guardar la lista de imágenes ganadas en el archivo
        with open(SAVE_FILE, 'w') as f:
            json.dump({'won_images': self.won_images}, f)
    
    def make_first_tile_white(self):
        # Asegurarse de que la primera baldosa sea blanca solo si no hay ninguna blanca
        if self.tiles and not any(hasattr(tile, 'is_white_tile') and tile.is_white_tile for tile in self.tiles):
            first_tile = self.tiles[0]

            # Crear una textura blanca con el tamaño de la baldosa
            white_texture = self.get_white_texture(first_tile.width, first_tile.height)

            # Cambiar la textura de la baldosa
            first_tile.texture = white_texture
            first_tile.is_white_tile = True  # Marcar esta baldosa como la baldosa blanca

            # Marcar la primera baldosa como la baldosa blanca
            self.first_tile_white = True
            self.white_tile_index = first_tile.pos_index
    
    def get_white_texture(self, width, height):
        # Crear y devolver una textura blanca con las dimensiones dadas
        white_image = PILImage.new('RGBA', (int(width), int(height)), color=(255, 255, 255, 255))
        return self.pil_image_to_texture(white_image)

    def return_to_menu(self, popup):
        # Cerrar el Popup y volver al menú principal
        popup.dismiss()
        self.manager.current = 'main_menu'

    def reset_game_state(self):
        # Resetear el estado del juego
        self.game_over = False
        self.grid_layout.clear_widgets()  # Limpiar la cuadrícula
        self.tiles = []  # Reiniciar la lista de baldosas
        self.initial_positions = {}
        self.first_tile_white = True
        self.white_tile_index = (0, 0)

    def show_victory_menu(self):
        self.game_over = True

        # Guardar la imagen actual en la lista de imágenes ganadas
        won_image = self.image_list[self.current_image_index]
        self.won_images.append(won_image)

        # No eliminar la imagen final
        if self.image_list[self.current_image_index]['path'] != 'imagen_final.png':
            del self.image_list[self.current_image_index]

        # Actualizar el archivo de guardado
        self.save_game_progress()

        # Crear un Popup para mostrar el menú de victoria si no es la imagen final
        if self.image_list[self.current_image_index]['path'] != 'imagen_final.png':
            layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
            label = Label(text='¡Felicidades,\nhas ganado!')
            btn_menu = Button(text='Volver al Menú', size_hint=(1, 0.2))
            btn_continue = Button(text='Continuar', size_hint=(1, 0.2))
            layout.add_widget(label)
            layout.add_widget(btn_menu)
            layout.add_widget(btn_continue)

            popup = Popup(title='Victoria', content=layout, size_hint=(0.5, 0.5))

            # Asignar acciones a los botones
            btn_menu.bind(on_release=lambda *args: self.return_to_menu(popup))
            btn_continue.bind(on_release=lambda *args: self.start_new_game(popup))

            popup.open()
        else:
            # Mostrar la imagen final directamente
            self.show_final_message()

    def start_new_game(self, popup):
        popup.dismiss()

        # Verificar si quedan imágenes disponibles
        if len(self.image_list) == 0:
            # Si no quedan imágenes, mostrar un mensaje indicando que se han desbloqueado todas
            self.show_final_message()
            return

        # Reiniciar el estado del juego
        self.reset_game_state()

        # Tomar la siguiente imagen (siempre la primera de la lista filtrada)
        self.current_image_index = 0
        for i, image_info in enumerate(self.image_list):
            if image_info not in self.won_images:
                self.current_image_index = i
                break

        # Cargar y dividir la nueva imagen
        self.load_and_display_image()

        # Desordenar las piezas
        shuffle_tiles(self)

        # Asegurarse de que se añaden los widgets a la cuadrícula
        self.grid_layout.clear_widgets()  # Asegurarse de limpiar la cuadrícula
        for tile in self.tiles:
            self.grid_layout.add_widget(tile)

        # Forzar la actualización de la pantalla
        self.manager.current = 'game'

    def reset_game_state(self):
        # Resetear el estado del juego
        self.game_over = False
        self.grid_layout.clear_widgets()  # Limpiar la cuadrícula
        self.tiles = []  # Reiniciar la lista de baldosas
        self.initial_positions = {}
        self.first_tile_white = True
        self.white_tile_index = (0, 0)

    def show_all_coupons_unlocked(self):
        # Crear un Popup que indique que todas las imágenes han sido desbloqueadas
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        label = Label(text='¡Felicidades! Has desbloqueado todos los cupones.')
        btn_menu = Button(text='Volver al Menú', size_hint=(1, 0.2))

        layout.add_widget(label)
        layout.add_widget(btn_menu)

        popup = Popup(title='Todos los Cupones Desbloqueados', content=layout, size_hint=(0.5, 0.5))

        # Accionar el botón de volver al menú
        btn_menu.bind(on_release=lambda *args: self.return_to_menu(popup))

        popup.open()

    def adjust_initial_tile_sizes(self, *args):
        # Actualizar el tamaño inicial de las baldosas
        self.update_tile_sizes(None, Window.width, Window.height)

    def update_tile_sizes(self, instance, width, height):
        # Calcular el tamaño óptimo de las baldosas basado en el tamaño de la ventana
        available_width = width - self.grid_layout.spacing[0] * 5
        available_height = height - self.grid_layout.spacing[1] * 5
        tile_size = min(available_width // 4, available_height // 4)

        # Ajustar el tamaño de cada baldosa
        for tile in self.tiles:
            tile.size = (tile_size, tile_size)

            # Si la baldosa es la baldosa blanca, actualizar su textura para el nuevo tamaño
            if hasattr(tile, 'is_white_tile') and tile.is_white_tile:
                tile.texture = self.get_white_texture(tile_size, tile_size)

        # Ajustar el tamaño del grid layout para contener todas las baldosas
        self.grid_layout.width = tile_size * 4 + self.grid_layout.spacing[0] * 3
        self.grid_layout.height = tile_size * 4 + self.grid_layout.spacing[1] * 3

        # Centrar horizontalmente la cuadrícula y dejar un margen superior
        self.grid_layout.pos_hint = {'center_x': 0.5, 'y': 0.2}  # 'y': 0.2 deja un margen superior del 20%

    def pil_image_to_texture(self, pil_image):
        pil_image = pil_image.transpose(PILImage.FLIP_TOP_BOTTOM)
        texture = Texture.create(size=pil_image.size, colorfmt='rgba')
        texture.blit_buffer(pil_image.tobytes(), colorfmt='rgba', bufferfmt='ubyte')
        return texture

    def check_victory(self):
        for tile in self.tiles:
            if tile.pos_index != self.initial_positions[tile.correct_index]:
                return False
        return True

    def swap_tiles(self, selected_tile):
        if self.game_over:
            return

        selected_index = selected_tile.pos_index
        white_index = self.white_tile_index

        if is_adjacent(selected_index, white_index):
            selected_linear_index = selected_index[0] * 4 + selected_index[1]
            white_linear_index = white_index[0] * 4 + white_index[1]

            print(f"Cambiando {selected_index} -> {white_index}")

            self.tiles[white_linear_index], self.tiles[selected_linear_index] = \
                self.tiles[selected_linear_index], self.tiles[white_linear_index]

            self.tiles[white_linear_index].pos_index = white_index
            self.tiles[selected_linear_index].pos_index = selected_index

            self.white_tile_index = selected_index
            self.grid_layout.clear_widgets()
            for tile in self.tiles:
                self.grid_layout.add_widget(tile)

            print(f"Posición actual de la baldosa blanca: {self.white_tile_index}")

            if self.check_victory():
                print("¡Victoria!")
                self.show_victory_menu()
        else:
            print("no se puede mover esta baldosa")
