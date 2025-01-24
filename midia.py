"""midia"""

import sys
from collections import defaultdict
import string

import pretty_midi

import mido as md
from mido.midifiles.meta import (
    MetaSpec,
    add_meta_spec,
)
from mido import MidiFile, Message, MetaMessage

from pydub import AudioSegment
from pydub.generators import Sine
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

from note import (
    Note,
    Rest,
    COLOR,
    DEFAULT_TEMPO,
    DEFAULT_TIME_SIGNATURE,
    DEFAULT_PPQN,
)


class MetaSpec_rest(MetaSpec):
    type_byte = 0xA0
    attributes = []
    defaults = []


class MetaSpec_measure(MetaSpec):
    type_byte = 0xA1
    attributes = ["index"]
    defaults = [1]


add_meta_spec(MetaSpec_rest)
add_meta_spec(MetaSpec_measure)


def tick2beat(tick, ppqn):
    """tick2beat"""
    return tick / ppqn


def beat2tick(beat, ppqn):
    """tick2beat"""
    return int(beat * ppqn)


def midfile2wav(midi_path, wav_path, bpm):
    """midfile2wav(midi_path, wav_path, bpm)"""
    mid = MidiFile(midi_path)
    midi2wav(mid, wav_path, bpm)


def midi2wav(mid_obj, wav_path, bpm):
    """Function to convert midi to wav
    ref: https://gist.github.com/jiaaro/339df443b005e12d6c2a"""

    def note_to_freq(note, concert_A=440.0):
        """
        http://en.wikipedia.org/wiki/MIDI_Tuning_Standard#Frequency_values
        """
        return (2.0 ** ((note - 69) / 12.0)) * concert_A

    output = AudioSegment.silent(mid_obj.length * 1000.0)

    def ticks_to_ms(ticks):
        tick_ms = (60000.0 / bpm) / mid_obj.ticks_per_beat
        return ticks * tick_ms

    for track in mid_obj.tracks:
        # position of rendering in ms
        current_pos = 0.0
        current_notes = defaultdict(dict)

        for msg in track:
            current_pos += ticks_to_ms(msg.time)
            if msg.type == "note_on":
                current_notes[msg.channel][msg.note] = (current_pos, msg)
            if msg.type == "note_off":
                start_pos, _ = current_notes[msg.channel].pop(msg.note)
                duration = current_pos - start_pos
                signal_generator = Sine(note_to_freq(msg.note))
                rendered = (
                    signal_generator.to_audio_segment(
                        duration=duration - 50, volume=-20
                    )
                    .fade_out(100)
                    .fade_in(30)
                )
                output = output.overlay(rendered, start_pos)
    output.export(wav_path, format="wav")


class MidiAnalyzer:
    """Class for analysis midi file"""

    def __init__(
        self,
        midi_path,
        convert_1_to_0=False,
        encoding="utf-8",
    ):
        sys.stdout.reconfigure(encoding="utf-8")  # printing encoding
        self.mid = MidiFile(midi_path)
        self.ppqn = self.mid.ticks_per_beat

        if self.mid.type == 1 and convert_1_to_0:
            self.mid.tracks = [md.merge_tracks(self.mid.tracks)]

        self.track_analyzers = [
            MidiTrackAnalyzer(track, self.ppqn, encoding=encoding)
            for track in self.mid.tracks
        ]

    def quantization(self):
        """quantization"""
        for track_analyzer in self.track_analyzers:
            track_analyzer.quantization()

    def analysis(
        self,
        track_bound=None,
        blind_note=False,
        blind_time=False,
        blind_lyric=True,
        track_list=None,
    ):
        """method to analysis"""

        if track_bound is None:
            track_bound = float("inf")
        # meta information of midi file
        header_style = "black on white blink"
        header_info = "\n".join(
            [
                f"[{header_style}]mid file type: {self.mid.type}",
                f"ticks per beat: {self.ppqn}",
                f"total duration: {self.mid.length}[/{header_style}]",
            ]
        )
        header_panel = Panel(
            header_info,
            title="[MIDI File Header]",
            subtitle=f"{self.mid.filename}",
            style=f"{header_style}",
            border_style=f"{header_style}",
        )
        rprint(header_panel)

        quantization_error, quantization_mean = 0, 0
        for i, track_analyzer in enumerate(self.track_analyzers):
            console = Console()
            console.rule(
                "[#ffffff on #4707a8]" + f'Track {i}: "{track_analyzer.name}"'
                f"[/#ffffff on #4707a8]",
                style="#ffffff on #4707a8",
            )
            if track_list is None or track_analyzer.name in track_list:
                _quantization_error, _quantization_mean = (
                    track_analyzer.analysis(
                        track_bound=track_bound,
                        blind_note=blind_note,
                        blind_time=blind_time,
                        blind_lyric=blind_lyric,
                    )
                )
                quantization_error += _quantization_error
                quantization_mean += _quantization_mean

        if track_list is None or track_list:
            if track_list is None:
                mean_denominator = len(self.mid.tracks)
            else:
                mean_denominator = len(track_list)
            total_q_mean = quantization_mean / mean_denominator
            print()
            rprint(
                "Total quantization error/mean of track error mean: "
                + f"{float(quantization_error):.5}/"
                + f"{total_q_mean:.5}"
            )


class MidiTrackAnalyzer:
    """Class for analysis midi track"""

    def __init__(self, track, ppqn, encoding="utf-8"):
        self.track = track
        self.name = track.name
        self.ppqn = ppqn
        self.encoding = encoding
        self._init_values()

    def _init_values(self):
        self.time_signature = DEFAULT_TIME_SIGNATURE
        self.tempo = DEFAULT_TEMPO
        self.length = 0

    def _get_quantized_note(self, msg, beat):
        result = []
        if msg.type == "note_on":
            result.append(MetaMessage("rest", time=beat2tick(beat, self.ppqn)))
        elif msg.type == "note_off":
            q_msg = msg.copy()
            q_msg.time = beat2tick(beat, self.ppqn)
            _msg_on = Message(
                "note_on", note=msg.note, velocity=msg.velocity, time=0
            )
            result.append(q_msg)
            result.append(_msg_on)
        return result

    def _quantization_one(self, msg, space):
        beat_idx = 0
        note_list = list(Note)
        q_time = None
        while beat_idx < len(Note):
            beat = tick2beat(msg.time, self.ppqn)
            q_beat = note_list[beat_idx].value.beat
            q_time = beat2tick(q_beat, self.ppqn)
            if q_beat > space:
                beat_idx += 2
                continue
            if beat > q_beat:
                q_msg = msg.copy()
                q_msg.time = q_time
                msg.time -= q_time
                return (
                    self._get_quantized_note(msg, q_beat),  # quantized note
                    q_time,  # quantized time
                )
            elif beat == q_beat:
                return (
                    None,  # original msg is already quantized
                    q_time,
                )
            elif beat < q_beat:
                beat_idx += 2
        return (
            msg,  # quantization failed
            None,
        )

    def _quantization(self, msg):
        quantized_note = []
        beat_idx = 0
        note_list = list(Note)
        while beat_idx < len(Note):
            beat = tick2beat(msg.time, self.ppqn)
            q_beat = note_list[beat_idx].value.beat
            if beat > q_beat:
                q_msg = msg.copy()
                q_msg.time = beat2tick(q_beat, self.ppqn)
                quantized_note += self._get_quantized_note(msg, q_beat)
                msg.time -= beat2tick(q_beat, self.ppqn)
            elif beat == q_beat:
                break
            else:
                beat_idx += 2  # 반음표를 고려하지 않음.

        quantized_note.append(msg)
        return quantized_note

    def quantization(self):
        """quantization
        박자가 4(온음표) 보다 크다 → 4보다 작아질 때 까지 4박을 독립시킨다.
        박자가 4보다 작다.
            박자가 2(2분음표)보다 크다 	→ 2박을 독립시킨다.
            박자가 1(4분음표)보다 크다 → 1박을 독립시킨다.
            박자가 0.5(8분음표)보다 크다 → 0.5박을 독립시킨다.
            박자가 0.25(16분음표)보다 크다 → 0.25박을 독립시킨다.
            박자가 0.125(32분음표)보다 크다 → 0.125박을 독립시킨다.
        박이 32분음표보다 작으면?

        기본적으로, 4/4박자표에서 정의된 노래라면, 4박자씩 마디를 채워나가게 된다.
        따라서 이 노래를 부른 음원을 분석하면 노트와 가사의 박자를 계속 가져와서 4박자 마디를
        채워나갈 수 있다. 만약 4박자 마디가 3.9 박이 채워졌는데, 그 다음 노트가 1.2박이면
        그 노트의 0.1 박을 가져와서 4박자 마디 4.0박을 채우게 되고, 그 다음 노트의 1.1박을
        그 다음 마디 4박에 채워야지. 근데 만약 4박자 마디가 3.99 박이 채워져서 0.01박을
        채워야 한다면, 32분음표(0.125박)보다 작은 박을 필요로 하는 건데, 최소단위를 32분음표라고
        가정했으므로 이건 존재하지 않는 박(0.01박)인 것이다.

        32분음표보다 작으면 존재하지 않는 박이고, 존재하지 않는 박이면 존재하지 않는다는 이유로
        삭제해야 함. 그런데 삭제하는 것까지는 좋은데, 이런 식으로 1/32음표보다 작은 박들을 모두
        삭제를 했다가는 에러가 누적되면서 악보와 노래의 싱크가 틀어지게 된다.
        따라서 삭제하되, 이 1/32음표보다 작은 박을 이전 노트나 다음 음표의 박으로 병합해준다.

        그러니까 기본적으로 32분음표(0.125박) 보다 작은 박은 존재하지 않는다고 가정하는 것.
        따라서 만약 0.125박 보다 작은 박이 발견되면
        이것은 가수가 정박에 부르지 않았기에 발생한 잔차로 해석.
        이 잔차가 32분음표보다 작기 때문에 실제로 존재하는 박이 아니며, 그러므로 이전 박이나 다음 박으로
        병합시키거나, 아예 삭제하고 이전 박이나 다음 박을 보충해주어야 함.

        박이 32분음표보다 작은 경우를 2가지로 해석할 수 있다.
        양의 경우: 음표보다 32분음표보다 작은 경우. ex) 노트의 박이 0.01 인 경우.
        음의 경우: 4박자 마디가 다 채워지도록 필요로하는 박이 32분음표 보다 작은 경우
        ex) 4박자 마디가 3.99박이 채워진 경우.

        0박의 존재를 가정해야 함. 1/32음표보다 작은 박이 발견될 경우 그 박이 실제로는 0.125박
        인데 가수가 잘못 불러서 0.125박보다 작아졌는지, 그 박이 실제로는 0박(즉, 없는 박)인데
        가수가 잘못 불러서 다른 박이 삐져나온 건지, 판단해야 하기 때문. 이를 위하여 이 박이 0.125박에
        가까운지, 0박에 가까운지 확률을 계산할 수 있어야 하고, 에러를 최소화할 수 있는 방향으로
        박을 결정해야 함.


        --> 알고리즘을 구현 했는데, 실제 MIDI 를 음원으로 합성하니까
        rest 라는 메시지가 음으로 합성되지 않는다. 근데 이건 당연한거고, custom 메시지이므로.
        음들이 quantization 된 게 음원을 합성하는 관점에서는 너무 과하게 분할된 것이다.
        그래서 quantization 을 한 이후에 실제로 음원을 합성하는 용도로,
        사운드 유닛들을 최대한 다시 합쳐주어야 한다.
        """

        modified_track = []
        note_queue = {}

        # for msg in self.track:
        #     if msg.type == "note_on":
        #         mma = MidiMessageAnalyzer_note_on(
        #             msg=msg, note_queue=note_queue
        #         )
        #         mma.alloc_note(msg.note)
        #         modified_track += self._quantization(msg)
        #     elif msg.type == "note_off":
        #         mma = MidiMessageAnalyzer_note_off(
        #             msg=msg, note_queue=note_queue
        #         )
        #         mma.free_note(msg.note)
        #         modified_track += self._quantization(msg)
        #     elif msg.type == "lyrics":
        #         modified_track.append(msg)
        #     else:
        #         modified_track.append(msg)

        i = 0
        space = 4
        error = 0
        q_note, q_time = None, None
        while i < len(self.track):
            if self.track[i].type == "note_on":
                if error:
                    self.track[i].time += error
                    error = 0

                # mma = MidiMessageAnalyzer_note_on(
                #     msg=self.track[i], note_queue=note_queue
                # )
                # mma.alloc_note(self.track[i].note)
                # q_note, q_time = self._quantization_one(self.track[i], space)
                # if q_time is not None:
                #     space -= tick2beat(q_time, self.ppqn)
                # modified_track.append(self.track[i])
                q_note, q_time = self._quantization_one(self.track[i], space)
            elif self.track[i].type == "note_off":
                if error:
                    self.track[i].time += error
                    error = 0
                # mma = MidiMessageAnalyzer_note_off(
                #     msg=self.track[i], note_queue=note_queue
                # )
                # mma.free_note(self.track[i].note)
                q_note, q_time = self._quantization_one(self.track[i], space)
                # if q_time is not None:
                #     space -= tick2beat(q_time, self.ppqn)
                # modified_track.append(self.track[i])
            elif self.track[i].type == "lyrics":
                modified_track.append(self.track[i])
                i += 1
                continue
            else:
                modified_track.append(self.track[i])
                i += 1
                continue

            if q_note is not None and q_time is not None:
                # quantized note
                modified_track += q_note
                space -= tick2beat(q_time, self.ppqn)
            elif q_note is None and q_time is not None:
                # original msg is already quantized
                modified_track.append(self.track[i])
                space -= tick2beat(q_time, self.ppqn)
                i += 1
            elif q_note is not None and q_time is None:
                # quantization failed
                # (0.0625, 0] 에 포함되면 0 로 취급하고(실제 박을 더 짧은 박(0)으로 간주했으므로 그 다음 박에 + 에러를 포워딩해서 박을 보상해줌.), 에러 포워딩
                # (0.125, 0.0625] 에 포함되면 0.125 로 취급하고(이러면 실제 박을 더 긴 박으로 간주했으므로, 그 다음 박으로 - 에러를 포워딩해서 박자를 보상해줌), 에러 포워딩
                # modified_track.append(self.track[i])
                beat = tick2beat(self.track[i].time, self.ppqn)
                if beat < 0.0625:
                    error = q_note.time - 0
                    q_note.time = 0
                    modified_track.append(q_note)
                elif beat < 0.125:
                    error = q_note.time - beat2tick(0.125, self.ppqn)
                    q_note.time = beat2tick(0.125, self.ppqn)
                    modified_track.append(q_note)
                else:
                    raise ValueError
                i += 1
                # space -= q_time
            # else:
            #     modified_track.append(msg)
            #     space -= q_time
            if space == 0:
                if self.track[i].type == "note_off":
                    # modified_track.append(MetaMessage("measure"))
                    modified_track = (
                        modified_track[:-1]
                        + [MetaMessage("measure")]
                        + [modified_track[-1]]
                    )
                elif self.track[i].type == "note_on":
                    modified_track.append(MetaMessage("measure"))
                space = 4
                # modified_track.append()
            elif space < 0:
                raise ValueError

        self.track = modified_track

    def print_note_num(self, note_num):
        """print_note_num"""
        color = "color(240)" if note_num == 0 else "color(47)"
        bpm = round(
            md.tempo2bpm(self.tempo, time_signature=self.time_signature)
        )
        info = f"[bold {color}]Total item num of BPM({bpm}): " + f"{note_num}"
        Console(width=55).rule(info, style=f"{color}")

    def analysis(
        self,
        track_bound=None,
        blind_note=False,
        blind_time=False,
        blind_lyric=True,
    ):
        """analysis track"""
        self._init_values()
        quantization_error = 0
        quantization_num = 0
        note_address = 0
        q_error = 0
        note_num = 0
        first_tempo = True
        note_queue = {}
        if track_bound is None:
            track_bound = float("inf")
        lyric = ""
        for i, msg in enumerate(self.track):
            if i > track_bound:
                break
            self.length += md.tick2second(
                msg.time,
                ticks_per_beat=self.ppqn,
                tempo=self.tempo,
            )
            msg_kwarg = {
                "msg": msg,
                "ppqn": self.ppqn,
                "tempo": self.tempo,
                "idx": i,
                "length": self.length,
            }
            if msg.type == "note_on":
                result, note_address, q_error = MidiMessageAnalyzer_note_on(
                    **msg_kwarg, note_queue=note_queue
                ).analysis(blind_time=blind_time, blind_note=blind_note)
            elif msg.type == "note_off":
                result, q_error = MidiMessageAnalyzer_note_off(
                    **msg_kwarg, note_queue=note_queue
                ).analysis(blind_time=blind_time, blind_note=blind_note)
            elif msg.type == "rest":
                result, q_error = MidiMessageAnalyzer_rest(
                    **msg_kwarg, note_queue=note_queue
                ).analysis(blind_time=blind_time, blind_note=blind_note)
            elif msg.type == "lyrics":
                result, _lyric, q_error = MidiMessageAnalyzer_lyrics(
                    **msg_kwarg,
                    msg_next=self.track[i + 1],
                    note_address=note_address,
                    note_queue=note_queue,
                ).analysis(blind_time=blind_time, blind_note=blind_note)
                lyric += _lyric
            elif msg.type == "measure":
                result = MidiMessageAnalyzer_measure().print()
            elif msg.type == "text" or msg.type == "track_name":
                result = MidiMessageAnalyzer_text(
                    **msg_kwarg,
                    encoding=self.encoding,
                ).analysis(blind_time=blind_time)
            elif msg.type == "set_tempo":
                if not first_tempo:
                    self.print_note_num(note_num)
                first_tempo = False
                result, self.tempo = MidiMessageAnalyzer_set_tempo(
                    **msg_kwarg,
                    time_signature=self.time_signature,
                ).analysis(blind_time=blind_time)
            elif msg.type == "end_of_track":
                self.print_note_num(note_num)
                result = MidiMessageAnalyzer_end_of_track(
                    **msg_kwarg
                ).analysis(blind_time=blind_time)
            elif msg.type == "key_signature":
                result = MidiMessageAnalyzer_key_signature(
                    **msg_kwarg
                ).analysis(blind_time=blind_time)
            elif msg.type == "time_signature":
                result, self.time_signature = (
                    MidiMessageAnalyzer_time_signature(
                        **msg_kwarg
                    ).analysis(blind_time=blind_time)
                )
            else:
                result = MidiMessageAnalyzer(**msg_kwarg).analysis(
                    blind_time=blind_time
                )

            if result:
                rprint(result)

            if msg.type in ["note_on", "note_off", "lyrics"]:
                quantization_error += q_error
                quantization_num += 1 if q_error else 0
                note_num += 1

        q_error_mean = 0
        rprint(f"Track lyric encode: {self.encoding}")
        rprint(f"Track total time: {self.length}")
        if quantization_num != 0:
            q_error_mean = quantization_error / quantization_num
            rprint(
                "Track total quantization error/mean: "
                + f"{quantization_error:.5}/"
                + f"{q_error_mean: .5}"
            )
        if not blind_lyric:
            print(f'LYRIC: "{lyric}"')
        return quantization_error, q_error_mean


class MidiMessageAnalyzer:
    """MidiMessageAnalyzer"""

    def __init__(
        self,
        msg,
        ppqn=DEFAULT_PPQN,
        tempo=DEFAULT_TEMPO,
        idx=0,
        length=0,
    ):
        self.msg = msg
        self.ppqn = ppqn
        self.tempo = tempo
        self.idx_info = f"[color(244)]{idx:4}[/color(244)]"
        self.length = length

    def info_type(self):
        """info_type"""
        return f"[black on white]\\[{self.msg.type}][/black on white]"

    def info_time(self):
        """time_info"""
        if self.msg.time:
            main_color = "#ffffff"
            sub_color = "white"
            time = md.tick2second(
                self.msg.time,
                ticks_per_beat=self.ppqn,
                tempo=self.tempo,
            )
            return " ".join(
                [
                    f"[{main_color}]{time:4.2f}[/{main_color}]"
                    + f"[{sub_color}]/{self.length:6.2f}[/{sub_color}]",
                    f"[{sub_color}]time=[/{sub_color}]"
                    + f"[{main_color}]{self.msg.time:<3}[/{main_color}]",
                ]
            )
        else:
            return ""

    def result(self, head="", body="", blind_time=False):
        """print strings"""
        time_info = "" if blind_time else self.info_time()
        _result = [self.idx_info, head, time_info, body]
        return " ".join([s for s in _result if s])

    def analysis(self, blind_time=False):
        """analysis"""
        return self.result(
            head=self.info_type(),
            body=f"[color(250)]{self.msg}[/color(250)]",
            blind_time=blind_time,
        )


class MidiMessageAnalyzer_set_tempo(MidiMessageAnalyzer):
    """MidiMessageAnalyzer_set_tempo"""

    def __init__(
        self,
        msg,
        ppqn=DEFAULT_PPQN,
        tempo=DEFAULT_TEMPO,
        idx=0,
        length=0,
        time_signature=DEFAULT_TIME_SIGNATURE,
    ):
        super().__init__(msg, ppqn, tempo=tempo, idx=idx, length=length)
        self.time_signature = time_signature

    def analysis(self, blind_time=False):
        bpm = round(
            md.tempo2bpm(self.msg.tempo, time_signature=self.time_signature)
        )
        result = self.result(
            head=self.info_type(),
            body=f"[white]BPM=[/white][color(190)]{bpm}[/color(190)]",
            blind_time=blind_time,
        )
        return result, self.msg.tempo


class MidiMessageAnalyzer_key_signature(MidiMessageAnalyzer):
    """MidiMessageAnalyzer_key_signature"""

    def analysis(self, blind_time=False):
        return self.result(
            head=self.info_type(), body=self.msg.key, blind_time=blind_time
        )


class MidiMessageAnalyzer_end_of_track(MidiMessageAnalyzer):
    """MidiMessageAnalyzer_end_of_track"""

    def analysis(self, blind_time=False):
        return self.result(head=self.info_type(), blind_time=blind_time)


class MidiMessageAnalyzer_time_signature(MidiMessageAnalyzer):
    """MidiMessageAnalyzer_time_signature"""

    def analysis(self, blind_time=False):
        result = self.result(
            head=self.info_type(),
            body=f"{self.msg.numerator}/{self.msg.denominator}",
            blind_time=blind_time,
        )
        return result, (self.msg.numerator, self.msg.denominator)


class MidiMessageAnalyzer_measure(MidiMessageAnalyzer):
    """MidiMessageAnalyzer_measure"""

    idx = 1

    def __init__(self):
        pass

    @classmethod
    def print(cls):
        """print measure"""
        Console(width=50).rule(
            f"[#ffffff]𝄞 measure {cls.idx}[/#ffffff]",
            style="#ffffff",
            characters="=",
        )
        cls.idx += 1


class MidiMessageAnalyzer_text(MidiMessageAnalyzer):
    """MidiMessageAnalyzer_text"""

    def __init__(
        self,
        msg,
        ppqn=DEFAULT_PPQN,
        tempo=DEFAULT_TEMPO,
        idx=0,
        length=0,
        encoding="utf-8",
        encoding_alternative="cp949",
    ):
        super().__init__(msg, ppqn, tempo=tempo, idx=idx, length=length)
        self._init_encoding(
            encoding=encoding, encoding_alternative=encoding_alternative
        )

    def _init_encoding(self, encoding="utf-8", encoding_alternative="cp949"):
        self.encoded_text = self.msg.bin()[3:]
        self.encoding = self.determine_encoding(encoding, encoding_alternative)

    def determine_encoding(self, *encoding_list):
        """determine_encoding"""
        for encoding in encoding_list:
            try:
                self.encoded_text.decode(encoding)
            except UnicodeDecodeError:
                continue
            else:
                return encoding
        raise UnicodeDecodeError

    def analysis(self, blind_time=False):
        """analysis text"""
        text = self.encoded_text.decode(self.encoding).strip()
        return self.result(
            head=self.info_type(), body=text, blind_time=blind_time
        )


class MidiMessageAnalyzer_SoundUnit(MidiMessageAnalyzer):
    """MidiMessageAnalyzer_SoundUnit"""

    def __init__(
        self,
        msg,
        ppqn=DEFAULT_PPQN,
        tempo=DEFAULT_TEMPO,
        idx=0,
        length=0,
        note_queue=None,
    ):
        super().__init__(
            msg,
            ppqn,
            tempo=tempo,
            idx=idx,
            length=length,
        )
        if note_queue is None:
            self.note_queue = {}
        else:
            self.note_queue = note_queue

    def note_queue_find(self, value):
        """note_queue_find"""
        for k, v in self.note_queue.items():
            if v == value:
                return k
        return None

    def note_queue_alloc(self):
        """note_queue_alloc"""
        address = 0
        while True:
            try:
                self.note_queue[address]
                address += 1
            except KeyError:
                return address

    def quantization_min(self, tick, as_rest=False):
        """select minimum error"""
        if tick == 0:
            return None, None
        beat = tick2beat(tick, self.ppqn)
        min_error = float("inf")
        quantized_note = None
        note_enum = Rest if as_rest else Note
        for note in note_enum:
            error = note.value.beat - beat
            if abs(error) < min_error:
                min_error = error
                quantized_note = note.value
        return min_error, quantized_note

    def quantization_info(
        self, error, real_beat, quantized_note, quantization_color="color(85)"
    ):
        """info_quantization"""
        if error is None:
            return ""
        else:
            if error == 0:
                err_msg = ""
            else:
                err_msg = f"[#ff0000]-{float(real_beat):.3}={error}[/#ff0000]"
            return (
                f"[{quantization_color}]"
                + f"{quantized_note.symbol:2}{quantized_note.name_kor}"
                + f"[/{quantization_color}]"
                + f"[color(249)]{float(quantized_note.beat):.3}박[/color(249)]"
                + err_msg
            )

    def note_info(self, note):
        """note_info"""
        return f"{pretty_midi.note_number_to_name(note):>3}({note})"


class MidiMessageAnalyzer_note_on(MidiMessageAnalyzer_SoundUnit):
    """MidiMessageAnalyzer_note_on"""

    def alloc_note(self, note):
        """alloc_note"""
        note_address = self.note_queue_alloc()
        self.note_queue[note_address] = note
        return note_address

    def analysis(self, blind_time=False, blind_note=False):
        addr = self.alloc_note(self.msg.note)
        # addr = self.note_queue_alloc()
        # self.note_queue[addr] = self.msg.note

        error, quantized_note = self.quantization_min(
            self.msg.time, as_rest=True
        )
        info_quantization = ""
        quantization_error = 0
        if error is not None:
            quantization_error = abs(error)
            info_quantization = self.quantization_info(
                round(error, 3),
                tick2beat(self.msg.time, self.ppqn),
                quantized_note,
            )
        color = f"color({COLOR[addr % len(COLOR)]})"
        note_msg = f"[{color}]┌{self.note_info(self.msg.note)}┐[/{color}]"
        result = ""
        if not blind_note:
            result = self.result(
                head=note_msg, body=info_quantization, blind_time=blind_time
            )
        return result, addr, quantization_error


class MidiMessageAnalyzer_note_off(MidiMessageAnalyzer_SoundUnit):
    """MidiMessageAnalyzer_note_off"""

    def free_note(self, note):
        """alloc_note"""
        addr = self.note_queue_find(note)
        if addr is not None:
            del self.note_queue[addr]
        return addr

    def analysis(self, blind_time=False, blind_note=False):
        addr = self.free_note(self.msg.note)
        # addr = self.note_queue_find(self.msg.note)
        color = "white on red" if addr is None else f"color({COLOR[addr]})"
        # del self.note_queue[addr]
        info_note_off = f"[{color}]└{self.note_info(self.msg.note)}┘[/{color}]"

        error, quantized_note = self.quantization_min(
            self.msg.time, as_rest=True if addr is None else False
        )
        info_quantization = ""
        quantization_error = 0
        if error is not None:
            quantization_error = abs(error)
            info_quantization = self.quantization_info(
                round(error, 3),
                tick2beat(self.msg.time, self.ppqn),
                quantized_note,
            )
        result = ""
        if not blind_note:
            result = self.result(
                head=info_note_off,
                body=info_quantization,
                blind_time=blind_time,
            )

        return result, quantization_error


class MidiMessageAnalyzer_rest(MidiMessageAnalyzer_SoundUnit):
    """MidiMessageAnalyzer_rest"""

    def analysis(self, blind_time=False, blind_note=False):
        error, quantized_note = self.quantization_min(
            self.msg.time, as_rest=True
        )
        info_quantization = ""
        quantization_error = 0
        if error is not None:
            quantization_error = abs(error)
            info_quantization = self.quantization_info(
                round(error, 3),
                tick2beat(self.msg.time, self.ppqn),
                quantized_note,
            )
        result = ""
        info_rest = f"[black on white]{quantized_note.symbol}[/black on white]"
        info_rest = f"{info_rest:^19}"
        info_rest = f"[#ffffff]{quantized_note.symbol:^9}[/#ffffff]"
        if not blind_note:
            result = self.result(
                head=info_rest,
                body=info_quantization,
                blind_time=blind_time,
            )

        return result, quantization_error


class MidiMessageAnalyzer_lyrics(
    MidiMessageAnalyzer_SoundUnit, MidiMessageAnalyzer_text
):
    """MidiMessageAnalyzer_lyrics"""

    def __init__(
        self,
        msg,
        msg_next,
        note_address,
        ppqn=DEFAULT_PPQN,
        tempo=DEFAULT_TEMPO,
        idx=0,
        length=0,
        encoding="utf-8",
        encoding_alternative="cp949",
        note_queue=None,
    ):
        self.msg = msg
        self.ppqn = ppqn
        self.tempo = tempo
        self.idx_info = f"[color(244)]{idx:4}[/color(244)]"
        self.length = length
        if note_queue is None:
            self.note_queue = {}
        else:
            self.note_queue = note_queue
        self._init_encoding(
            encoding=encoding, encoding_alternative=encoding_alternative
        )
        self.msg_next = msg_next
        self.note_address = note_address

    def is_alnumpunc(self, s):
        """is_alnumpunc"""
        candidate = string.ascii_letters + string.digits + string.punctuation
        for c in s:
            if c not in candidate:
                return False
        return True

    def analysis(
        self, blind_time=False, border_color="#ffffff", blind_note=False
    ):
        if not self.note_queue and (
            self.msg_next.type != "note_on" or self.msg_next.time != 0
        ):  # error case
            lyric_style = "white on red"
            border_color = "white on red"
        else:
            lyric_style = "#98ff29"
            border_color = f"color({COLOR[self.note_address]})"

        lyric = self.encoded_text.decode(self.encoding).strip()
        border = f"[{border_color}]│[/{border_color}]"
        lyric_info = (
            f"{lyric:^7}" if self.is_alnumpunc(lyric) else f"{lyric:^6}"
        )

        error, quantized_note = self.quantization_min(self.msg.time)
        info_quantization = ""
        quantization_error = 0
        if error is not None:
            quantization_error = abs(error)
            info_quantization = self.quantization_info(
                round(error, 3),
                tick2beat(self.msg.time, self.ppqn),
                quantized_note,
            )
        head = (
            border
            + f"[{lyric_style}]"
            + lyric_info
            + f"[/{lyric_style}]"
            + border
        )
        result = ""
        if not blind_note:
            result = self.result(
                head=head,
                body=info_quantization,
                blind_time=blind_time,
            )
        return result, lyric, quantization_error
