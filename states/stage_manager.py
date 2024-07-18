TIME_ADD_STARS_INCREMENT_TIMER_DECREASE = 1.0

# StageManager handles the creation of stars via different stages.
# The time we create stars is defined by the Stage class and reduced over time.
# Every TIME_ADD_STARS_INCREMENT_TIMER_DECREASE seconds we decrease the time in a stage when new stars are create
# next time, so over time, we will have more an more stars on screen and the game will get more difficult.
# During a stage, we reduce the time we create stars over the duration of state. The decrease time is
# calculated during init of the Stage objects: (new_stars_every_sec_begin - self.new_stars_every_sec_end) / duration_secs

class StageManager:
    def __init__(self):
        self.stages = []
        self.stages.append(Stage(0, 5, 1000, 750))
        self.stages.append(Stage(1, 10, 750, 500))
        self.stages.append(Stage(2, 15, 500, 400))
        self.stages.append(Stage(3, 20, 400, 300))
        self.stages.append(Stage(4, 20, 300, 200))
        self.stages.append(Stage(5, 25, 200, 150))
        self.stages.append(Stage(6, 30, 150, 125))

        # now we have all stages, we calculate the start time in game elapsed time which is the durations summed up
        stage_start_elapsed_time = 0
        for stage in self.stages:
            stage_start_elapsed_time += stage.duration_secs
            stage.stage_start_elapsed_time = stage_start_elapsed_time

        self.last_time_stars_created = 0
        self.last_time_star_create_time_decrease = 0
        self.current_stage = 0
        self.final_stage_final_create_duration = False

    def stars_to_be_created(self, elapsed_time) -> bool:
        stage = self.stages[self.current_stage]
        if elapsed_time - self.last_time_stars_created >= stage.current_create_duration:
            # keep when we created starts last time
            self.last_time_stars_created = elapsed_time
            return True
        return False

    def handle_stages(self, elapsed_time) -> bool:
        if self.final_stage_final_create_duration:
            return False

        stage = self.stages[self.current_stage]
        if elapsed_time >= stage.stage_start_elapsed_time:
            if self.current_stage < len(self.stages) - 1:
                self.current_stage += 1
                return True

        if elapsed_time - self.last_time_star_create_time_decrease < TIME_ADD_STARS_INCREMENT_TIMER_DECREASE:
            return False

        stage.current_create_duration -= stage.decrease_per_second
        # keep time when we have last reduced the star create time
        self.last_time_star_create_time_decrease = elapsed_time

        # let us check if we have reached the final stage. Now we create start at a final fixed rate and to not decrease anymore
        if self.current_stage + 1 == len(self.stages):
            if stage.current_create_duration < stage.new_stars_every_sec_end:
                stage.current_create_duration = stage.new_stars_every_sec_end
                self.final_stage_final_create_duration = True
        return False

    def get_stage_str(self):
        if self.current_stage + 1 == len(self.stages):
            return "FINAL STAGE"
        return str(f"STAGE {self.current_stage + 1}")

    def get_current_create_duration(self):
        return self.stages[self.current_stage].current_create_duration * 1000


class Stage:
    def __init__(self, num: int, duration_secs: int, new_stars_every_ms_begin: int, new_stars_every_ms_end: int):
        self.num = num
        self.duration_secs = duration_secs
        self.new_stars_every_sec_begin = new_stars_every_ms_begin / 1000
        self.new_stars_every_sec_end = new_stars_every_ms_end / 1000
        self.stage_start_elapsed_time = 0

        # calculate the remaining properties
        self.decrease_per_second = (self.new_stars_every_sec_begin - self.new_stars_every_sec_end) / duration_secs
        self.current_create_duration = self.new_stars_every_sec_begin
