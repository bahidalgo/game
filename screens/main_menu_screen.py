# main_menu_screen.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.app import App

from game.game_mechanics import shuffle_tiles  # Importar shuffle_tiles

class MainMenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Layout principal
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        # Crear un título
        title_label = Label(text='Jueguito para Guagua Clau', font_size='24sp', size_hint=(1, 0.2))
        layout.add_widget(title_label)

        # Botón de jugar
        play_button = Button(text='JUGAR', size_hint=(1, 0.2))
        play_button.bind(on_press=self.on_play_button_press)
        layout.add_widget(play_button)

        # Botón de mis cupones
        coupons_button = Button(text='MIS CUPONES', size_hint=(1, 0.2))
        coupons_button.bind(on_press=self.on_coupons_button_press)
        layout.add_widget(coupons_button)

        # Botón de salir
        exit_button = Button(text='SALIR', size_hint=(1, 0.2))
        exit_button.bind(on_press=self.on_exit_button_press)
        layout.add_widget(exit_button)

        self.add_widget(layout)

    def on_play_button_press(self, instance):
        game_screen = self.manager.get_screen('game')

        # Encontrar la primera imagen que no se ha ganado
        game_screen.current_image_index = 0  # Reiniciar al primer índice
        for i, image_info in enumerate(game_screen.image_list):
            if image_info not in game_screen.won_images:
                game_screen.current_image_index = i
                break

        # Verificar si se está en la imagen final
        if game_screen.image_list[game_screen.current_image_index]['path'] == 'imagen_final.png':
            # Mostrar la imagen final
            game_screen.show_final_message()
            self.manager.current = 'game'
        else:
            # Desordenar las piezas antes de comenzar el juego
            game_screen.load_and_display_image()  # Cargar y dividir la nueva imagen
            shuffle_tiles(game_screen)  # Cambiar el valor de swap_count según sea necesario
            # Navegar a la pantalla de juego
            self.manager.current = 'game'

    def on_exit_button_press(self, instance):
        # Acción al presionar el botón "SALIR"
        App.get_running_app().stop()  # Cerrar la aplicación

    def on_coupons_button_press(self, instance):
        # Actualizar la pantalla de cupones antes de mostrarla
        game_screen = self.manager.get_screen('game')
        self.manager.get_screen('my_coupons').update_coupons(game_screen.won_images)
        self.manager.current = 'my_coupons'  # Navegar a la pantalla "Mis Cupones"
