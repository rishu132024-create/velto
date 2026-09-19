class VeltoSoundError(Exception):
    pass


class VeltoSound:
    def __init__(self, source=None):
        self.source = source
        self.volume = 1.0
        self.playing = False
        self.loop = False

    def load(self, source):
        self.source = str(source)
        return True

    def play(self, loop=False):
        if self.source is None:
            raise VeltoSoundError("Sound source is not set")

        self.loop = bool(loop)
        self.playing = True
        return True

    def pause(self):
        self.playing = False
        return True

    def stop(self):
        self.playing = False
        return True

    def set_volume(self, volume):
        volume = float(volume)

        if volume < 0 or volume > 1:
            raise VeltoSoundError(
                "Volume must be between 0 and 1"
            )

        self.volume = volume
        return True

    def is_playing(self):
        return self.playing

    def info(self):
        return {
            "source": self.source,
            "volume": self.volume,
            "playing": self.playing,
            "loop": self.loop
        }
