# my_coupons_screen.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.carousel import Carousel
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.anchorlayout import AnchorLayout  # Importar AnchorLayout


class MyCouponsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Usar RelativeLayout para posicionar la flecha y mantener el margen
        layout = RelativeLayout()

        # Crear el contenedor del carrusel para agregar márgenes
        carousel_container = AnchorLayout(
            anchor_x='center',
            anchor_y='center',
            padding=[20, 0, 20, 0]  # Margen de 20 píxeles a la derecha e izquierda
        )

        # Crear el carrusel para las imágenes ganadas
        self.carousel = Carousel(direction='right', loop=True, size_hint=(1, 1))
        carousel_container.add_widget(self.carousel)

        # Crear el botón de la flecha
        self.back_button = Button(
            size_hint=(None, None),
            size=(100, 100),  # Tamaño del botón cuadrado
            background_normal='flecha.png',  # Ruta de la imagen de la flecha
            pos_hint={'x': 0, 'top': 1},  # Posición en la esquina superior izquierda
            padding=(20, 20)  # Margen interno derecho e izquierdo de 20 píxeles
        )
        self.back_button.bind(on_press=self.on_back_button_press)

        # Añadir el botón de la flecha y el carrusel al layout
        layout.add_widget(carousel_container)
        layout.add_widget(self.back_button)

        self.add_widget(layout)

    def update_coupons(self, won_images):
        # Limpiar el carrusel
        self.carousel.clear_widgets()
        
        # Verificar si hay imágenes ganadas antes de añadirlas al carrusel
        if not won_images:
            # Mostrar un mensaje de que no hay imágenes ganadas
            no_coupons_label = Label(text="No hay cupones ganados aún.", size_hint=(1, 1))
            self.carousel.add_widget(no_coupons_label)
            return
        
        # Añadir imágenes ganadas al carrusel
        for item in won_images:
            image_path = item['path']
            message = item['message']
            
            # Crear un layout para cada imagen y su mensaje
            image_layout = BoxLayout(orientation='vertical')
            image = Image(source=image_path)
            label = Label(text=message, size_hint=(1, 0.2))
            
            image_layout.add_widget(image)
            image_layout.add_widget(label)
            self.carousel.add_widget(image_layout)

    def on_back_button_press(self, instance):
        # Acción al presionar la flecha para volver al menú principal
        self.manager.current = 'main_menu'
