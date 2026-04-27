from PyQt5.QtGui import QFont

class Typography:
    FAMILY = "Inter"

    @staticmethod
    def overlay():
        font = QFont(Typography.FAMILY, 20)
        font.setWeight(QFont.Medium)
        return font

    @staticmethod
    def body():
        return QFont(Typography.FAMILY, 14)

    @staticmethod
    def small():
        return QFont(Typography.FAMILY, 12)