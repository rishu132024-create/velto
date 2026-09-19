class VeltoAnimationError(Exception):
    pass


class VeltoAnimation:
    def __init__(self, name="animation"):
        self.name = str(name)
        self.frames = []
        self.current_frame = 0
        self.speed = 10.0
        self.loop = True
        self.playing = False
        self.time = 0.0

    def add_frame(self, image, duration=None):
        if duration is None:
            duration = 1.0 / self.speed

        duration = float(duration)

        if duration <= 0:
            raise VeltoAnimationError(
                "Frame duration must be greater than zero"
            )

        self.frames.append({
            "image": image,
            "duration": duration
        })

        return True

    def remove_frame(self, index):
        index = int(index)

        if index < 0 or index >= len(self.frames):
            raise VeltoAnimationError(
                "Frame index out of range"
            )

        self.frames.pop(index)

        if self.current_frame >= len(self.frames):
            self.current_frame = max(
                0,
                len(self.frames) - 1
            )

    def clear(self):
        self.frames.clear()
        self.current_frame = 0
        self.time = 0.0

    def set_speed(self, fps):
        fps = float(fps)

        if fps <= 0:
            raise VeltoAnimationError(
                "Animation speed must be greater than zero"
            )

        self.speed = fps

    def set_loop(self, enabled):
        self.loop = bool(enabled)

    def play(self):
        self.playing = True

    def pause(self):
        self.playing = False

    def stop(self):
        self.playing = False
        self.current_frame = 0
        self.time = 0.0

    def update(self, delta):
        if not self.playing:
            return

        if not self.frames:
            return

        self.time += float(delta)

        while self.time >= self.frames[self.current_frame]["duration"]:
            self.time -= self.frames[
                self.current_frame
            ]["duration"]

            self.current_frame += 1

            if self.current_frame >= len(self.frames):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(
                        self.frames
                    ) - 1
                    self.playing = False
                    self.time = 0.0
                    break

    def current_image(self):
        if not self.frames:
            return None

        return self.frames[
            self.current_frame
        ]["image"]

    def frame_count(self):
        return len(self.frames)

    def current_frame_index(self):
        return self.current_frame

    def info(self):
        return {
            "name": self.name,
            "frames": len(self.frames),
            "current_frame": self.current_frame,
            "speed": self.speed,
            "loop": self.loop,
            "playing": self.playing
        }
