import tkinter as tk


class VeltoGraphicsError(Exception):
    pass


class VeltoGraphics:
    def __init__(self, width=800, height=600, title="Velto"):
        self.width = int(width)
        self.height = int(height)
        self.title = str(title)

        self.root = None
        self.canvas = None

    def create_window(self):
        if self.root is not None:
            raise VeltoGraphicsError(
                "Graphics window already exists"
            )

        self.root = tk.Tk()

        self.root.title(self.title)

        self.root.geometry(
            str(self.width)
            + "x"
            + str(self.height)
        )

        self.canvas = tk.Canvas(
            self.root,
            width=self.width,
            height=self.height,
            bg="white"
        )

        self.canvas.pack()

        return True

    def clear(self):
        if self.canvas is None:
            raise VeltoGraphicsError(
                "Graphics window is not created"
            )

        self.canvas.delete("all")

    def rectangle(
        self,
        x1,
        y1,
        x2,
        y2,
        fill="black"
    ):
        if self.canvas is None:
            raise VeltoGraphicsError(
                "Graphics window is not created"
            )

        return self.canvas.create_rectangle(
            x1,
            y1,
            x2,
            y2,
            fill=fill
        )

    def circle(
        self,
        x,
        y,
        radius,
        fill="black"
    ):
        if self.canvas is None:
            raise VeltoGraphicsError(
                "Graphics window is not created"
            )

        return self.canvas.create_oval(
            x - radius,
            y - radius,
            x + radius,
            y + radius,
            fill=fill
        )

    def line(
        self,
        x1,
        y1,
        x2,
        y2,
        fill="black",
        width=1
    ):
        if self.canvas is None:
            raise VeltoGraphicsError(
                "Graphics window is not created"
            )

        return self.canvas.create_line(
            x1,
            y1,
            x2,
            y2,
            fill=fill,
            width=width
        )

    def text(
        self,
        x,
        y,
        value,
        fill="black",
        size=20
    ):
        if self.canvas is None:
            raise VeltoGraphicsError(
                "Graphics window is not created"
            )

        return self.canvas.create_text(
            x,
            y,
            text=str(value),
            fill=fill,
            font=("Arial", size)
        )

    def run(self):
        if self.root is None:
            raise VeltoGraphicsError(
                "Graphics window is not created"
            )

        self.root.mainloop()

    def close(self):
        if self.root is not None:
            self.root.destroy()

            self.root = None
            self.canvas = None
