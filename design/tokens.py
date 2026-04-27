from PyQt5.QtGui import QColor

class Color:
    # Primary system
    PRIMARY = QColor("#5E6AD2")      # Raycast purple-blue
    PRIMARY_HOVER = QColor("#6F7BFF")

    # Background
    SURFACE = QColor(30, 30, 30, 200)
    SURFACE_LIGHT = QColor(40, 40, 40, 220)

    # Text
    TEXT_PRIMARY = QColor("#FFFFFF")
    TEXT_SECONDARY = QColor("#BBBBBB")

    # Danger
    DANGER = QColor("#FF5C5C")


class Radius:
    SMALL = 6
    MEDIUM = 12
    LARGE = 16


class Spacing:
    XS = 4
    SM = 8
    MD = 12
    LG = 20