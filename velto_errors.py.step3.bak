class VeltoError(Exception):
    def __init__(self, message, filename=None, line=None, source_line=None):
        self.message = message
        self.filename = filename
        self.line = line
        self.source_line = source_line

        super().__init__(message)

    def format(self):
        lines = ["Velto Error"]

        if self.filename:
            lines.append(f"File: {self.filename}")

        if self.line is not None:
            lines.append(f"Line: {self.line}")

        if self.filename or self.line is not None:
            lines.append("")

        if self.source_line:
            lines.append(f"    {self.source_line}")

            if self.line is not None:
                lines.append(
                    f"    {' ' * 0}^"
                )

        if self.source_line:
            lines.append("")

        lines.append(f"Error: {self.message}")

        return "\n".join(lines)
