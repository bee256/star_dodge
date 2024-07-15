import csv
import pygame as pg
from os import path
from typing import List, Dict
from datetime import datetime, timedelta
from states.state import State
from utils.colors import LIGHT_BLUE, WHITE, BLACK
from utils.paths import dir_fonts
from utils.settings import Settings

screen: pg.Surface
settings: Settings


class HighscoreState(State):
    def __init__(self, menu_state: State):
        super().__init__()

        global screen, settings
        settings = Settings()
        screen = settings.screen

        self.highscores = load_highscores()
        self.menu_state = menu_state
        self.settings = Settings()
        self.screen = self.settings.screen
        self.header_font = pg.font.Font(path.join(dir_fonts, 'SpaceGrotesk-Bold.ttf'), self.settings.font_size_base)
        self.entry_font = pg.font.Font(path.join(dir_fonts, 'SpaceGrotesk-Regular.ttf'), int(self.settings.font_size_base * 0.8))
        self.overall_scores = filter_overall(self.highscores)
        self.today_scores = filter_today(self.highscores)
        self.last_hour_scores = filter_last_hour(self.highscores)

    def handle_events(self, events: List[pg.event.Event], frame_time):
        for event in events:
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                return self.menu_state

    def render(self):
        screen.blit(settings.background_img, (0, 0))
        self.render_table("Overall", self.overall_scores, 0, self.screen.get_width() // 2, self.screen.get_height(), max_entries=15)
        self.render_table("Today", self.today_scores, self.screen.get_width() // 2, self.screen.get_width() // 2,
                          self.screen.get_height() // 2, max_entries=6)
        self.render_table("Last Hour", self.last_hour_scores, self.screen.get_width() // 2, self.screen.get_width() // 2,
                          self.screen.get_height() // 2, y_offset=self.screen.get_height() // 2, max_entries=6)
        pg.display.flip()

    def render_table(self, title: str, scores: List[Dict], x: int, width: int, height: int, y_offset=0, max_entries=15):
        # Rahmen und Hintergrund
        table_rect = pg.Rect(x + 10, y_offset + 10, width - 20, height - 20)
        pg.draw.rect(self.screen, LIGHT_BLUE, table_rect, border_radius=5)
        inner_rect = pg.Rect(x + 15, y_offset + 15, width - 30, height - 30)
        pg.draw.rect(self.screen, BLACK, inner_rect, border_radius=5)
        header_text = self.header_font.render(title, True, LIGHT_BLUE)
        self.screen.blit(header_text, (x + width // 2 - header_text.get_width() // 2, y_offset + 30))
        columns = ["#", "Name", "Score", "Datum"]
        col_x = [x + width / 10, x + width / 6, x + width / 2 - 20, x + width - width / 3]
        for i, col in enumerate(columns):
            col_text = self.entry_font.render(col, True, LIGHT_BLUE)
            self.screen.blit(col_text, (col_x[i], y_offset + 90))

        y = y_offset + 140
        for idx, score_entry in enumerate(scores[:max_entries]):  # Begrenze auf die max_entries Einträge
            rank_text = self.entry_font.render(str(idx + 1), True, WHITE)
            name_text = self.entry_font.render(score_entry['name'], True, WHITE)
            score_text = self.entry_font.render(f"{score_entry['score']:.2f}", True, WHITE)
            date_text = self.entry_font.render(score_entry['date'].strftime('%Y-%m-%d '), True, WHITE)
            self.screen.blit(rank_text, (col_x[0], y))
            self.screen.blit(name_text, (col_x[1], y))
            self.screen.blit(score_text, (col_x[2], y))
            self.screen.blit(date_text, (col_x[3], y))
            y += 40

    def get_frame_rate(self) -> int:
        return 1


def load_highscores():
    highscores = []
    try:
        # TODO: create function to return a typical OS specific directory to read/write high score file
        with open('highscores.csv', mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) >= 3:  # Überprüfen, ob die Zeile mindestens drei Elemente hat
                    highscore = {'name': row[0], 'score': float(row[1]), 'date': datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S')}
                    highscores.append(highscore)
                else:
                    print(f"Ignoriere ungültige Zeile: {row}")  # Optional: Melden Sie ungültige Zeilen
    except FileNotFoundError:
        print("Keine Highscores gefunden.")
    except ValueError as e:
        print(f"Fehler beim Konvertieren eines Highscores: {e}")

    return highscores


def filter_overall(scores: List[Dict]) -> List[Dict]:
    return sorted(scores, key=lambda x: x["score"], reverse=True)


def filter_today(scores: List[Dict]) -> List[Dict]:
    today = datetime.now().date()
    return sorted(
        [score for score in scores if score["date"].date() == today],
        key=lambda x: x["score"],
        reverse=True
    )


def filter_last_hour(scores: List[Dict]) -> List[Dict]:
    one_hour_ago = datetime.now() - timedelta(hours=1)
    return sorted(
        [score for score in scores if score["date"] >= one_hour_ago],
        key=lambda x: x["score"],
        reverse=True
    )
