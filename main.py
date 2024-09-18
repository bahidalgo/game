# main.py
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager
from screens.main_menu_screen import MainMenuScreen
from screens.my_coupons_screen import MyCouponsScreen
from screens.game_screen import GameScreen  # Importar desde su nuevo módulo

class MyGameApp(App):
    def build(self):
        Window.size = (360, 640)
        self.screen_manager = ScreenManager()

        self.main_menu = MainMenuScreen(name='main_menu')
        self.game_screen = GameScreen(name='game')
        self.coupons_screen = MyCouponsScreen(name='my_coupons')

        self.screen_manager.add_widget(self.main_menu)
        self.screen_manager.add_widget(self.game_screen)
        self.screen_manager.add_widget(self.coupons_screen)

        return self.screen_manager

if __name__ == '__main__':
    MyGameApp().run()