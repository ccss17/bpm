import numpy as np


# This function is obtained from librosa.
def get_rms(
    y,
    *,
    frame_length=2048,
    hop_length=512,
    pad_mode="constant",
):
    # 패딩 추가
    padding = (int(frame_length // 2), int(frame_length // 2))
    y = np.pad(y, padding, mode=pad_mode)

    #
    axis = -1
    # put our new within-frame axis at the end for now
    out_strides = y.strides + tuple([y.strides[axis]])

    # Reduce the shape on the framing axis
    x_shape_trimmed = list(y.shape)
    x_shape_trimmed[axis] -= frame_length - 1
    out_shape = tuple(x_shape_trimmed) + tuple([frame_length])
    xw = np.lib.stride_tricks.as_strided(
        y, shape=out_shape, strides=out_strides
    )
    if axis < 0:
        target_axis = axis - 1
    else:
        target_axis = axis + 1
    xw = np.moveaxis(xw, -1, target_axis)

    # Downsample along the target axis
    slices = [slice(None)] * xw.ndim
    slices[axis] = slice(0, None, hop_length)
    x = xw[tuple(slices)]

    # Calculate power
    power = np.mean(np.abs(x) ** 2, axis=-2, keepdims=True)

    return np.sqrt(power)


class Slicer:
    def __init__(
        self,
        sr: int,
        threshold: float = -40.0,
        min_length: int = 5000,
        max_length: int = 15000,
        min_interval: int = 300,
        hop_size: int = 20,
        max_sil_kept: int = 5000,
    ):
        if not min_length >= min_interval >= hop_size:
            raise ValueError(
                "The following condition must be satisfied: min_length >= min_interval >= hop_size"
            )
        if not max_sil_kept >= hop_size:
            raise ValueError(
                "The following condition must be satisfied: max_sil_kept >= hop_size"
            )
        min_interval = sr * min_interval / 1000
        self.threshold = 10 ** (threshold / 20.0)
        self.hop_size = round(sr * hop_size / 1000)
        self.win_size = min(round(min_interval), 4 * self.hop_size)
        self.min_length = round(sr * min_length / 1000 / self.hop_size)
        self.max_length = round(sr * max_length / 1000 / self.hop_size)
        self.min_interval = round(min_interval / self.hop_size)
        self.max_sil_kept = round(sr * max_sil_kept / 1000 / self.hop_size)
        self.chunks_time = []

    def _apply_slice(self, waveform, begin, end):
        # self.chunks_time.append((begin.item(), end.item()))
        self.chunks_time.append((begin, end))
        if len(waveform.shape) > 1:
            return waveform[
                :,
                begin * self.hop_size : min(
                    waveform.shape[1], end * self.hop_size
                ),
            ]
        else:
            return waveform[
                begin * self.hop_size : min(
                    waveform.shape[0], end * self.hop_size
                )
            ]

    def silence_tag(self, i, silence_start, rms_list, sil_tags):
        if i - silence_start == 1:
            return
        else:
            if silence_start == 0:
                sil_tags.append((0, i - 1))
            else:
                sil_tags.append((silence_start, i - 1))

    def segment_tag_over_max_length(
        self, seg_start, seg_end, seg_index, rms_list, seg_tags, flag=0
    ):
        silence_tags = []
        sil_start = None
        sil_end = None

        for i, rms in enumerate(rms_list[seg_start : seg_end + 1]):
            if rms < self.threshold:
                if sil_start is None:
                    sil_start = i + seg_start
                continue
            else:
                if sil_start is None:
                    continue
                else:
                    sil_end = i + seg_start
                    if sil_end - sil_start == 1:
                        sil_start = None
                        sil_end = None
                        continue
                    else:
                        silence_tags.append([sil_start, sil_end - 1])
                        sil_start = None
                        sil_end = None
                        continue

        for i, tag in enumerate(silence_tags):
            tag.append(tag[1] - tag[0])

        silence_tags = sorted(silence_tags, key=lambda x: x[-1], reverse=True)
        # print(f"silence_tags of ({seg_start}:{seg_end}):", silence_tags)

        if len(silence_tags) == 0:
            seg_tags.insert(i, (seg_start, seg_end, 0))
            return

        for tag in silence_tags:
            if (
                tag[0] - seg_start <= self.max_length
                and seg_end - tag[1] <= self.max_length
            ):
                if flag == 0:
                    del seg_tags[seg_index]
                seg_tags.append((seg_start, tag[0]))
                seg_tags.append((tag[1], seg_end))
                return

            elif (
                tag[0] - seg_start <= self.max_length
                and seg_end - tag[1] > self.max_length
            ):
                if flag == 0:
                    del seg_tags[seg_index]
                seg_tags.append((seg_start, tag[0]))
                self.segment_tag_over_max_length(
                    tag[1], seg_end, seg_index + 1, rms_list, seg_tags, 1
                )
                return

            elif (
                tag[0] - seg_start > self.max_length
                and seg_end - tag[1] <= self.max_length
            ):
                if flag == 0:
                    del seg_tags[seg_index]
                seg_tags.append((seg_start, tag[0]))
                self.segment_tag_over_max_length(
                    seg_start, tag[0], seg_index + 1, rms_list, seg_tags, 1
                )
                return

            else:
                if flag == 0:
                    del seg_tags[seg_index]
                self.segment_tag_over_max_length(
                    tag[1], seg_end, seg_index + 1, rms_list, seg_tags, 1
                )
                self.segment_tag_over_max_length(
                    seg_start, tag[0], seg_index + 1, rms_list, seg_tags, 1
                )
                return

    def sil2seg(self, sil_tags, len_rms_list):
        result = []
        # 첫 번째 튜플의 첫 번째 값이 0이 아닐 경우 (0, 해당 값 - 1) 추가
        if sil_tags[0][0] != 0:
            result.append((0, sil_tags[0][0] - 1))

        # 중간 튜플 처리
        for i in range(len(sil_tags) - 1):
            result.append((sil_tags[i][1] + 1, sil_tags[i + 1][0] - 1))

        # 마지막 튜플 처리
        result.append((sil_tags[-1][1] + 1, len_rms_list))

        return result

    # @timeit
    def slice(self, waveform):
        if self.chunks_time:
            self.chunks_time = []
        # 다채널 처리
        if len(waveform.shape) > 1:
            samples = waveform.mean(axis=0)
        else:
            samples = waveform

        # 길이 확인; 오디오 클립이 너무 짧은 경우.
        if (
            samples.shape[0] + self.hop_size - 1
        ) // self.hop_size <= self.min_length:
            return [waveform]

        # RMS 분석
        rms_list = get_rms(
            y=samples, frame_length=self.win_size, hop_length=self.hop_size
        ).squeeze(0)

        sil_tags = []
        silence_start = None
        clip_start = 0
        for i, rms in enumerate(rms_list):
            # Keep looping while frame is silent.
            if rms < self.threshold:
                # Record start of silent frames.
                if silence_start is None:
                    silence_start = i
                continue
            # Keep looping while frame is not silent and silence start has not been recorded.
            if silence_start is None:
                continue

            if i - silence_start >= self.min_interval:  # silence 구간일 때
                clip_length = silence_start - clip_start
                if (
                    clip_length >= self.min_length
                ):  # clip의 최소 길이 보장할 때
                    self.silence_tag(i, silence_start, rms_list, sil_tags)
                    clip_start = i
                    silence_start = None
                else:
                    silence_start = None
                    continue

            else:  # silence 구간이 아닐 때
                silence_start = None
                continue

        seg_tags = self.sil2seg(sil_tags, len(rms_list) - 1)
        # print("max: ",self.max_length)
        # print("max(s): ",self.max_length/self.sr)
        # print("min: ",self.min_length)
        # print("Original seg_tags: ", seg_tags)
        for i, tag in enumerate(seg_tags):
            seg_start = tag[0]
            seg_end = tag[1]
            seg_length = seg_end - seg_start
            if seg_length > self.max_length and len(tag) == 2:
                # print("seg_tag:", tag)
                # print("before_seg_tags:", seg_tags)
                self.segment_tag_over_max_length(
                    seg_start, seg_end, i, rms_list, seg_tags
                )
                # print("after_seg_tags:", sorted(seg_tags, key=lambda x: x[0]))

        seg_tags = sorted(seg_tags, key=lambda x: x[0])
        # print(seg_tags)
        if seg_tags[-1][1] - seg_tags[-1][0] < self.min_length:
            del seg_tags[-1]
        if seg_tags[0] == (0, 0):
            del seg_tags[0]

        if len(sil_tags) == 0:
            return [waveform]
        else:
            chunks = []
            for i, tag in enumerate(seg_tags):
                if tag[0] == 0:
                    chunks.append(
                        self._apply_slice(waveform, tag[0], tag[1] + 1)
                    )
                else:
                    chunks.append(
                        self._apply_slice(waveform, tag[0] - 1, tag[1] + 1)
                    )
            return chunks


def main():
    import os.path
    from argparse import ArgumentParser

    import librosa
    import soundfile

    parser = ArgumentParser()
    parser.add_argument("audio", type=str, help="The audio to be sliced")
    parser.add_argument(
        "--out", type=str, help="Output directory of the sliced audio clips"
    )
    parser.add_argument(
        "--db_thresh",
        type=float,
        required=False,
        default=-40,
        help="The dB threshold for silence detection",
    )
    parser.add_argument(
        "--min_length",
        type=int,
        required=False,
        default=5000,
        help="The minimum milliseconds required for each sliced audio clip",
    )
    parser.add_argument(
        "--min_interval",
        type=int,
        required=False,
        default=300,
        help="The minimum milliseconds for a silence part to be sliced",
    )
    parser.add_argument(
        "--hop_size",
        type=int,
        required=False,
        default=10,
        help="Frame length in milliseconds",
    )
    parser.add_argument(
        "--max_sil_kept",
        type=int,
        required=False,
        default=500,
        help="The maximum silence length kept around the sliced clip, presented in milliseconds",
    )
    args = parser.parse_args()
    out = args.out
    if out is None:
        out = os.path.dirname(os.path.abspath(args.audio))
    audio, sr = librosa.load(args.audio, sr=None, mono=False)
    slicer = Slicer(
        sr=sr,
        threshold=args.db_thresh,
        min_length=args.min_length,
        min_interval=args.min_interval,
        hop_size=args.hop_size,
        max_sil_kept=args.max_sil_kept,
    )
    chunks = slicer.slice(audio)
    if not os.path.exists(out):
        os.makedirs(out)
    for i, chunk in enumerate(chunks):
        if len(chunk.shape) > 1:
            chunk = chunk.T
        soundfile.write(
            os.path.join(
                out,
                f"%s_%d.wav"
                % (os.path.basename(args.audio).rsplit(".", maxsplit=1)[0], i),
            ),
            chunk,
            sr,
        )


if __name__ == "__main__":
    main()
