"""note rest information dictionary"""

from collections import namedtuple
from enum import Enum

NoteRestNamedTuple = namedtuple("Rest", ["beat", "name_eng", "name_kor", "symbol"])


class Rest(Enum):
    """Rest Enum"""

    WHOLE_REST = NoteRestNamedTuple(4, "whole rest", "온쉼표", "𝄻")
    DOTTED_WHOLE_REST = NoteRestNamedTuple(3, "dotted whole rest", "점2분쉼표", "𝄼.")
    HALF_REST = NoteRestNamedTuple(2, "half rest", "2분쉼표", "𝄼")
    DOTTED_QUARTER_REST = NoteRestNamedTuple(
        1.5, "dotted quarter rest", "점4분쉼표", "𝄽."
    )
    QUARTER_REST = NoteRestNamedTuple(1, "quarter rest", "4분쉼표", "𝄽")
    DOTTED_EIGHTH_REST = NoteRestNamedTuple(
        0.75, "dotted eighth rest", "점8분쉼표", "𝄾."
    )
    EIGHTH_REST = NoteRestNamedTuple(0.5, "eighth rest", "8분쉼표", "𝄾")
    DOTTED_SIXTEENTH_REST = NoteRestNamedTuple(
        0.375, "dotted sixteenth rest", "점16분쉼표", "𝄿."
    )
    SIXTEENTH_REST = NoteRestNamedTuple(0.25, "sixteenth rest", "16분쉼표", "𝄿")
    DOTTED_THIRTY_SECOND_REST = NoteRestNamedTuple(
        0.1875, "dotted thirty-second rest", "점32분쉼표", "𝅀."
    )
    THIRTY_SECOND_REST = NoteRestNamedTuple(
        0.125, "thirty-second rest", "32분쉼표", "𝅀"
    )


class Note(Enum):
    """Note Enum"""

    WHOLE_NOTE = NoteRestNamedTuple(4, "whole note", "온음표", "𝅝")
    DOTTED_WHOLE_NOTE = NoteRestNamedTuple(3, "dotted whole note", "점2분음표", "𝅗𝅥.")
    HALF_NOTE = NoteRestNamedTuple(2, "half note", "2분음표", "𝅗𝅥")
    DOTTED_QUARTER_NOTE = NoteRestNamedTuple(
        1.5, "dotted quarter note", "점4분음표", "♩."
    )
    QUARTER_NOTE = NoteRestNamedTuple(1, "quarter note", "4분음표", "♩")
    DOTTED_EIGHTH_NOTE = NoteRestNamedTuple(
        0.75, "dotted eighth note", "점8분음표", "♪."
    )
    EIGHTH_NOTE = NoteRestNamedTuple(0.5, "eighth note", "8분음표", "♪")
    DOTTED_SIXTEENTH_NOTE = NoteRestNamedTuple(
        0.375, "dotted sixteenth note", "점16분음표", "𝅘𝅥𝅯."
    )
    SIXTEENTH_NOTE = NoteRestNamedTuple(0.25, "sixteenth note", "16분음표", "𝅘𝅥𝅯")
    DOTTED_THIRTY_SECOND_NOTE = NoteRestNamedTuple(
        0.1875, "dotted thirty-second note", "점32분음표", "𝅘𝅥𝅰."
    )
    THIRTY_SECOND_NOTE = NoteRestNamedTuple(
        0.125, "thirty-second note", "32분음표", "𝅘𝅥𝅰"
    )


NOTE_COLOR_LIST = (
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
