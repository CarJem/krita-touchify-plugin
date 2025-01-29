from api_krita.enums.helpers import EnumGroup


class PieAction(EnumGroup):
    def __new__(cls, value):
        setattr(value, "PLACEHOLDER", "PLACEHOLDER")
        super().__new__(cls, value)