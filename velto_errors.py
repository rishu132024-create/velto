class VeltoError(Exception):

    def __init__(
        self,
        message,
        filename=None,
        line=None,
        source_line=None,
        column=None,
        hint=None
    ):
        self.message = str(message)
        self.filename = filename
        self.line = line
        self.source_line = source_line
        self.column = column
        self.hint = hint

        super().__init__(self.message)

    def format(self):
        parts = ["Velto Error", ""]

        if self.filename:
            parts.append("File: " + str(self.filename))

        if self.line is not None:
            parts.append("Line: " + str(self.line))

        if self.filename or self.line is not None:
            parts.append("")

        if self.source_line:
            source = str(self.source_line).rstrip("\r\n")
            parts.append("    " + source)

            if self.column is not None:
                position = max(0, int(self.column) - 1)
                parts.append("    " + (" " * position) + "^")
            else:
                parts.append("    ^")

            parts.append("")

        parts.append("Error: " + self.message)

        if self.hint:
            parts.append("")
            parts.append("Hint: " + str(self.hint))

        return "\n".join(parts)

    def __str__(self):
        return self.format()


def format_error(error):
    if isinstance(error, VeltoError):
        return error.format()

    return "Velto Error\n\nError: " + str(error)
