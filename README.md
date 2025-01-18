
# Requirements

- ffmpeg: https://www.ffmpeg.org/download.html
- Python packages

    ```shell
    $ pip install librosa pydub rich pretty_midi
    $ pip install git+https://github.com/ccss17/mido
    ```

quantization 에러를 줄여야 함. --> 에러가 중첩되니까 --> 싱크를 맞춰야 함.

--> 이전 quantization 에러를 고려해서 다음 노트의 에러를 계산해야 함. 에러가 - 면 밀렸다, + 면 땡겨졌다 이런 식으로 판단해서, 지금은 에러를 독립적으로 보기 때문에 에러가 계속 중첩 되는 상황 

--> 최종적으로는 quantization 된 mid 파일을 음원으로 재생하고, 노래를 같이 재생해보면서 싱크가 맞으면 제대로 했다 이런 결론을 내릴 수 있음. 
