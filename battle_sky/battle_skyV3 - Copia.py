import arcade
import random
import time
from arcade.gui import UIManager, UIFlatButton
import json
import os

WIDTH = 800
HEIGHT = 600
TITLE = "Battle Sky"

def load_player():
    if os.path.exists('top_player.json'):
        try:
            with open('top_player.json', 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {'id': '', 'punti': 0, 'tempo': 0, 'nemici': 0}
    else:
        return {'id': '', 'punti': 0, 'tempo': 0, 'nemici': 0}

def save_player(data):
    with open('top_player.json', 'w') as f:
        json.dump(data, f)

buff_speed = 10
bullet_speed = 4
Hp = 3
top_player = load_player()

def reset_stats():
    global tempo, punti, somma_nemici, Hp
    tempo = 0
    punti = 0
    somma_nemici = 0
    Hp = 3

class Menu(arcade.View):
    def __init__(self):
        super().__init__()

        self.setup()
        self.player_name = ""

        # TABELLA
        self.tabella_list = arcade.SpriteList()
        self.tabella = arcade.Sprite("tabella.png")
        self.tabella.center_x = 80
        self.tabella.center_y = 500
        self.tabella.scale = 0.30
        self.tabella_list.append(self.tabella)

        # LOGHI
        self.logo_list = arcade.SpriteList()
        self.logo = arcade.Sprite("aereo_1.png")
        self.logo.center_x = WIDTH - 500
        self.logo.center_y = HEIGHT//2 - 100
        self.logo.scale = 0.30

        self.logo2 = arcade.Sprite("aereo_2.png")
        self.logo2.center_x = WIDTH - 300
        self.logo2.center_y = HEIGHT//2 - 100
        self.logo2.scale = 0.30

        self.logo3 = arcade.Sprite("aereo_3.png")
        self.logo3.center_x = WIDTH - 400
        self.logo3.center_y = HEIGHT//2 - 200
        self.logo3.scale = 0.30

        self.logo_list.append(self.logo)
        self.logo_list.append(self.logo2)
        self.logo_list.append(self.logo3)

        # SFONDO
        self.schermata_menu_list = arcade.SpriteList()
        self.schermata_menu = arcade.Sprite("menu.jpg")
        self.schermata_menu.center_x = WIDTH//2
        self.schermata_menu.center_y = HEIGHT//2
        self.schermata_menu.width = WIDTH
        self.schermata_menu.height = HEIGHT
        self.schermata_menu_list.append(self.schermata_menu)

        # TESTI OTTIMIZZATI
        self.text_top_player = arcade.Text("TOP PLAYER", 50, 520, arcade.color.RED, 10)
        self.text_id = arcade.Text("", 20, 500, arcade.color.WHITE, 8)
        self.text_punti = arcade.Text("", 20, 480, arcade.color.WHITE, 8)
        self.text_tempo = arcade.Text("", 20, 460, arcade.color.WHITE, 8)
        self.text_nemici = arcade.Text("", 20, 440, arcade.color.WHITE, 8)

        self.text_title = arcade.Text("BATTLE SKY", WIDTH//2, HEIGHT//2+200,
                                      arcade.color.RED, 50, anchor_x="center")

        self.text_scegli = arcade.Text("SCEGLI IL TUO JET", WIDTH//2, HEIGHT//2+50,
                                       arcade.color.BLACK, 30, anchor_x="center")

        self.text_inserisci = arcade.Text("Inserisci il tuo Id:",
                                          WIDTH//2 - 50, HEIGHT//2 + 160,
                                          arcade.color.BLACK, 20, anchor_x="center")

        self.text_obbligatorio = arcade.Text("Obbligatorio inserire un iD",
                                             WIDTH//2 + 45, HEIGHT//2 + 120,
                                             arcade.color.RED, anchor_x="center")

        # TESTO DINAMICO DEL NOME
        self.text_player_name = arcade.Text(
            "",
            WIDTH//2 + 45,
            HEIGHT//2 + 120,
            arcade.color.YELLOW,
            20,
            anchor_x="center"
        )

    def setup(self):
        self.suono_menu = arcade.load_sound("sound_menu.mp3")
        self.suono_menu1 = self.suono_menu.play(loop=True)

    def on_draw(self):
        self.clear()
        self.schermata_menu_list.draw()
        self.logo_list.draw()
        self.tabella_list.draw()

        # aggiorna tabella
        self.text_id.text = f"ID: {top_player['id']}"
        self.text_punti.text = f"Punti: {top_player['punti']}"
        self.text_tempo.text = f"Tempo: {top_player['tempo']}"
        self.text_nemici.text = f"Nemici: {top_player['nemici']}"

        self.text_top_player.draw()
        self.text_id.draw()
        self.text_punti.draw()
        self.text_tempo.draw()
        self.text_nemici.draw()

        self.text_title.draw()
        self.text_scegli.draw()
        self.text_inserisci.draw()

        if self.player_name.strip() == "":
            self.text_obbligatorio.draw()

        self.text_player_name.text = self.player_name
        self.text_player_name.draw()

    def on_text(self, text):
        self.player_name += text

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.BACKSPACE:
            self.player_name = self.player_name[:-1]

    def on_mouse_press(self, x, y, button, modifiers):
        click = arcade.get_sprites_at_point((x, y), self.logo_list)
        if click:
            if self.player_name.strip() == "":
                return
            global name_player
            name_player = self.player_name
            logo_selezionato = click[0]
            game_view = game(logo_selezionato.texture)
            self.suono_menu1.delete()
            self.window.show_view(game_view)
class Buff(arcade.Sprite):
    def __init__(self, texture, tipo):
        super().__init__(texture)
        self.change_y = -buff_speed
        self.tipo = tipo

    def update(self, delta_time=1/60):
        self.center_y += self.change_y
        if self.bottom <= 0:
            self.remove_from_sprite_lists()


class bullet(arcade.Sprite):
    def __init__(self, texture):
        super().__init__(texture)
        self.change_y = bullet_speed

    def update(self, delta_time=1/60):
        self.center_y += self.change_y
        if self.top > HEIGHT:
            self.remove_from_sprite_lists()


class game(arcade.View):
    def __init__(self, logo_texture):
        super().__init__()

        reset_stats()

        self.enemies_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.hp_list = arcade.SpriteList()
        self.esplosioni_list = arcade.SpriteList()
        self.buff_list = arcade.SpriteList()

        self.buff_timer = 10
        self.moovment_speed = 5
        self.buff_active = None
        self.buff_durata = 0

        # SUONI PRECARICATI (FLUIDITÀ)
        self.sound_explosion = arcade.load_sound('sound_explosion.mp3')
        self.sound_bullet = arcade.load_sound('sound_bullet.mp3')
        self.sound_game = arcade.load_sound('sound_game.mp3').play(loop=True)

        # INVULNERABILITÀ
        self.invulnerabilita = False
        self.invulnerabilita_timer = 1
        self.invulnerabilita_god = False

        # SFONDO
        self.background_list = arcade.SpriteList()
        background = arcade.Sprite("background1.jpg")
        background.center_x = WIDTH//2
        background.center_y = HEIGHT//2
        background.width = WIDTH
        background.height = HEIGHT
        self.background_list.append(background)

        # VITE
        Hp0 = arcade.Sprite('Hp.png')
        Hp0.center_x = WIDTH//2
        Hp0.center_y = HEIGHT - 20
        Hp0.scale = 0.005

        Hp1 = arcade.Sprite('Hp.png')
        Hp1.center_x = WIDTH//2 + 20
        Hp1.center_y = HEIGHT - 20
        Hp1.scale = 0.005

        Hp2 = arcade.Sprite('Hp.png')
        Hp2.center_x = WIDTH//2 - 20
        Hp2.center_y = HEIGHT - 20
        Hp2.scale = 0.005

        self.hp_list.append(Hp0)
        self.hp_list.append(Hp1)
        self.hp_list.append(Hp2)

        # TESTI OTTIMIZZATI
        self.text_tempo = arcade.Text("Tempo: 0", 10, HEIGHT - 40, arcade.color.WHITE, 10)
        self.text_punti = arcade.Text("Punti: 0", 20, HEIGHT - 70, arcade.color.WHITE, 10)
        self.text_player_name = arcade.Text(f"Id: {name_player}", WIDTH - 100, HEIGHT - 20,
                                            arcade.color.WHITE, 10)

        # PERSONAGGIO
        self.player_list = arcade.SpriteList()
        self.logo_sprite = arcade.Sprite()
        self.logo_sprite.texture = logo_texture
        self.logo_sprite.center_x = WIDTH//2
        self.logo_sprite.center_y = HEIGHT//2
        self.logo_sprite.scale = 0.30
        self.player_list.append(self.logo_sprite)

    def spawn_enemy(self, texture, hp, points):
        enemy = arcade.Sprite(texture)
        enemy.scale = 0.30
        enemy.center_x = random.randint(0, WIDTH)
        enemy.center_y = HEIGHT + 50
        enemy.change_y = -5
        enemy.hp = hp
        enemy.points = points
        self.enemies_list.append(enemy)

    def spawn_buff(self):
        tipo = random.choice(['speed', 'double_shot', 'laser_blast', 'god'])
        buff_tipes = {
            "speed": ("buff_speed.png", 0.004),
            "god": ("buff_god_background.png", 0.003),
            "double_shot": ("double_bullet.png", 0.002),
            "laser_blast": ("change_bullet.png", 0.002)
        }

        texture, prob = buff_tipes[tipo]
        if random.random() < prob:
            buff = Buff(texture, tipo)
            buff.scale = 0.030
            buff.center_x = random.randint(0, WIDTH)
            buff.center_y = HEIGHT + 50
            buff.change_y = -5
            self.buff_list.append(buff)

    def reset_buff(self):
        self.moovment_speed = 5
        self.buff_active = None
        self.buff_durata = 0
        if self.invulnerabilita_god:
            self.invulnerabilita_god = False
            self.invulnerabilita = True
        else:
            self.invulnerabilita_timer = 1

    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP:
            self.logo_sprite.change_y = self.moovment_speed
        elif key == arcade.key.DOWN:
            self.logo_sprite.change_y = -self.moovment_speed
        elif key == arcade.key.LEFT:
            self.logo_sprite.change_x = -self.moovment_speed
        elif key == arcade.key.RIGHT:
            self.logo_sprite.change_x = self.moovment_speed
        elif key == arcade.key.SPACE:
            self.shooting = True
            self.sound_bullet.play()

            if self.buff_active == 'double_shot':
                for offset in (-10, 10):
                    b = bullet('Bullet.png')
                    b.scale = 0.010
                    b.center_x = self.logo_sprite.center_x + offset
                    b.bottom = self.logo_sprite.top
                    b.change_y = bullet_speed
                    self.bullet_list.append(b)

            elif self.buff_active in ('laser_blast', 'god'):
                laser = bullet('laser.png')
                laser.scale = 0.030
                laser.center_x = self.logo_sprite.center_x
                laser.bottom = self.logo_sprite.top
                laser.change_y = 10
                self.bullet_list.append(laser)

            else:
                b = bullet('Bullet.png')
                b.scale = 0.010
                b.center_x = self.logo_sprite.center_x
                b.bottom = self.logo_sprite.top
                b.change_y = bullet_speed
                self.bullet_list.append(b)

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.UP, arcade.key.DOWN):
            self.logo_sprite.change_y = 0
        elif key in (arcade.key.LEFT, arcade.key.RIGHT):
            self.logo_sprite.change_x = 0
        elif key == arcade.key.SPACE:
            self.shooting = False

    def on_update(self, delta_time):
        global tempo, punti, somma_nemici
        tempo += delta_time
        self.text_tempo.text = f"Tempo: {int(tempo)}"
        self.text_punti.text = f"Punti: {punti}"

        self.logo_sprite.update()
        self.bullet_list.update()
        self.enemies_list.update()
        self.buff_list.update()
        self.spawn_buff()
        self.esplosioni_list.update()

        # BORDI
        self.logo_sprite.left = max(self.logo_sprite.left, 0)
        self.logo_sprite.right = min(self.logo_sprite.right, WIDTH)
        self.logo_sprite.bottom = max(self.logo_sprite.bottom, 0)
        self.logo_sprite.top = min(self.logo_sprite.top, HEIGHT)

        # SPAWN NEMICI
        if random.random() < 0.0010:
            self.spawn_enemy("aereo_4.png", 1, 600)
        if random.random() < 0.0015:
            self.spawn_enemy("aereo_5.png", 3, 400)
        if random.random() < 0.0030:
            self.spawn_enemy("aereo_6.png", 2, 200)
        if random.random() < 0.0043:
            self.spawn_enemy("aereo_7.png", 1, 100)

        # INVULNERABILITÀ
        if self.invulnerabilita and not self.invulnerabilita_god:
            self.invulnerabilita_timer -= delta_time
            if self.invulnerabilita_timer <= 0:
                self.invulnerabilita = False

        # COLLISIONI PROIETTILI
        for b in self.bullet_list:
            hit = arcade.check_for_collision_with_list(b, self.enemies_list)
            if not hit:
                continue

            if self.buff_active in ('laser_blast', 'god'):
                damage = 3
            else:
                damage = 1

            for enemy in hit:
                enemy.hp -= damage
                if enemy.hp <= 0:
                    punti += enemy.points
                    somma_nemici += 1
                    enemy.remove_from_sprite_lists()

                    self.sound_explosion.play()
                    boom = arcade.Sprite('explosion.png')
                    boom.center_x = enemy.center_x
                    boom.center_y = enemy.center_y
                    boom.scale = 0.05
                    boom.timer = 0.3
                    self.esplosioni_list.append(boom)

            if self.buff_active not in ('laser_blast', 'god'):
                b.remove_from_sprite_lists()

        # TIMER ESPLOSIONI
        for boom in self.esplosioni_list:
            boom.timer -= delta_time
            if boom.timer <= 0:
                boom.remove_from_sprite_lists()

        # NEMICI USCITI
        for enemy in self.enemies_list:
            if enemy.bottom < 0:
                punti -= enemy.points
                enemy.remove_from_sprite_lists()

        # COLLISIONI FISICHE
        hit_enemy = arcade.check_for_collision_with_list(self.logo_sprite, self.enemies_list)
        hit_buff = arcade.check_for_collision_with_list(self.logo_sprite, self.buff_list)

        if hit_enemy and not self.invulnerabilita:
            global Hp
            Hp -= 1
            if self.hp_list:
                cuore = self.hp_list.pop()
                cuore.remove_from_sprite_lists()
                self.invulnerabilita = True
                self.invulnerabilita_timer = 1.0

            if Hp <= 0:
                self.window.show_view(GameOver())

        # RACCOLTA BUFF
        for t in hit_buff:
            if t.tipo == 'speed':
                self.reset_buff()
                self.buff_active = 'speed'
                self.moovment_speed = 10
                self.buff_durata = 15

            elif t.tipo == 'double_shot':
                self.reset_buff()
                self.buff_active = 'double_shot'
                self.buff_durata = 10

            elif t.tipo == 'laser_blast':
                self.reset_buff()
                self.buff_active = 'laser_blast'
                self.buff_durata = 8

            elif t.tipo == 'god':
                self.reset_buff()
                self.buff_active = 'god'
                self.invulnerabilita_god = True
                self.invulnerabilita = True
                self.moovment_speed = 10
                self.buff_durata = 8

            t.remove_from_sprite_lists()

        # TIMER BUFF
        if self.buff_active:
            self.buff_durata -= delta_time
            if self.buff_durata <= 0:
                self.reset_buff()

    def on_draw(self):
        self.clear()
        self.background_list.draw()
        self.player_list.draw()
        self.text_tempo.draw()
        self.text_punti.draw()
        self.text_player_name.draw()
        self.enemies_list.draw()
        self.bullet_list.draw()
        self.hp_list.draw()
        self.esplosioni_list.draw()
        self.buff_list.draw()
class GameOver(arcade.View):
    def __init__(self):
        super().__init__()

        self.game_over_list = arcade.SpriteList()
        self.game_over = arcade.Sprite('gameover.jpg')
        self.game_over.center_x = WIDTH//2
        self.game_over.center_y = HEIGHT//2
        self.game_over.width = WIDTH
        self.game_over.height = HEIGHT
        self.game_over_list.append(self.game_over)

        self.special_text = None

        if punti > top_player['punti']:
            top_player['id'] = name_player
            top_player['punti'] = punti
            top_player['nemici'] = somma_nemici
            top_player['tempo'] = int(tempo)
            save_player(top_player)

            self.special_text = arcade.Text(
                "CONGRATULAZIONI, SEI IL NUOVO KING DEGLI AEREI!",
                80, 500, arcade.color.AERO_BLUE, 20
            )

        self.summary_text=arcade.Text(
            f''' - RIEPILOGO PARTITA -\n
            
            \ntempo: {int(tempo)}
            \npunti: {punti} \n
            \nnemici sconfitti: {somma_nemici}''',
            self.center_x // 2 - 100,
            self.center_y // 2 - 100,
            arcade.color.RED,
            font_size= 14
        )
        
        self.ui = UIManager()
        self.ui.enable()

        self.button_home = UIFlatButton(
            text="Home",
            width=100,
            height=50,
            x=10,
            y=550
        )
        self.button_home.on_click = self.on_click_home
        self.ui.add(self.button_home)

        self.sound_voice = arcade.load_sound("sound_voice.mp3").play()
        self.sound_gameover = arcade.load_sound("sound_gameover.mp3").play(loop=True)

    def on_click_home(self, event):
        self.sound_voice.delete()
        self.sound_gameover.delete()
        self.window.show_view(Menu())

    def on_draw(self):
        self.clear()
        self.game_over_list.draw()
        if self.special_text:
            self.special_text.draw()
        self.summary_text.draw()
        self.ui.draw()


def main():
    window = arcade.Window(WIDTH, HEIGHT, TITLE)
    menu = Menu()
    window.show_view(menu)
    arcade.run()

main()