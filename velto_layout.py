class VeltoLayoutError(Exception):
    pass


class Layout:
    def __init__(
        self,
        x=0,
        y=0,
        width=400,
        height=300,
        spacing=10
    ):
        self.x = float(x)
        self.y = float(y)
        self.width = float(width)
        self.height = float(height)
        self.spacing = float(spacing)
        self.children = []

    def add(self, element):
        if not hasattr(element, "set_position"):
            raise VeltoLayoutError(
                "Invalid UI element"
            )

        self.children.append(element)

    def remove(self, element):
        if element in self.children:
            self.children.remove(element)

    def clear(self):
        self.children.clear()

    def count(self):
        return len(self.children)


class Row(Layout):
    def arrange(self):
        current_x = self.x

        for element in self.children:
            element.set_position(
                current_x,
                self.y
            )

            current_x += (
                element.width
                + self.spacing
            )


class Column(Layout):
    def arrange(self):
        current_y = self.y

        for element in self.children:
            element.set_position(
                self.x,
                current_y
            )

            current_y += (
                element.height
                + self.spacing
            )


class Grid(Layout):
    def __init__(
        self,
        columns=2,
        x=0,
        y=0,
        width=400,
        height=300,
        spacing=10
    ):
        super().__init__(
            x,
            y,
            width,
            height,
            spacing
        )

        self.columns = int(columns)

        if self.columns <= 0:
            raise VeltoLayoutError(
                "Columns must be greater than zero"
            )

    def arrange(self):
        for index, element in enumerate(
            self.children
        ):
            column = index % self.columns
            row = index // self.columns

            cell_width = (
                self.width
                / self.columns
            )

            cell_height = (
                element.height
                + self.spacing
            )

            element.set_position(
                self.x
                + column * cell_width,
                self.y
                + row * cell_height
            )
