"""Module for test code"""

import pathlib

import bpmlib

import mido
from rich import print


def test_bpm_estimator_librosa(audio_path):
    """Test bpm_estimator_librosa"""
    print(round(bpmlib.bpm_estimator_librosa(audio_path)[0]))


def test_bpm_estimator_pretty_midi(midi_path):
    """Test bpm_estimator_pretty_midi"""
    print(round(bpmlib.bpm_estimator_pretty_midi(midi_path)))


def test_get_bpm_from_midi(midi_path):
    """Test get_bpm_from_midi"""
    print(round(bpmlib.get_bpm_from_midi(midi_path)))


def test_create_sample_midi1(midi_path):
    """test_sample_midi"""
    mid = mido.MidiFile()
    mid.ticks_per_beat = 2
    track = mido.MidiTrack()
    mid.tracks.append(track)

    track.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(60), time=0))
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

    track.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(60), time=0))
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

    track.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(60), time=0))
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

    track.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(60), time=0))
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

    track.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(60), time=0))

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

    track.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(60), time=0))
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

    track.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(60), time=0))
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

    track.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(60), time=0))
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
    from rich import inspect
    from rich import print
    from rich.columns import Columns
    from rich import pretty
    from rich.panel import Panel
    from rich.color import Color
    from rich.console import Console
    from rich.console import Group
    from rich.style import Style
    from rich.text import Text
    from rich.padding import Padding

    print("[italic red]Hello[/italic red] World!")
    pretty.install()
    print(Panel.fit("[bold yellow]Hi, I'm a Panel", border_style="red"))
    # color = Color.parse("red")
    # print(color)
    # print(inspect(color, methods=True))

    console = Console()
    console.print([1, 2, 3])
    console.print("[blue underline]Looks like a link")
    # console.print(locals())
    console.print("FOO", style="white on blue")
    # print("FOO", style="white on blue")
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
    console.print("Danger, Will Robinson!", style="blink bold red underline on white")
    console.print("foo [not bold]bar[/not bold] baz", style="bold")
    console.print("Google", style="link https://google.com")

    danger_style = Style(color="red", blink=True, bold=True)
    console.print("Danger, Will Robinson!", style=danger_style)

    console = Console()
    base_style = Style.parse("cyan")
    console.print("Hello, World", style=base_style + Style(underline=True))

    style = Style(color="magenta", bgcolor="yellow", italic=True)
    style = Style.parse("italic magenta on yellow")

    print("[bold red]alert![/bold red] Something happened")
    print("[bold italic yellow on red blink]This text is impossible to read")
    print("[bold red]Bold and red[/] not bold or red")
    print("[bold]Bold[italic] bold and italic [/bold]italic[/italic]")

    # console = Console()
    # text = Text("Hello, World!")
    # text.stylize("bold magenta", 0, 6)
    # console.print(text)

    # text = Text.from_ansi("\033[1mHello, World!\033[0m")
    # console.print(text.spans)

    # panel = Panel(Text("Hello", justify="right"))
    # print(panel)

    # columns = Columns("sample", equal=True, expand=True)
    # print(columns)

    # panel_group = Group(
    #     Panel("Hello", style="on blue"),
    #     Panel("World", style="on red"),
    # )
    # print(Panel(panel_group))

    # test = Padding("Hello", 1)
    # print(test)

    print(Panel("Hello, [red]World!"))
    print(Panel.fit("Hello, [red]World!"))
    print(Panel("Hello, [red]World!", title="Welcome", subtitle="Thank you"))

    # console.print("Hello", style="color(5)")

    color_list = [15, 165, 47, 9, 87, 121, 27, 190]
    for color in color_list:
        text = Text("Hello", style=f"color({color})")
        # console.print("Hello", style=f"color({color})")
        console.print(text, end=" ")
        # print(text)


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

    #
    # PRE-DEFINED NOTES
    #
    # bpmlib.show_notes()

    #
    # BPM ESTIMATOR vs BPM FROM MIDI
    #
    # test_bpm_estimator_librosa(samples[0]["wav"])
    # test_get_bpm_from_midi(samples[0]["mid"])

    # for sample in samples:
    #     print(
    #         f'{bpmlib.bpm_estimator_librosa(sample["wav"])[0]:.2f}'
    #         + f' {bpmlib.get_bpm_from_midi(sample["mid"]):.2f}'
    #     )

    #
    # ANALYSIS MIDI FILE
    #
    # bpmlib.MidiAnalyzer(samples[0]["mid"]).analysis(print_bound_per_track=55)
    # bpmlib.MidiAnalyzer(samples[2]["mid"]).analysis(print_bound_per_track=40)
    # bpmlib.MidiAnalyzer(samples[3]["mid"]).analysis(print_bound_per_track=20)
    # bpmlib.MidiAnalyzer(samples[0]["mid"]).analysis()
    # bpmlib.MidiAnalyzer(samples[1]["mid"])
    bpmlib.MidiAnalyzer(samples[2]["mid"]).analysis()
    # bpmlib.MidiAnalyzer(samples[2]["mid"]).analysis(blind_time=True)
    # bpmlib.MidiAnalyzer(samples[2]["mid"]).analysis(convert_1_to_0=True, print_bound_per_track=40)
    # bpmlib.MidiAnalyzer(samples[3]["mid"])
    # bpmlib.MidiAnalyzer(samples[3]["mid"]).analysis(convert_1_to_0=True)
    # bpmlib.MidiAnalyzer(samples[2]["mid"]).analysis(print_bound_per_track=15)
    # bpmlib.MidiAnalyzer(samples[2]["mid"]).analysis(
    #     convert_1_to_0=True, blind_note_lyrics=True
    # )
    # for k, v in bpmlib.NOTE.items():
    #     print(f'{k} {v}')

    # 에러 사항 출력:
    # 가사의 time=0 이 아닌 것들 출력
    # note 가 꼬여있는 것들 출력

    # ticks per beat 기반으로 가사와 음표가 몇분음표인지 출력

    #
    # LYRIC PATCH TEST
    #
    # midi_path = samples[3]["mid"]
    # idx = midi_path.find(".")
    # out_path = midi_path[:idx] + "(utf-8)" + midi_path[idx:]
    # bpmlib.patch_lyric(midi_path, out_path, src_encode="cp949", tgt_encode="utf-8")

    #
    # TEST RICH
    #
    # test_rich()

    #
    # CREATE SAMPLE MIDI AND ANALYSIS IT
    #
    # test_create_sample_midi1("test_sample1.mid")
    # bpmlib.midi2wav("test_sample1.mid", "test_sample1.wav", 60)
    # test_create_sample_midi2("test_sample2.mid")
    # bpmlib.midi2wav("test_sample2.mid", "test_sample2.wav", 60)
    # test_create_sample_midi3("test_sample3.mid")
    # bpmlib.midi2wav("test_sample3.mid", "test_sample3.wav", 60)
    # test_create_sample_midi4("test_sample4.mid")
    # bpmlib.midi2wav("test_sample4.mid", "test_sample4.wav", 60)
    # test_create_sample_midi6("test_sample6.mid")
    # bpmlib.midi2wav("test_sample6.mid", "test_sample6.wav", 60)
    # test_create_sample_midi7("test_sample7.mid")
    # bpmlib.midi2wav("test_sample7.mid", "test_sample7.wav", 60)
    # test_create_sample_midi8("test_sample8.mid")
    # bpmlib.midi2wav("test_sample8.mid", "test_sample8.wav", 60)

    # bpmlib.MidiAnalyzer("test_sample1.mid").analysis()
    # bpmlib.MidiAnalyzer("test_sample2.mid").analysis()
    # bpmlib.MidiAnalyzer("test_sample3.mid").analysis()
    # bpmlib.MidiAnalyzer("test_sample4.mid").analysis()
    # bpmlib.MidiAnalyzer("test_sample5.mid").analysis()
    # bpmlib.MidiAnalyzer("test_sample6.mid").analysis()
    # bpmlib.MidiAnalyzer("test_sample7.mid").analysis()
    # bpmlib.MidiAnalyzer("test_sample8.mid").analysis()

    #
    # GET STATISTICS of ESTIMATED CORRECTED BPM ERROR
    #
    # sample_num = 1
    # data_path = pathlib.Path("dataset/SINGER_16")
    # bpmlib.statistics_estimated_bpm_error(data_path)
    # bpmlib.statistics_estimated_bpm_error(data_path, sample_num=sample_num)
    # print()
    # data_path = pathlib.Path("dataset/가창자_s02")
    # bpmlib.statistics_estimated_bpm_error(data_path)

    # data_path = pathlib.Path("d:/dataset/177.다음색 가이드보컬 데이터")
    # print(data_path)
    # bpmlib.statistics_estimated_bpm_error(data_path)
    # print()
    # data_path = pathlib.Path("d:/dataset/004.다화자 가창 데이터")
    # print(data_path)
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
