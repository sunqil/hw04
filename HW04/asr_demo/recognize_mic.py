import argparse
import json
import os
import queue
import sys

from vosk import Model, KaldiRecognizer
import sounddevice as sd


def default_model_dir() -> str:
    # 默认模型目录：在当前运行脚本目录（asr_demo）下的 models/vosk-model
    return os.path.join(os.path.dirname(__file__), "models", "vosk-model")


def main() -> None:
    parser = argparse.ArgumentParser(description="使用 Vosk + sounddevice 进行麦克风实时识别")
    parser.add_argument(
        "--model-dir",
        default=default_model_dir(),
        help="Vosk 模型目录（默认：models/vosk-model）",
    )
    parser.add_argument("--sample-rate", type=int, default=16000, help="麦克风采样率（默认：16000）")
    args = parser.parse_args()

    model_dir = args.model_dir
    if not os.path.isdir(model_dir):
        print(
            f"模型目录不存在：{model_dir}\n请先下载 Vosk 模型并放置到该目录。",
            file=sys.stderr,
        )
        sys.exit(1)

    model = Model(model_dir)
    recognizer = KaldiRecognizer(model, args.sample_rate)

    q: "queue.Queue[bytes]" = queue.Queue()
    last_partial = ""

    def callback(indata, frames, time, status):
        # status 用于指示采集是否发生溢出/中断等问题
        if status:
            print(f"\n[采集状态] {status}", file=sys.stderr)
        # indata dtype 设为 int16 后，tobytes() 即为 Vosk 所需的 PCM 字节流
        q.put(bytes(indata))

    print("开始麦克风实时识别，按 Ctrl+C 退出。")
    print(f"提示：脚本默认 16kHz 单声道 int16（sample-rate={args.sample_rate}）。")

    try:
        with sd.InputStream(
            samplerate=args.sample_rate,
            channels=1,
            dtype="int16",
            callback=callback,
        ):
            while True:
                data = q.get()
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    text = (result.get("text") or "").strip()
                    if text:
                        print(f"\n[最终] {text}")
                        last_partial = ""
                else:
                    partial = json.loads(recognizer.PartialResult()).get("partial", "").strip()
                    if partial and partial != last_partial:
                        # 使用同一行持续更新中间识别结果
                        print(f"\r[中间] {partial}", end="", flush=True)
                        last_partial = partial
    except KeyboardInterrupt:
        print("\n已退出。")


if __name__ == "__main__":
    main()

