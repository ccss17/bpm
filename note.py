"""note rest information dictionary"""

from collections import namedtuple
from enum import Enum

DEFAULT_BPM = 120
DEFAULT_TEMPO = 500000
DEFAULT_TIME_SIGNATURE = (4, 4)
DEFAULT_PPQN = 480
DEFAULT_MEASURE_SPACE = 4

NoteNamedTuple = namedtuple(
    "NoteNamedTuple", ["beat", "name_eng", "name_kor", "symbol", "name_short"]
)


class Rest(Enum):
    """Rest Enum"""

    WHOLE_REST = NoteNamedTuple(4, "whole rest", "온쉼표", "𝄻", "r/1")
    HALF_REST = NoteNamedTuple(2, "half rest", "2분쉼표", "𝄼", "r/2")
    QUARTER_REST = NoteNamedTuple(1, "quarter rest", "4분쉼표", "𝄽", "r/4")
    EIGHTH_REST = NoteNamedTuple(0.5, "eighth rest", "8분쉼표", "𝄾", "r/8")
    SIXTEENTH_REST = NoteNamedTuple(
        0.25, "sixteenth rest", "16분쉼표", "𝄿", "r/16"
    )
    THIRTY_SECOND_REST = NoteNamedTuple(
        0.125, "thirty-second rest", "32분쉼표", "𝅀", "r/32"
    )
    # SIXTY_FOURTH_REST = NoteNamedTuple(
    #     0.0625, "sixty-fourth rest", "64분쉼표", "𝅁", "r/64"
    # )


class Note(Enum):
    """Note Enum"""

    WHOLE_NOTE = NoteNamedTuple(4, "whole note", "온음표", "𝅝", "n/1")
    HALF_NOTE = NoteNamedTuple(2, "half note", "2분음표", "𝅗𝅥", "n/2")
    QUARTER_NOTE = NoteNamedTuple(1, "quarter note", "4분음표", "♩", "n/4")
    EIGHTH_NOTE = NoteNamedTuple(0.5, "eighth note", "8분음표", "♪", "n/8")
    SIXTEENTH_NOTE = NoteNamedTuple(
        0.25, "sixteenth note", "16분음표", "𝅘𝅥𝅯", "n/16"
    )
    THIRTY_SECOND_NOTE = NoteNamedTuple(
        0.125, "thirty-second note", "32분음표", "𝅘𝅥𝅰", "n/32"
    )
    # SIXTY_FOURTH_NOTE = NoteNamedTuple(
    #     0.0625, "sixty-fourth note", "64분음표", "𝅘𝅥𝅱", "n/64"
    # )


COLOR = (
    15,
    165,
    47,
    87,
    121,
    9,
    27,
    190,
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    9,
    11,
    30,
    33,
    37,
    39,
    51,
    46,
    63,
    57,
    87,
    121,
    91,
    104,
    123,
    118,
    129,
    159,
    124,
    127,
    157,
    159,
    135,
    162,
    194,
    201,
    226,
    230,
    217,
)
