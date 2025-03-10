"""Module for test code"""

import pathlib
from pathlib import Path
import sys
import multiprocessing as mp
import pathlib
import random
import os
import json
import re

import numpy as np
import librosa
import soundfile
import mido
from pydub import AudioSegment
from pydub.silence import split_on_silence

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

from g2pk import G2p


from slicer2 import Slicer
# from slicer2_ver4 import Slicer

import bpmlib
import midia
import note


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
    lyric = """J 다정했던사람이여나를잊었나 벌써나를 잊어버렸나 그리움만남겨놓고나를잊었나 벌써나를잊어 버렸나 그대지금그누구를사랑하는가 굳은약속 변해버렸나 예전에는우린서로사랑 했는데 이젠맘이변해 버렸나 아이별이 그리쉬운가 세월가버렸다고 이젠나를잊고서멀리 멀리떠나가는가 아아나는몰랐네 그대마음변할주우울 난정말몰랐었네 오나너하나만으을 믿고살았네에에에 그대만으을믿었네 오네가보고파서어 나는어쩌나아아 그리우움만쌓이네 아이별이 그리쉬운가 세월가버렸다고 이젠나를잊고서 멀리  멀리떠나가는가 아아나는몰랐네 그대마음변할주우울 난정말몰랐었네 오오오난너하나만으을 믿고살았네에에 그대만으을믿었네 오네가아 보고파서어나는어쩌나아아 그리우움만쌓이네 H"""
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


def test_slice(wav_path, dir_path):
    """test_slice"""
    audio, sr = librosa.load(wav_path, sr=None, mono=False)
    slicer = Slicer(
        sr=sr,
        threshold=-40,
        min_length=5000,
        min_interval=300,
        hop_size=10,
        max_sil_kept=500,
    )
    chunks = slicer.slice(audio)
    for i, chunk in enumerate(chunks):
        if len(chunk.shape) > 1:
            chunk = chunk.T  # Swap axes if the audio is stereo.
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        soundfile.write(
            f"{dir_path}/example_{i:02}.wav", chunk, sr
        )  # Save sliced audio files with soundfile.


def test_clips_duration(clip_path):
    """test_clips_duration"""
    data_path = pathlib.Path(clip_path)
    time = 0
    for clip in sorted(data_path.rglob("*.wav")):
        duration = librosa.get_duration(path=clip)
        time += duration
        print(clip, duration)
    print(time)
    print(librosa.get_duration(path="sample/ba_05688_-4_a_s02_m_02.wav"))


def test_slice_midi(wav_path, mid_path):
    """test_slice_midi"""
    ma = midia.MidiAnalyzer(mid_path, convert_1_to_0=True)
    ma.split_space_note(remove_silence_threshold=0.3)
    ma.quantization(unit="32")
    # ma.analysis(
    #     track_bound=None,
    #     track_list=None,
    #     blind_note_info=True,
    #     blind_lyric=False,
    # )

    audio, sr = librosa.load(wav_path, sr=None, mono=False)
    slicer = Slicer(
        sr=sr,
        threshold=-40,
        min_length=5000,
        max_length=500,
        min_interval=300,
        hop_size=10,
        max_sil_kept=500,
    )
    chunks = slicer.slice(audio)
    print("chunk_time:")
    for chunk_time in slicer.chunks_time:
        rprint(chunk_time, (chunk_time[1] - chunk_time[0]) / 100)

    # begin, end = slicer.chunks_time[0]
    # rprint(ma.slice(begin / 100, end / 100))
    # chunks_time = [
    #     (chunk_time[0] / 100, chunk_time[1] / 100)
    #     for chunk_time in slicer.chunks_time
    # ]
    g2p = G2p()
    for item in ma.slice_chunks_time(slicer.chunks_time):
        rprint(item[0])
        if item[1] is None:
            rprint(item[1])
        else:
            rprint(f"{item[1]} = [red]{np.sum(item[1]):.2f}[/red]")
        rprint(f'"{item[2]}"')
        if item[-1] is None:
            rprint(f'"{item[-1]}"')
        else:
            rprint(f'"{g2p(item[-1])}"')
        print()


def test_trim_slice(wav_path, dir_path):
    """test_trim_slice"""
    audio, sr = librosa.load(wav_path, sr=None, mono=False)
    slicer = Slicer(
        sr=sr,
        threshold=-40,
        min_length=5000,
        min_interval=300,
        hop_size=10,
        max_sil_kept=500,
    )
    audio_trimmed, index = librosa.effects.trim(audio)
    chunks = slicer.slice(audio_trimmed)
    for i, chunk in enumerate(chunks):
        if len(chunk.shape) > 1:
            chunk = chunk.T  # Swap axes if the audio is stereo.
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        soundfile.write(
            f"{dir_path}/example_{i:02}.wav", chunk, sr
        )  # Save sliced audio files with soundfile.


def test_trim_slice_midi(wav_path, mid_path):
    """test_trim_slice_midi"""
    ma = midia.MidiAnalyzer(mid_path, convert_1_to_0=True)
    ma.split_space_note(remove_silence_threshold=0.3)
    ma.quantization(unit="32")
    # ma.analysis(
    #     track_bound=None,
    #     track_list=None,
    #     blind_note_info=True,
    #     blind_lyric=False,
    # )

    audio, sr = librosa.load(wav_path, sr=None, mono=False)
    slicer = Slicer(
        sr=sr,
        threshold=-40,
        min_length=5000,
        min_interval=300,
        hop_size=10,
        max_sil_kept=500,
    )
    chunks = slicer.slice(audio)
    for i, chunk_time in enumerate(slicer.chunks_time):
        print(i, chunk_time, (chunk_time[1] - chunk_time[0]) / 100)
    print()

    audio_trimmed, index = librosa.effects.trim(audio)
    print(index, index[0] / sr, index[1] / sr)
    chunks = slicer.slice(audio_trimmed)
    for i, chunk_time in enumerate(slicer.chunks_time):
        print(i, chunk_time, (chunk_time[1] - chunk_time[0]) / 100)

    # begin, end = slicer.chunks_time[0]
    # rprint(ma.slice(begin / 100, end / 100))
    # chunks_time = [
    #     (chunk_time[0] / 100, chunk_time[1] / 100)
    #     for chunk_time in slicer.chunks_time
    # ]
    # g2p = G2p()
    # for item in ma.slice_chunks_time(slicer.chunks_time):
    #     rprint(item[0])
    #     if item[1] is None:
    #         rprint(item[1])
    #     else:
    #         rprint(f"{item[1]} = [red]{np.sum(item[1]):.2f}[/red]")
    #     rprint(f'"{item[2]}"')
    #     if item[-1] is None:
    #         rprint(f'"{item[-1]}"')
    #     else:
    #         rprint(f'"{g2p(item[-1])}"')
    #     print()


def test_split_audio_pydub(wav_path, dir_path):
    # Load the audio file
    audio = AudioSegment.from_file(wav_path, format="wav")

    # Parameters
    min_silence_len = 700  # Minimum silence length in ms
    silence_thresh = -40  # Silence threshold in dB
    keep_silence = 200  # Keep some silence at the start and end of chunks
    max_duration = 15000  # Max segment length in ms (5 seconds)

    # Step 1: Split by silence
    chunks = split_on_silence(
        audio,
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh,
        keep_silence=keep_silence,
    )

    # Step 2: Ensure no chunk is longer than max_duration
    def split_long_chunks(chunks, max_duration):
        final_chunks = []
        for chunk in chunks:
            while len(chunk) > max_duration:
                final_chunks.append(
                    chunk[:max_duration]
                )  # Take the first part
                chunk = chunk[max_duration:]  # Keep the remaining part
            final_chunks.append(chunk)  # Add the last remaining part
        return final_chunks

    # Apply max length split
    final_chunks = split_long_chunks(chunks, max_duration)

    # Export each chunk
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    for i, chunk in enumerate(final_chunks):
        chunk.export(f"{dir_path}/chunk_{i}.wav", format="wav")

    print(f"Total {len(final_chunks)} chunks saved.")


def test_split_librosa(audio_path, dir_path):
    # Load the audio file
    # audio_path = "audio.wav"
    y, sr = librosa.load(audio_path, sr=None)  # Load with original sample rate

    # Convert amplitude to decibels (dB)
    y_db = librosa.amplitude_to_db(np.abs(y), ref=np.max)

    # Set an absolute silence threshold (e.g., -40 dBFS)
    absolute_silence_thresh = -40  # Silence if below this

    # Mask silent regions (set them to 0)
    y_filtered = np.where(y_db > absolute_silence_thresh, y, 0)

    # Detect non-silent intervals
    non_silent_intervals = librosa.effects.split(
        y_filtered, top_db=10
    )  # Works with modified signal

    # Maximum segment length in seconds
    max_duration = 15  # Max segment length in seconds
    max_samples = int(max_duration * sr)  # Convert to samples

    # Function to enforce max segment length
    def split_long_segments(y, intervals, max_samples):
        split_segments = []
        for start, end in intervals:
            if (end - start) > max_samples:
                for i in range(start, end, max_samples):
                    split_segments.append((i, min(i + max_samples, end)))
            else:
                split_segments.append((start, end))
        return split_segments

    # Apply max length split
    final_intervals = split_long_segments(y, non_silent_intervals, max_samples)

    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    # Save extracted audio segments
    for i, (start, end) in enumerate(final_intervals):
        print(start / sr, end / sr)
        chunk = y[start:end]
        soundfile.write(f"{dir_path}/chunk_{i}.wav", chunk, sr)

    print(f"Total {len(final_intervals)} chunks saved.")


def _conversion_gv_to_json(midi_path, dir_path):
    # dir_path = "C:/Users/chans/repo/dataset/다화자 가창 데이터 json"
    # dir_path = "d:/dataset/다화자 가창 데이터 json"
    if os.path.exists(pathlib.Path(dir_path) / midi_path.name):
        return
    ma = midia.MidiAnalyzer(midi_path, convert_1_to_0=True)
    ma.split_space_note(remove_silence_threshold=0.3)
    ma.quantization(unit="32")
    ma.to_json(dir_path=dir_path)


def conversion_gv_to_json(data_path, json_path):
    # data_path = pathlib.Path(
    #     "C:/Users/chans/repo/dataset/004.다화자 가창 데이터"
    # )
    # data_path = pathlib.Path("d:/dataset/004.다화자 가창 데이터")
    # json_path = "d:/dataset/다화자 가창 데이터 json"
    data_path = pathlib.Path(data_path)
    with mp.Pool(mp.cpu_count()) as p:
        samples = list(data_path.rglob("*.mid"))
        args = zip(samples, (json_path for _ in range(len(samples))))
        p.starmap(_conversion_gv_to_json, args)


def verify_json_wav(data_path, json_path):
    sys.stdout.reconfigure(encoding="utf-8")  # printing encoding
    data_path = pathlib.Path(data_path)
    json_path = pathlib.Path(json_path)

    wav_set = list(sorted(data_path.rglob("*.wav"), key=lambda x: x.stem))
    json_set = list(sorted(json_path.rglob("*.json"), key=lambda x: x.stem))
    for wav_path, json_path in zip(wav_set, json_set):
        if wav_path.stem != json_path.stem:
            raise ValueError


def _save_splitted_json(json_path, output_path):
    # dir_path = pathlib.Path(
    #     "C:/Users/chans/repo/dataset/다화자 가창 데이터 json_splitted"
    # )
    # dir_path = pathlib.Path("d:/dataset/다화자 가창 데이터 json_splitted")
    output_path = pathlib.Path(output_path)
    chunks = midia.split_json_by_slience(json_path)
    if output_path is None:
        output_path = Path("")
    else:
        output_path = Path(output_path)
        output_path.mkdir(exist_ok=True, parents=True)
    file_path = output_path / json_path.name
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=4, ensure_ascii=False)


def save_splitted_json(json_path, output_path):
    # json_path = pathlib.Path(
    #     "C:/Users/chans/repo/dataset/다화자 가창 데이터 json"
    # )
    # json_path = pathlib.Path("d:/dataset/다화자 가창 데이터 json")
    json_path = pathlib.Path(json_path)
    # output_path = pathlib.Path(
    #     "C:/Users/chans/repo/dataset/다화자 가창 데이터 json_splitted"
    # )
    # for json_path in json_path.rglob("*.json"):
    #     chunks = midia.split_json_by_slience(json_path)
    #     if output_path is None:
    #         output_path = Path("")
    #     else:
    #         output_path = Path(output_path)
    #         output_path.mkdir(exist_ok=True, parents=True)
    #     file_path = output_path / json_path.name
    #     with open(file_path, "w", encoding="utf-8") as f:
    #         json.dump(chunks, f, indent=4, ensure_ascii=False)
    with mp.Pool(mp.cpu_count()) as p:
        samples = list(json_path.rglob("*.json"))
        args = zip(samples, (output_path for _ in range(len(samples))))
        p.starmap(_save_splitted_json, args)


def split_audio():
    audio_path = pathlib.Path(
        "C:/Users/chans/repo/dataset/004.다화자 가창 데이터"
    )
    json_path = pathlib.Path(
        "C:/Users/chans/repo/dataset/다화자 가창 데이터 json_splitted"
    )
    audio_path = pathlib.Path("d:/dataset/004.다화자 가창 데이터")
    json_path = pathlib.Path("d:/dataset/다화자 가창 데이터 json_splitted")
    samples = zip(
        sorted(audio_path.rglob("*.wav"), key=lambda x: x.stem),
        sorted(json_path.rglob("*.json"), key=lambda x: x.stem),
    )
    mids = list(sorted(audio_path.rglob("*.mid"), key=lambda x: x.stem))

    def _split_audio(y, sr, start_time, end_time, output_filename):
        start_sample = int(start_time * sr)  # Convert time to sample index
        end_sample = int(end_time * sr)

        chunk = y[start_sample:end_sample]  # Extract the segment
        soundfile.write(output_filename, chunk, sr)  # Save as WAV file

    for wav_path, json_path in samples:
        if wav_path.stem != json_path.stem:
            print(wav_path, json_path)
        with open(json_path, "r", encoding="utf-8") as f:
            json_data = json.load(f)
        # rprint(json_data)
        y, sr = librosa.load(wav_path, sr=None)
        output_dir_path = "clips_json"
        if not os.path.exists(output_dir_path):
            os.makedirs(output_dir_path)
        # for i, chunk in enumerate(json_data):
        #     _split_audio(
        #         y,
        #         sr,
        #         start_time=chunk["chunk_info"]["start_time"],
        #         end_time=chunk["chunk_info"]["end_time"],
        #         output_filename=f"{output_dir_path}/{i}.wav",
        #     )
        break

    ma = midia.MidiAnalyzer(mids[0], convert_1_to_0=True)
    ma.split_space_note(remove_silence_threshold=0.3)
    ma.quantization(unit="32")
    ma.analysis(
        track_bound=None,
        track_list=None,
        blind_note_info=True,
        blind_lyric=False,
    )
    print(wav_path)
    print(json_path)


def _singer_id(filename):
    sid = re.findall(r"s\d\d", filename)[0]
    return int(sid[1:]) + 26


def _split_audio(y, sr, start_time, end_time, output_filename):
    start_sample = int(start_time * sr)  # Convert time to sample index
    end_sample = int(end_time * sr)

    chunk = y[start_sample:end_sample]  # Extract the segment
    soundfile.write(output_filename, chunk, sr)  # Save as WAV file


def _preprocess_dataset(
    wav_path,
    json_path,
    pitch_dir_path,
    duration_dir_path,
    clips_dir_path,
    sampling_rate,
    hop_length,
):
    g2p = G2p()
    if wav_path.stem != json_path.stem:
        raise ValueError
    filename = wav_path.stem
    with open(json_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    metadata = ""
    y, sr = librosa.load(wav_path, sr=None)
    for i, chunk in enumerate(json_data):
        subfilename = f"{filename}_{i:02}"
        lyric = "".join([item["lyric"] for item in chunk["chunk"]])
        lyric = " ".join([g2p(x) for x in lyric.split()])
        metadata += f"{subfilename}|{lyric}|{_singer_id(filename)}|11|SV\n"

        np.save(
            f"{pitch_dir_path}/{subfilename}.npy",
            np.array([item["pitch"] for item in chunk["chunk"]]),
        )

        note_duration_frame = midia.duration_secs_to_frames(
            np.array([item["length"] for item in chunk["chunk"]]),
            sampling_rate,
            hop_length,
        )
        np.save(f"{duration_dir_path}/{subfilename}.npy", note_duration_frame)

        _split_audio(
            y,
            sr,
            start_time=chunk["chunk_info"]["start_time"],
            end_time=chunk["chunk_info"]["end_time"],
            output_filename=f"{clips_dir_path}/{subfilename}.wav",
        )
    return metadata


def preprocess_dataset(
    data_path,
    json_path,
    output_dir_path,
    sample_num=None,
    sampling_rate=22050,
    hop_length=256,
):
    verify_json_wav(data_path, json_path)

    wav_set = sorted(
        pathlib.Path(data_path).rglob("*.wav"), key=lambda x: x.stem
    )
    json_set = sorted(
        pathlib.Path(json_path).rglob("*.json"), key=lambda x: x.stem
    )

    dir_path = Path(output_dir_path)
    dir_path.mkdir(exist_ok=True, parents=True)

    pitch_dir_path = f"{output_dir_path}/note_pitch"
    pitch_dir_path = Path(pitch_dir_path)
    pitch_dir_path.mkdir(exist_ok=True, parents=True)

    duration_dir_path = f"{output_dir_path}/note_duration"
    duration_dir_path = Path(duration_dir_path)
    duration_dir_path.mkdir(exist_ok=True, parents=True)

    clips_dir_path = f"{output_dir_path}/audio"
    clips_dir_path = Path(clips_dir_path)
    clips_dir_path.mkdir(exist_ok=True, parents=True)

    # g2p = G2p()
    # for wav_path, json_path in zip(wav_set, json_set):
    #     if wav_path.stem != json_path.stem:
    #         raise ValueError
    #     filename = wav_path.stem
    #     with open(json_path, "r", encoding="utf-8") as f:
    #         json_data = json.load(f)

    #     for i, chunk in enumerate(json_data):
    #         lyric = "".join([item["lyric"] for item in chunk["chunk"]])
    #         lyric = " ".join([g2p(x) for x in lyric.split()])
    #         with open(
    #             f"{output_dir_path}/metadata.txt", "a", encoding="utf-8"
    #         ) as f:
    #             f.write(
    #                 f"{filename}_{i}|{lyric}|{_singer_id(filename)}|28|SV\n"
    #             )

    #     for i, chunk in enumerate(json_data):
    #         np.save(
    #             f"{pitch_dir_path}/{filename}_{i}.npy",
    #             np.array([item["pitch"] for item in chunk["chunk"]]),
    #         )

    #     sampling_rate = 22050
    #     hop_length = 256
    #     for i, chunk in enumerate(json_data):
    #         note_duration_frame = midia.duration_secs_to_frames(
    #             np.array([item["length"] for item in chunk["chunk"]]),
    #             sampling_rate,
    #             hop_length,
    #         )
    #         np.save(
    #             f"{duration_dir_path}/{filename}_{i}.npy", note_duration_frame
    #         )

    #     y, sr = librosa.load(wav_path, sr=None)
    #     for i, chunk in enumerate(json_data):
    #         _split_audio(
    #             y,
    #             sr,
    #             start_time=chunk["chunk_info"]["start_time"],
    #             end_time=chunk["chunk_info"]["end_time"],
    #             output_filename=f"{clips_dir_path}/{filename}_{i}.wav",
    #         )

    #     break

    args = zip(
        wav_set,
        json_set,
        (pitch_dir_path for _ in range(len(wav_set))),
        (duration_dir_path for _ in range(len(wav_set))),
        (clips_dir_path for _ in range(len(wav_set))),
        (sampling_rate for _ in range(len(wav_set))),
        (hop_length for _ in range(len(wav_set))),
    )
    with mp.Pool(mp.cpu_count()) as p:
        if sample_num:
            args = list(args)
            if sample_num < len(args):
                args = random.sample(args, k=sample_num)
        metadata_list = p.starmap(_preprocess_dataset, args)
        with open(
            f"{output_dir_path}/metadata.txt", "w", encoding="utf-8"
        ) as f:
            f.write("".join(metadata_list))


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

    # test_slice(samples[2]["wav"], "clips")
    # test_trim_slice(samples[2]["wav"], "clips_trimmed")
    # mid_path = "d:/dataset/004.다화자 가창 데이터/01.데이터/1.Training/라벨링데이터/01.발라드R&B/B. 여성/01. 20대/가창자_s01/ba_06799_+0_a_s01_f_02.mid"
    # mid_path = "d:/dataset/004.다화자 가창 데이터/01.데이터/2.Validation/라벨링데이터/02.록팝/A. 남성/01. 20대/가창자_s02/ro_01274_+0_a_s02_m_02.mid"
    # mid_path = "D:/dataset/004.다화자 가창 데이터/01.데이터/2.Validation/라벨링데이터/02.록팝/A. 남성/03. 40대 이상/가창자_s18/ro_03036_+0_s_s18_m_04.mid"
    # mid_path = "D:/dataset/004.다화자 가창 데이터/01.데이터/2.Validation/라벨링데이터/01.발라드R&B/B. 여성/01. 20대/가창자_s01/ba_00118_+0_a_s01_f_02.mid"
    # mid_path = "D:/dataset/004.다화자 가창 데이터/01.데이터/1.Training/라벨링데이터/01.발라드R&B/A. 남성/02. 30대/가창자_s11/ba_24340_+0_s_s11_m_03.mid"
    # ma = midia.MidiAnalyzer(samples[3]["mid"], convert_1_to_0=True)
    # ma = midia.MidiAnalyzer(mid_path, convert_1_to_0=True)
    # ma.split_space_note(remove_silence_threshold=0.3)
    # ma.quantization(unit="32")
    # ma.analysis(
    #     track_bound=None,
    #     track_list=None,
    #     blind_note_info=True,
    #     blind_lyric=False,
    # )
    # ma.to_json(dir_path="json")
    # test_slice_midi(samples[2]["wav"], samples[2]["mid"])
    # test_clips_duration("clips_prev")
    # test_clips_duration("clips")
    # test_split_librosa(samples[2]["wav"], "clips_librosa")
    # ma.slice()
    # ma.analysis(track_bound=30, track_list=["Melody"])
    # mid_path = "test_q2_midi.mid"
    # mid_path = "test_q_ff_merged_midi.mid"
    # mid_path = "test_qs_midi.mid"
    # ma.mid.save(mid_path)
    # ma = midia.MidiAnalyzer(mid_path, convert_1_to_0=True)
    # ma.analysis(track_bound=None, track_list=None, blind_note_info=True)
    # print(list(Note)[-1].value.beat, list(Note)[-1].value.beat / 2)
    # midia.midi2wav(ma.mid, "test.wav", 62)
    # test_split_audio_pydub(samples[2]["wav"], "clips_pydub")

    # t1 = mido.MidiFile(mid_path).tracks[1]
    # t2 = mido.MidiFile(samples[2]["mid"]).tracks[1]
    # midia.compare_track(t1, t2)

    # test_custom_msg()

    # rprint(mido.Message("note_on", note=0, velocity=0, time=0))

    # def beat_iter(i):
    #     beat = 4 * (3 / 4) ** ((i + 1) // 2) * (2 / 3) ** (i // 2)
    #     return round(beat, 4)
    # ma.analysis()

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

    # idx = 0
    # json_path = pathlib.Path("d:/dataset/json")
    # json_path = pathlib.Path(
    #     "C:/Users/chans/repo/dataset/다화자 가창 데이터 json"
    # )
    # mid_path = pathlib.Path("d:/dataset/004.다화자 가창 데이터")
    # mid_path = pathlib.Path(
    #     "C:/Users/chans/repo/dataset/004.다화자 가창 데이터"
    # )
    # for i, json_path in enumerate(
    #     sorted(json_path.rglob("*.json"), key=lambda x: x.stem)
    # ):
    #     if i == idx:
    #         chunks = midia.split_json_by_slience(json_path)
    #         rprint(chunks)
    #         print(json_path)
    #         break

    # save_splitted_json()
    # split_audio()

    # for i, mid_path in enumerate(
    #     sorted(mid_path.rglob("*.mid"), key=lambda x: x.stem)
    # ):
    #     if i == idx:
    #         print(mid_path)
    #         ma = midia.MidiAnalyzer(mid_path, convert_1_to_0=True)
    #         ma.split_space_note(remove_silence_threshold=0.3)
    #         ma.quantization(unit="32")
    #         ma.analysis(
    #             track_bound=None,
    #             track_list=None,
    #             blind_note_info=True,
    #             blind_lyric=False,
    #         )
    #         break

    # sys.stdout.reconfigure(encoding="utf-8")  # printing encoding
    # for p1, p2 in zip(
    #     sorted(data_path.rglob("*.wav")), sorted(data_path.rglob("*.mid"))
    # ):
    #     print(p1)
    #     print(p2)
    #     print()

    data_path = "d:/dataset/004.다화자 가창 데이터"
    json_path = "d:/dataset/다화자 가창 데이터 json"
    # conversion_gv_to_json(data_path, json_path)
    # verify_json_wav(data_path, json_path)

    json_splitted_path = "d:/dataset/다화자 가창 데이터 json_splitted"
    # save_splitted_json(json_path, json_splitted_path)
    # verify_json_wav(data_path, json_splitted_path)

    output_dir_path = "d:/dataset/다화자 가창 데이터 preprocessed"
    preprocess_dataset(
        data_path,
        json_splitted_path,
        output_dir_path,
        sample_num=None,
        sampling_rate=22050,
        hop_length=256,
    )
