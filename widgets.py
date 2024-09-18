# widgets.py
from kivy.uix.image import Image

class MovableImage(Image):
    def __init__(self, **kwargs):
        self.game_screen = kwargs.pop('game_screen')
        super().__init__(**kwargs)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.game_screen.swap_tiles(self)
            return True
        return super().on_touch_down(touch)
