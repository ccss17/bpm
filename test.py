"""Module for test code"""

import mido
from rich import print as rprint
from rich import pretty
from rich.panel import Panel
from rich.console import Console
from rich.style import Style
from rich.text import Text
# from rich import inspect
# from rich.columns import Columns
# from rich.console import Group
# from rich.padding import Padding
# from rich.color import Color

import bpmlib
import midia


def test_bpm_estimator_librosa(audio_path):
    """Test bpm_estimator_librosa"""
    rprint(round(bpmlib.bpm_estimator_librosa(audio_path)[0]))


def test_bpm_estimator_pretty_midi(midi_path):
    """Test bpm_estimator_pretty_midi"""
    rprint(round(bpmlib.bpm_estimator_pretty_midi(midi_path)))


def test_get_bpm_from_midi(midi_path):
    """Test get_bpm_from_midi"""
    rprint(round(bpmlib.bpm_from_midi_file(midi_path)))


def test_create_sample_midi1(midi_path):
    """test_sample_midi"""
    mid = mido.MidiFile()
    mid.ticks_per_beat = 2
    track = mido.MidiTrack()
    mid.tracks.append(track)

    track.append(
        mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(60), time=0)
    )
    track.append(mido.Message("note_on", note=64, velocity=127, time=4))
    track.append(mido.Message("note_off", note=64, velocity=127, time=8))
    track.append(mido.Message("note_on", note=74, velocity=127, time=4))
    track.append(mido.Message("note_off", note=74, velocity=127, time=8))
    track.append(mido.MetaMessage("end_of_track", time=8))

    mid.save(midi_path)


def test_create_sample_midi2(midi_path):
    """test_sample_midi"""
    mid = mido.MidiFile()
    mid.ticks_per_beat = 2
    track = mido.MidiTrack()
    mid.tracks.append(track)

    track.append(
        mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(60), time=0)
    )
    track.append(mido.Message("note_on", note=64, velocity=64, time=4))
    track.append(mido.MetaMessage("lyrics", text="a", time=4))
    track.append(mido.Message("note_off", note=64, velocity=127, time=8))
    track.append(mido.MetaMessage("lyrics", text="b", time=4))
    track.append(mido.Message("note_on", note=74, velocity=64, time=4))
    track.append(mido.Message("note_off", note=74, velocity=127, time=8))
    track.append(mido.MetaMessage("lyrics", text="d", time=4))

    mid.save(midi_path)


def test_create_sample_midi3(midi_path):
    """test_sample_midi"""
    mid = mido.MidiFile()
    mid.ticks_per_beat = 2
    track = mido.MidiTrack()
    mid.tracks.append(track)

    track.append(
        mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(60), time=0)
    )
    track.append(mido.Message("note_on", note=64, velocity=64, time=4))
    track.append(mido.MetaMessage("lyrics", text="a", time=6))
    track.append(mido.MetaMessage("lyrics", text="b", time=4))
    track.append(mido.Message("note_off", note=64, velocity=127, time=8))

    mid.save(midi_path)


def test_create_sample_midi4(midi_path):
    """test_sample_midi"""
    mid = mido.MidiFile()
    mid.ticks_per_beat = 2
    track = mido.MidiTrack()
    mid.tracks.append(track)

    track.append(
        mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(60), time=0)
    )
    track.append(mido.Message("note_on", note=64, velocity=64, time=2))
    track.append(mido.MetaMessage("lyrics", text="a", time=12))
    track.append(mido.Message("note_on", note=74, velocity=64, time=2))
    track.append(mido.Message("note_off", note=64, velocity=127, time=8))
    track.append(mido.MetaMessage("lyrics", text="b", time=10))
    track.append(mido.Message("note_off", note=74, velocity=127, time=8))

    mid.save(midi_path)


def test_create_sample_midi5(midi_path):
    """test_sample_midi"""
    mid = mido.MidiFile()
    mid.ticks_per_beat = 2
    track = mido.MidiTrack()
    mid.tracks.append(track)

    track.append(
        mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(60), time=0)
    )

    track.append(mido.Message("note_on", note=66, velocity=66, time=0))
    track.append(mido.Message("note_off", note=66, velocity=127, time=1))
    track.append(mido.MetaMessage("lyrics", text="a", time=0))
    track.append(mido.Message("note_on", note=67, velocity=66, time=0))
    track.append(mido.Message("note_off", note=67, velocity=127, time=2))
    track.append(mido.MetaMessage("lyrics", text="b", time=0))
    track.append(mido.Message("note_on", note=68, velocity=66, time=0))
    track.append(mido.Message("note_off", note=68, velocity=127, time=1))
    track.append(mido.MetaMessage("lyrics", text="c", time=1))
    track.append(mido.Message("note_on", note=69, velocity=66, time=0))
    track.append(mido.Message("note_off", note=69, velocity=127, time=2))
    track.append(mido.MetaMessage("lyrics", text="d", time=1))
    track.append(mido.Message("note_on", note=70, velocity=66, time=0))
    track.append(mido.Message("note_off", note=70, velocity=127, time=1))
    track.append(mido.MetaMessage("lyrics", text="e", time=2))
    track.append(mido.Message("note_on", note=71, velocity=66, time=0))
    track.append(mido.Message("note_off", note=71, velocity=127, time=2))
    track.append(mido.MetaMessage("lyrics", text="f", time=2))
    track.append(mido.Message("note_on", note=72, velocity=66, time=0))
    track.append(mido.Message("note_off", note=72, velocity=127, time=2))
    track.append(mido.MetaMessage("lyrics", text="g", time=2))
    track.append(mido.Message("note_on", note=73, velocity=66, time=1))
    track.append(mido.Message("note_off", note=73, velocity=127, time=2))

    mid.save(midi_path)


def test_create_sample_midi6(midi_path):
    """test_sample_midi"""
    mid = mido.MidiFile()
    mid.ticks_per_beat = 1
    track = mido.MidiTrack()
    mid.tracks.append(track)

    track.append(
        mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(60), time=0)
    )
    track.append(mido.Message("note_on", note=61, velocity=64, time=1))
    track.append(mido.Message("note_off", note=61, velocity=127, time=1))

    track.append(mido.Message("note_on", note=62, velocity=66, time=0))
    track.append(mido.MetaMessage("lyrics", text="a", time=0))
    track.append(mido.Message("note_off", note=62, velocity=127, time=1))
    track.append(mido.Message("note_on", note=62, velocity=66, time=0))
    track.append(mido.MetaMessage("lyrics", text="b", time=0))
    track.append(mido.Message("note_off", note=62, velocity=127, time=1))
    track.append(mido.Message("note_on", note=62, velocity=66, time=0))
    track.append(mido.MetaMessage("lyrics", text="c", time=0))
    track.append(mido.Message("note_off", note=62, velocity=127, time=1))
    track.append(mido.Message("note_on", note=62, velocity=66, time=0))
    track.append(mido.MetaMessage("lyrics", text="d", time=0))
    track.append(mido.Message("note_off", note=62, velocity=127, time=1))
    track.append(mido.Message("note_on", note=62, velocity=66, time=0))
    track.append(mido.MetaMessage("lyrics", text="e", time=0))
    track.append(mido.Message("note_off", note=62, velocity=127, time=1))
    track.append(mido.Message("note_on", note=62, velocity=66, time=0))
    track.append(mido.MetaMessage("lyrics", text="f", time=0))
    track.append(mido.Message("note_off", note=62, velocity=127, time=1))

    mid.save(midi_path)


def test_create_sample_midi7(midi_path):
    """test_sample_midi"""
    mid = mido.MidiFile()
    mid.ticks_per_beat = 1
    track = mido.MidiTrack()
    mid.tracks.append(track)

    track.append(
        mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(60), time=0)
    )
    track.append(mido.Message("note_on", note=61, velocity=64, time=0))
    track.append(mido.Message("note_off", note=61, velocity=127, time=1))

    track.append(mido.Message("note_on", note=62, velocity=66, time=0))
    track.append(mido.MetaMessage("lyrics", text="1", time=0))
    track.append(mido.Message("note_off", note=62, velocity=127, time=1))
    track.append(mido.Message("note_on", note=62, velocity=66, time=0))
    track.append(mido.MetaMessage("lyrics", text="1", time=1))
    track.append(mido.Message("note_off", note=62, velocity=127, time=1))
    track.append(mido.Message("note_on", note=62, velocity=66, time=0))
    track.append(mido.MetaMessage("lyrics", text="1", time=2))
    track.append(mido.Message("note_off", note=62, velocity=127, time=1))
    track.append(mido.Message("note_on", note=62, velocity=66, time=0))
    track.append(mido.MetaMessage("lyrics", text="1", time=3))
    track.append(mido.Message("note_off", note=62, velocity=127, time=1))
    track.append(mido.Message("note_on", note=62, velocity=66, time=0))
    track.append(mido.MetaMessage("lyrics", text="1", time=4))
    track.append(mido.Message("note_off", note=62, velocity=127, time=1))
    track.append(mido.Message("note_on", note=62, velocity=66, time=0))
    track.append(mido.MetaMessage("lyrics", text="1", time=5))
    track.append(mido.Message("note_off", note=62, velocity=127, time=1))

    track.append(mido.Message("note_on", note=63, velocity=66, time=0))
    track.append(mido.MetaMessage("lyrics", text="2", time=0))
    track.append(mido.Message("note_off", note=63, velocity=127, time=2))
    track.append(mido.Message("note_on", note=63, velocity=66, time=0))
    track.append(mido.MetaMessage("lyrics", text="2", time=1))
    track.append(mido.Message("note_off", note=63, velocity=127, time=2))
    track.append(mido.Message("note_on", note=63, velocity=66, time=0))
    track.append(mido.MetaMessage("lyrics", text="2", time=2))
    track.append(mido.Message("note_off", note=63, velocity=127, time=2))
    track.append(mido.Message("note_on", note=63, velocity=66, time=0))
    track.append(mido.MetaMessage("lyrics", text="2", time=3))
    track.append(mido.Message("note_off", note=63, velocity=127, time=2))
    track.append(mido.Message("note_on", note=63, velocity=66, time=0))
    track.append(mido.MetaMessage("lyrics", text="2", time=4))
    track.append(mido.Message("note_off", note=63, velocity=127, time=2))
    track.append(mido.Message("note_on", note=63, velocity=66, time=0))
    track.append(mido.MetaMessage("lyrics", text="2", time=5))
    track.append(mido.Message("note_off", note=63, velocity=127, time=2))

    track.append(mido.Message("note_on", note=64, velocity=66, time=0))
    track.append(mido.MetaMessage("lyrics", text="3", time=0))
    track.append(mido.Message("note_off", note=64, velocity=127, time=1))
    track.append(mido.Message("note_on", note=64, velocity=66, time=0))
    track.append(mido.MetaMessage("lyrics", text="3", time=0))
    track.append(mido.Message("note_off", note=64, velocity=127, time=2))
    track.append(mido.Message("note_on", note=64, velocity=66, time=0))
    track.append(mido.MetaMessage("lyrics", text="3", time=0))
    track.append(mido.Message("note_off", note=64, velocity=127, time=3))
    track.append(mido.Message("note_on", note=64, velocity=66, time=0))
    track.append(mido.MetaMessage("lyrics", text="3", time=0))
    track.append(mido.Message("note_off", note=64, velocity=127, time=4))
    track.append(mido.Message("note_on", note=64, velocity=66, time=0))
    track.append(mido.MetaMessage("lyrics", text="3", time=0))
    track.append(mido.Message("note_off", note=64, velocity=127, time=5))

    track.append(mido.Message("note_on", note=65, velocity=66, time=0))
    track.append(mido.MetaMessage("lyrics", text="4", time=0))
    track.append(mido.MetaMessage("lyrics", text="4", time=0))
    track.append(mido.Message("note_off", note=65, velocity=127, time=1))
    track.append(mido.Message("note_on", note=65, velocity=66, time=1))
    track.append(mido.MetaMessage("lyrics", text="4", time=0))
    track.append(mido.MetaMessage("lyrics", text="4", time=1))
    track.append(mido.Message("note_off", note=65, velocity=127, time=2))
    track.append(mido.Message("note_on", note=65, velocity=66, time=2))
    track.append(mido.MetaMessage("lyrics", text="4", time=1))
    track.append(mido.MetaMessage("lyrics", text="4", time=0))
    track.append(mido.Message("note_off", note=65, velocity=127, time=3))
    track.append(mido.Message("note_on", note=65, velocity=66, time=3))
    track.append(mido.MetaMessage("lyrics", text="4", time=1))
    track.append(mido.MetaMessage("lyrics", text="4", time=1))
    track.append(mido.Message("note_off", note=65, velocity=127, time=3))
    track.append(mido.Message("note_on", note=65, velocity=66, time=4))
    track.append(mido.MetaMessage("lyrics", text="4", time=1))
    track.append(mido.MetaMessage("lyrics", text="4", time=2))
    track.append(mido.Message("note_off", note=65, velocity=127, time=3))

    mid.save(midi_path)


def test_create_sample_midi8(midi_path):
    """test_sample_midi"""
    mid = mido.MidiFile()
    mid.ticks_per_beat = 2
    track = mido.MidiTrack()
    mid.tracks.append(track)

    track.append(
        mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(60), time=0)
    )
    track.append(mido.Message("note_on", note=64, velocity=64, time=2))
    track.append(mido.MetaMessage("lyrics", text="a", time=12))
    track.append(mido.Message("note_on", note=74, velocity=64, time=2))
    track.append(mido.MetaMessage("lyrics", text="a", time=12))
    track.append(mido.Message("note_on", note=65, velocity=64, time=2))
    track.append(mido.MetaMessage("lyrics", text="a", time=12))
    track.append(mido.Message("note_on", note=66, velocity=64, time=2))
    track.append(mido.MetaMessage("lyrics", text="a", time=12))
    track.append(mido.Message("note_off", note=64, velocity=127, time=8))
    track.append(mido.MetaMessage("lyrics", text="a", time=10))
    track.append(mido.Message("note_off", note=74, velocity=127, time=8))
    track.append(mido.MetaMessage("lyrics", text="a", time=10))
    track.append(mido.Message("note_off", note=66, velocity=127, time=8))
    track.append(mido.MetaMessage("lyrics", text="a", time=10))
    track.append(mido.Message("note_off", note=65, velocity=127, time=8))
    track.append(mido.MetaMessage("lyrics", text="a", time=10))

    mid.save(midi_path)


def test_rich():
    """test_rich"""

    rprint("[italic red]Hello[/italic red] World!")
    pretty.install()
    rprint(Panel.fit("[bold yellow]Hi, I'm a Panel", border_style="red"))
    # color = Color.parse("red")
    # rprint(color)
    # rprint(inspect(color, methods=True))

    console = Console()
    console.print([1, 2, 3])
    console.print("[blue underline]Looks like a link")
    # console.print(locals())
    console.print("FOO", style="white on blue")
    # rprint("FOO", style="white on blue")
    console.rule("[bold red]Chapter 2")

    console = Console(width=20)
    style = "bold white on blue"
    console.print("Rich", style=style)
    console.print("Rich", style=style, justify="left")
    console.print("Rich", style=style, justify="center")
    console.print("Rich", style=style, justify="right")
    console.rule("[bold red]Chapter 2")

    console = Console()
    # console.input("What is [i]your[/i] [bold red]name[/]? :smiley: ")
    console.print("What is [i]your[/i] [bold red]name[/]? :smiley: ")
    console.print("Hello", style="magenta")
    console.print("Hello", style="color(5)")
    console.print("Hello", style="#af00ff")
    console.print("Hello", style="rgb(175,0,255)")
    console.print("DANGER!", style="red on white")
    console.print(
        "Danger, Will Robinson!", style="blink bold red underline on white"
    )
    console.print("foo [not bold]bar[/not bold] baz", style="bold")
    console.print("Google", style="link https://google.com")

    danger_style = Style(color="red", blink=True, bold=True)
    console.print("Danger, Will Robinson!", style=danger_style)

    console = Console()
    base_style = Style.parse("cyan")
    console.print("Hello, World", style=base_style + Style(underline=True))

    style = Style(color="magenta", bgcolor="yellow", italic=True)
    style = Style.parse("italic magenta on yellow")

    rprint("[bold red]alert![/bold red] Something happened")
    rprint("[bold italic yellow on red blink]This text is impossible to read")
    rprint("[bold red]Bold and red[/] not bold or red")
    rprint("[bold]Bold[italic] bold and italic [/bold]italic[/italic]")

    # console = Console()
    # text = Text("Hello, World!")
    # text.stylize("bold magenta", 0, 6)
    # console.print(text)

    # text = Text.from_ansi("\033[1mHello, World!\033[0m")
    # console.print(text.spans)

    # panel = Panel(Text("Hello", justify="right"))
    # rprint(panel)

    # columns = Columns("sample", equal=True, expand=True)
    # rprint(columns)

    # panel_group = Group(
    #     Panel("Hello", style="on blue"),
    #     Panel("World", style="on red"),
    # )
    # rprint(Panel(panel_group))

    # test = Padding("Hello", 1)
    # rprint(test)

    rprint(Panel("Hello, [red]World!"))
    rprint(Panel.fit("Hello, [red]World!"))
    rprint(Panel("Hello, [red]World!", title="Welcome", subtitle="Thank you"))

    # console.print("Hello", style="color(5)")

    color_list = [15, 165, 47, 9, 87, 121, 27, 190]
    for color in color_list:
        text = Text("Hello", style=f"color({color})")
        # console.print("Hello", style=f"color({color})")
        console.print(text, end=" ")
        # rprint(text)


def test_patch_encode(
    midi_path,
    out_path,
    src_encode="cp949",
    tgt_encode="utf-8",
):
    """Function to patch lyric encoding"""
    # from mido.meta import meta_charset

    mid = mido.MidiFile(midi_path)
    for track in mid.tracks:
        for msg in track:
            if msg.type == "lyrics":
                msg.text = (
                    msg.bin()[3:]
                    .decode(src_encode)
                    .encode(tgt_encode)
                    .decode(tgt_encode)
                )
    # with meta_charset("utf-8"):
    mid.charset = "utf-8"
    mid.save(out_path)


def test_modify_lyrics(midi_path, out_path):
    """test_modify_lyrics"""
    mid = mido.MidiFile(midi_path)
    for track in mid.tracks:
        for i, msg in enumerate(track):
            if i >= 0x100:
                i %= 0x100
            if msg.type == "lyrics":
                msg.text = (
                    msg.bin()[3:]
                    .decode("cp949")
                    .encode("utf-8")
                    .decode("utf-8")
                )
    mid.save(out_path)


def test_insert_lyrics(midi_obj, target_track_list=None):
    """test_insert_lyrics"""
    lyric = (
        "다정했던사람이여나를잊었나벌써나를잊어버렸나그리움만남겨놓고나를잊었나벌써나를잊어버렸나그대지금그누"
        + "구를사랑하는가굳은약속변해버렸나예전 에는우린서로사랑했는데이젠맘이변해버렸나아이별이그리쉬운가세월"
        + "가버렸다고 이젠나를잊고서멀리멀리떠나가는가아아나는몰랐네그대마음변할주우울난정말몰 랐었네오나너하나"
        + "만으을믿고살았네에에에그대만으을믿었네오네가보고파서어나 는어쩌나아아그리우움만쌓이네아이별이그리쉬운"
        + "가세월가버렸다고이젠나를잊고 서멀리멀리떠나가는가아아나는몰랐네그대마음변할주우울난정말몰랐었네오오오 난"
        + "너하나만으을믿고살았네에에그대만으을믿었네오네가아보고파서어나는어쩌나 아아그리우움만쌓이네H"
    )
    for i, track in enumerate(midi_obj.tracks):
        if target_track_list is None or track.name in target_track_list:
            modified_track = []
            modified_num = 0
            for msg in track:
                modified_track.append(msg)
                # idx = j + modified_num
                # if idx >= 0x100:
                #     idx %= 0x100
                if msg.type == "note_on":
                    if modified_num < len(lyric):
                        modified_track.append(
                            mido.MetaMessage(
                                "lyrics", text=f"{lyric[modified_num]}", time=0
                            )
                        )
                    else:
                        modified_track.append(
                            mido.MetaMessage(
                                "lyrics", text=f"x{modified_num:X}", time=0
                            )
                        )
                    modified_num += 1
                    msg.note -= 5
                elif msg.type == "note_off":
                    msg.note -= 5
            midi_obj.tracks[i] = modified_track
    return midi_obj


def test_custom_msg():
    from mido.midifiles.meta import (
        MetaSpec,
        MetaSpec_time_signature,
        add_meta_spec,
    )
    from mido import MetaMessage

    class MetaSpec_rest(MetaSpec):
        type_byte = 0xA0
        attributes = []
        defaults = []

    class MetaSpec_measure(MetaSpec_time_signature):
        type_byte = 0xA1
        attributes = [
            "index",
            "numerator",
            "denominator",
        ]
        defaults = [1, 4, 4]

    add_meta_spec(MetaSpec_rest)
    add_meta_spec(MetaSpec_measure)
    rprint(MetaMessage("measure", time=777))
    rprint(MetaMessage("rest", time=888))


if __name__ == "__main__":
    samples = [
        {
            "wav": "sample/SINGER_66_30TO49_HUSKY_MALE_DANCE_C2835.wav",
            "mid": "sample/SINGER_66_30TO49_HUSKY_MALE_DANCE_C2835.mid",
        },
        {
            "wav": "sample/SINGER_16_10TO29_CLEAR_FEMALE_BALLAD_C0632.wav",
            "mid": "sample/SINGER_16_10TO29_CLEAR_FEMALE_BALLAD_C0632.mid",
        },
        {
            "wav": "sample/ba_05688_-4_a_s02_m_02.wav",
            "mid": "sample/ba_05688_-4_a_s02_m_02.mid",
        },
        {
            "wav": "sample/ba_09303_+0_a_s02_m_02.wav",
            "mid": "sample/ba_09303_+0_a_s02_m_02.mid",
        },
    ]

    real_samples = [
        {
            "mid": "sample/짠짜라-장윤정.mid",
        },
        {
            "mid": "sample/남광진_편지.mid",
        },
        {
            "mid": "sample/그리움만쌓이네.mid",
        },
        {
            "mid": "sample/98_Necro (D#Min 142) Keys -12.mid",
        },
    ]
    #
    # BPM ESTIMATOR vs BPM FROM MIDI
    #
    # test_bpm_estimator_librosa(samples[0]["wav"])
    # test_get_bpm_from_midi(samples[0]["mid"])

    # for sample in samples:
    #     rprint(
    #         f'{bpmlib.bpm_estimator_librosa(sample["wav"])[0]:.2f}'
    #         + f' {bpmlib.get_bpm_from_midi(sample["mid"]):.2f}'
    #     )

    #
    # ANALYSIS MIDI FILE
    #
    # midia.MidiAnalyzer(samples[0]["mid"]).analysis(track_bound=55)
    # midia.MidiAnalyzer(samples[2]["mid"]).analysis(track_bound=40)
    # midia.MidiAnalyzer(samples[3]["mid"]).analysis(track_bound=20)
    # midia.MidiAnalyzer(samples[0]["mid"]).analysis()

    # midia.MidiAnalyzer(samples[2]["mid"]).analysis(blind_note=True)
    # midia.MidiAnalyzer(samples[2]["mid"]).analysis(blind_time=True)
    # midia.MidiAnalyzer(samples[2]["mid"]).analysis(convert_1_to_0=True)
    # midia.MidiAnalyzer(samples[3]["mid"]).analysis(convert_1_to_0=True)
    # midia.MidiAnalyzer(samples[2]["mid"]).analysis(track_bound=15)
    # ma = midia.MidiAnalyzer(samples[2]["mid"], convert_1_to_0=True)

    ma = midia.MidiAnalyzer(samples[2]["mid"])
    ma.quantization()
    ma.analysis(track_bound=None, track_list=None, blind_note_info=True)
    # ma.analysis(track_bound=30, track_list=["Melody"])
    # mid_path = "test_q2_midi.mid"
    # mid_path = "test_q_ff_merged_midi.mid"
    # ma.mid.save(mid_path)
    # ma = midia.MidiAnalyzer(mid_path)
    # ma.analysis(track_bound=None, track_list=None)
    # print(list(Note)[-1].value.beat, list(Note)[-1].value.beat / 2)
    # midia.midi2wav(ma.mid, "test.wav", 62)

    # t1 = mido.MidiFile(mid_path).tracks[1]
    # t2 = mido.MidiFile(samples[2]["mid"]).tracks[1]
    # midia.compare_track(t1, t2)

    # test_custom_msg()

    # rprint(mido.Message("note_on", note=0, velocity=0, time=0))

    # def beat_iter(i):
    #     beat = 4 * (3 / 4) ** ((i + 1) // 2) * (2 / 3) ** (i // 2)
    #     return round(beat, 4)
    # ma.analysis()

    # 에러 사항 출력:
    # ticks per beat 기반으로 가사와 음표가 몇분음표인지 출력
    # quantization 에러를 줄여야 함. --> 에러가 중첩되니까 --> 싱크를 맞춰야 함.
    # --> 이전 quantization 에러를 고려해서 다음 노트의 에러를 계산해야 함.
    # 에러가 - 면 밀렸다, + 면 땡겨졌다 이런 식으로 판단해서, 지금은 에러를 독립적으로
    # 보기 때문에 에러가 계속 중첩 되는 상황
    # --> 최종적으로는 quantization 된 mid 파일을 음원으로 재생하고, 노래를 같이 재생해보면서
    # 싱크가 맞으면 제대로 했다 이런 결론을 내릴 수 있음.

    #
    # LYRIC PATCH TEST
    #
    # midi_path = samples[3]["mid"]
    # idx = midi_path.find(".")
    # out_path = midi_path[:idx] + "(utf-8)2" + midi_path[idx:]
    # test_patch_encode(
    #     midi_path, out_path, src_encode="cp949", tgt_encode="utf-8"
    # )

    # ma = midia.MidiAnalyzer(samples[2]["mid"])
    # ma.analysis(blind_time=True, target_track_list=[
    #             "Melody"], track_bound=20)
    # ma.partition()
    # ma.analysis(blind_time=True, track_bound=20)
    # ma.analysis(track_bound=20)
    # ma.analysis()

    # modified_midi_path = "test.mid"
    # test_modify_lyrics(samples[2]["mid"], modified_midi_path)
    # midia.MidiAnalyzer(modified_midi_path).analysis(blind_time=True)

    # ma = midia.MidiAnalyzer(real_samples[3]["mid"])
    # ma.analysis(target_track_list=["Musicbox"], blind_time=True)
    # ma.analysis()
    # test_insert_lyrics(ma.mid, target_track_list=None)
    # modified_midi_path = "test2.mid"
    # ma.mid.save(modified_midi_path, encoding='utf-8'=True)
    # ma = midia.MidiAnalyzer(modified_midi_path)
    # ma.analysis(target_track_list=["Musicbox"], blind_time=True)

    # midi_path = "exported_midi/ba_05688_-4_a_s02_m_02(utf-8).mid"
    # ma = midia.MidiAnalyzer(midi_path)
    # ma.analysis(blind_time=True)

    #
    # TEST RICH
    #
    # test_rich()

    #
    # CREATE SAMPLE MIDI AND ANALYSIS IT
    #
    # test_create_sample_midi1("test_sample1.mid")
    # midia.midi2wav("test_sample1.mid", "test_sample1.wav", 60)
    # test_create_sample_midi2("test_sample2.mid")
    # midia.midi2wav("test_sample2.mid", "test_sample2.wav", 60)
    # test_create_sample_midi3("test_sample3.mid")
    # midia.midi2wav("test_sample3.mid", "test_sample3.wav", 60)
    # test_create_sample_midi4("test_sample4.mid")
    # midia.midi2wav("test_sample4.mid", "test_sample4.wav", 60)
    # test_create_sample_midi6("test_sample6.mid")
    # midia.midi2wav("test_sample6.mid", "test_sample6.wav", 60)
    # test_create_sample_midi7("test_sample7.mid")
    # midia.midi2wav("test_sample7.mid", "test_sample7.wav", 60)
    # test_create_sample_midi8("test_sample8.mid")
    # midia.midi2wav("test_sample8.mid", "test_sample8.wav", 60)

    # midia.MidiAnalyzer("test_sample1.mid").analysis()
    # midia.MidiAnalyzer("test_sample2.mid").analysis()
    # midia.MidiAnalyzer("test_sample3.mid").analysis()
    # midia.MidiAnalyzer("test_sample4.mid").analysis()
    # midia.MidiAnalyzer("test_sample5.mid").analysis()
    # midia.MidiAnalyzer("test_sample6.mid").analysis()
    # midia.MidiAnalyzer("test_sample7.mid").analysis()
    # midia.MidiAnalyzer("test_sample8.mid").analysis()

    #
    # GET STATISTICS of ESTIMATED CORRECTED BPM ERROR
    #
    # import pathlib
    # sample_num = 1
    # data_path = pathlib.Path("dataset/SINGER_16")
    # bpmlib.statistics_estimated_bpm_error(data_path)
    # bpmlib.statistics_estimated_bpm_error(data_path, sample_num=sample_num)
    # rprint()
    # data_path = pathlib.Path("dataset/가창자_s02")
    # bpmlib.statistics_estimated_bpm_error(data_path)

    # data_path = pathlib.Path("d:/dataset/177.다음색 가이드보컬 데이터")
    # rprint(data_path)
    # bpmlib.statistics_estimated_bpm_error(data_path)
    # rprint()
    # data_path = pathlib.Path("d:/dataset/004.다화자 가창 데이터")
    # rprint(data_path)
    # bpmlib.statistics_estimated_bpm_error(data_path)
    #
    # Output:
    #
    # d:\dataset\177.다음색 가이드보컬 데이터
    # error(0); mean/std: 42.13, 35.27
    # error(2); mean/std:  4.39,  7.71
    # error(4); mean/std:  4.08,  6.77
    # error(8); mean/std:  4.08,  6.77
    # selected error:
    #   error(/8): 0
    #   error(/4): 41
    #   error(/2): 1998
    #   error(0) : 1541
    #   error(*2): 29
    #   error(*4): 0
    #   error(*8): 0
    # d:\dataset\004.다화자 가창 데이터
    # error(0); mean/std: 38.97, 36.49
    # error(2); mean/std:  6.16,  8.72
    # error(4); mean/std:  5.91,  8.17
    # error(8); mean/std:  5.91,  8.17
    # selected error:
    #   error(/8): 0
    #   error(/4): 78
    #   error(/2): 1993
    #   error(0) : 2078
    #   error(*2): 77
    #   error(*4): 0
    #   error(*8): 0

    #
    # bpm error samples
    #
    # underestimated bpm(/2) sample:
    #   SINGER_14_10TO29_NORMAL_FEMALE_DANCE_C0555.wav
    #   [estimated bpm]=78.30, [bpm from midi file]=120.0
    # underestimated bpm(/2) sample:
    #   ba_05206_+0_a_s14_f_03.wav
    #   [estimated bpm]=95.70, [bpm from midi file]=203.98
    # overestimated bpm(*2) sample:
    #   SINGER_12_10TO29_CLEAR_FEMALE_DANCE_C0477.wav
    #   [estimated bpm]=215.33, [bpm from midi file]=120.0
    # overestimated bpm(*2) sample:
    #   ba_06573_-1_a_s09_m_03.wav
    #   [estimated bpm]=112.34, [bpm from midi file]=63.23
