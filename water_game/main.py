import pyxel
from scenes.title import TitleScene
from scenes.world_map import WorldMapScene
from scenes.collection import CollectionScene
from scenes.shop import ShopScene
from scenes.lab import LabScene
from scenes.results import ResultsScene
from scenes.ending import EndingScene, GameOverScene
from data.levels import SOURCE_ORDER


class Game:
    def __init__(self):
        pyxel.init(256, 256, title="Aqua Purifier - SDG6", fps=30)
        pyxel.mouse(False)  # hide system cursor, we draw our own
        self._init_sounds()

        self._new_game_state()
        self.scene_name = "title"
        self.scene = TitleScene()

        pyxel.run(self.update, self.draw)

    def _init_sounds(self):
        # 0: UI click
        pyxel.sounds[0].set(
            notes="c3",
            tones="p",
            volumes="3",
            effects="n",
            speed=8,
        )
        # 1: water bubble
        pyxel.sounds[1].set(
            notes="g2e2c2",
            tones="n",
            volumes="321",
            effects="vvv",
            speed=10,
        )
        # 2: success jingle
        pyxel.sounds[2].set(
            notes="c3e3g3c4",
            tones="ssss",
            volumes="4444",
            effects="nnnn",
            speed=8,
        )
        # 3: failure buzz
        pyxel.sounds[3].set(
            notes="c3a2f2c2",
            tones="ssss",
            volumes="4321",
            effects="nnnn",
            speed=10,
        )
        # 4: filter start
        pyxel.sounds[4].set(
            notes="c2e2g2c3e3",
            tones="ttttt",
            volumes="23432",
            effects="nnnnn",
            speed=6,
        )
        # 5: collect water
        pyxel.sounds[5].set(
            notes="e3g3",
            tones="pp",
            volumes="43",
            effects="nn",
            speed=6,
        )
        # 6-7: background music
        pyxel.sounds[6].set(
            notes="c2c2g2g2a2a2g2r",
            tones="ssssssss",
            volumes="33333333",
            effects="nnnnnnnn",
            speed=20,
        )
        pyxel.sounds[7].set(
            notes="f2f2e2e2d2d2c2r",
            tones="ssssssss",
            volumes="33333333",
            effects="nnnnnnnn",
            speed=20,
        )
        # 8: water drop collect (short plop)
        pyxel.sounds[8].set(
            notes="g3c4",
            tones="pn",
            volumes="42",
            effects="nn",
            speed=5,
        )
        # 9: hazard hit (low thud)
        pyxel.sounds[9].set(
            notes="c2a1",
            tones="nn",
            volumes="43",
            effects="ff",
            speed=6,
        )
        # 10: buy / purchase (coin clink)
        pyxel.sounds[10].set(
            notes="e4g4e4",
            tones="ppp",
            volumes="343",
            effects="nnn",
            speed=5,
        )
        # 11: can't afford (error buzz)
        pyxel.sounds[11].set(
            notes="c2c2",
            tones="nn",
            volumes="33",
            effects="ff",
            speed=8,
        )
        # 12: add filter to pipeline (slot in)
        pyxel.sounds[12].set(
            notes="c3e3",
            tones="tp",
            volumes="33",
            effects="nn",
            speed=5,
        )
        # 13: remove filter (slot out)
        pyxel.sounds[13].set(
            notes="e3c3",
            tones="pt",
            volumes="32",
            effects="nn",
            speed=5,
        )
        # 14: filtration running (bubbling loop-like)
        pyxel.sounds[14].set(
            notes="c2e2g2e2c2e2g2c3",
            tones="nnnnnnnn",
            volumes="23433432",
            effects="vvvvvvvv",
            speed=8,
        )
        # 15: filtration complete (ding!)
        pyxel.sounds[15].set(
            notes="e3g3c4e4",
            tones="ssss",
            volumes="4444",
            effects="nnnn",
            speed=6,
        )
        # 16: upgrade (power up)
        pyxel.sounds[16].set(
            notes="c3e3g3c4g4",
            tones="ttttt",
            volumes="23454",
            effects="nnnnn",
            speed=5,
        )
        # 17: contract accept (confirmation)
        pyxel.sounds[17].set(
            notes="g3c4e4",
            tones="ppp",
            volumes="444",
            effects="nnn",
            speed=6,
        )
        # 18: water collection done (victory splash)
        pyxel.sounds[18].set(
            notes="c3e3g3e3g3c4",
            tones="nnnnnn",
            volumes="345543",
            effects="vvvvvv",
            speed=6,
        )
        # 19: unlock source (grand reveal)
        pyxel.sounds[19].set(
            notes="c3c3g3g3c4c4",
            tones="ssssss",
            volumes="234554",
            effects="nnnnnn",
            speed=8,
        )
        # 20: button hover tick (subtle)
        pyxel.sounds[20].set(
            notes="e4",
            tones="p",
            volumes="1",
            effects="n",
            speed=4,
        )
        # 21: pipeline full (warning)
        pyxel.sounds[21].set(
            notes="a2a2",
            tones="pp",
            volumes="32",
            effects="nn",
            speed=6,
        )
        pyxel.musics[0].set([6, 7], [], [], [])

    def _new_game_state(self):
        self.game_state = {
            "coins": 5000,
            "reputation": 0,
            "total_liters": 0,
            "total_earned": 0,
            "jobs_done": 0,
            "unlocked": set(),
            "filter_uses": {},
            "current_source": None,
            "water_sample": None,
            "result_water": None,
            "stages": [],
            "pipeline": [],
            "active_contract": None,
            "saved_pipeline": [],
            "filter_upgrades": {},
            "equipped_pump": "bucket",
            "owned_pumps": {"bucket"},
            "owned_filters": set(),
            "sources_completed": set(),
        }

    def update(self):
        result = self.scene.handle_input()
        self.scene.update()
        if result:
            self._switch_scene(result)

        # check game over (broke with no filters owned to earn with).
        # Only checked on the world map hub so the player is never killed
        # mid-build in the lab/shop while actively spending to set up a run.
        if self.scene_name == "world_map":
            coins = self.game_state.get("coins", 0)
            owned = self.game_state.get("owned_filters", set())
            if coins <= 0 and len(owned) == 0:
                self._switch_scene("game_over")

        # check victory (all 5 sources completed with grade A or B)
        if self.scene_name == "world_map":
            completed = self.game_state.get("sources_completed", set())
            if len(completed) >= len(SOURCE_ORDER):
                self._switch_scene("ending")

    def draw(self):
        self.scene.draw()

    def _switch_scene(self, name):
        pyxel.play(3, 0)  # click sound
        self.scene_name = name

        if name == "title":
            self.scene = TitleScene()
            pyxel.playm(0, loop=True)
        elif name == "new_game":
            self._new_game_state()
            self.scene = TitleScene()
            self.scene_name = "title"
            pyxel.playm(0, loop=True)
        elif name == "world_map":
            self.scene = WorldMapScene(self.game_state)
        elif name == "shop":
            self.scene = ShopScene(self.game_state)
        elif name == "collection":
            self.scene = CollectionScene(self.game_state)
            pyxel.play(1, 1)
        elif name == "lab":
            self.scene = LabScene(self.game_state)
            pyxel.stop()
        elif name == "results":
            self.scene = ResultsScene(self.game_state)
            grade = self.game_state.get("result_water")
            if grade and grade.get_grade() in ("A", "B"):
                pyxel.play(2, 2)
            else:
                pyxel.play(2, 3)
        elif name == "ending":
            self.scene = EndingScene(self.game_state)
            pyxel.stop()
            pyxel.play(1, 2)  # victory jingle
        elif name == "game_over":
            self.scene = GameOverScene(self.game_state)
            pyxel.stop()
            pyxel.play(1, 3)  # failure sound


if __name__ == "__main__":
    Game()
