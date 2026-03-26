import argparse
import json
import os
import wave
import sys

from vosk import Model, KaldiRecognizer


def default_model_dir() -> str:
    # 默认模型目录：在当前运行脚本目录（asr_demo）下的 models/vosk-model
    return os.path.join(os.path.dirname(__file__), "models", "vosk-model")


def check_wav_format(wav_path: str) -> tuple[int, int]:
    """
    基本 WAV 检查：
    - 必须存在
    - 单声道（channels == 1）
    - 16-bit PCM（sampwidth == 2 且 comdtype 为 NONE）
    返回 (sample_rate, channels)
    """
    if not os.path.isfile(wav_path):
        raise FileNotFoundError(f"音频文件不存在：{wav_path}")

    with wave.open(wav_path, "rb") as wf:
        channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()  # 字节数：16-bit PCM => 2
        comp = wf.getcomptype()        # PCM 通常为 'NONE'
        sample_rate = wf.getframerate()

        if channels != 1:
            raise ValueError(f"WAV 必须为单声道（channels=1），当前 channels={channels}")
        if sampwidth != 2 or comp != "NONE":
            raise ValueError("WAV 必须为 16-bit PCM（sample_width=2 且编码类型为 PCM/NONE）。")

        return sample_rate, channels


def main() -> None:
    parser = argparse.ArgumentParser(description="使用 Vosk 识别 wav 音频文件")
    parser.add_argument("wav_path", help="输入 wav 文件路径，例如 test.wav")
    parser.add_argument(
        "--model-dir",
        default=default_model_dir(),
        help="Vosk 模型目录（默认：models/vosk-model）",
    )
    args = parser.parse_args()

    model_dir = args.model_dir
    if not os.path.isdir(model_dir):
        print(f"模型目录不存在：{model_dir}\n请先下载 Vosk 模型并放置到该目录。", file=sys.stderr)
        sys.exit(1)

    try:
        sample_rate, _ = check_wav_format(args.wav_path)
    except Exception as e:
        print(f"音频文件检查失败：{e}", file=sys.stderr)
        sys.exit(1)

    # 加载模型与识别器
    model = Model(model_dir)
    recognizer = KaldiRecognizer(model, sample_rate)

    # 逐块读取音频并送入解码器
    with wave.open(args.wav_path, "rb") as wf:
        while True:
            data = wf.readframes(4000)
            if not data:
                break
            if recognizer.AcceptWaveform(data):
                # 文件识别这里也会触发局部结果，但作业要求输出最终识别文本
                pass

    final_result = recognizer.FinalResult()
    try:
        obj = json.loads(final_result)
        text = (obj.get("text") or "").strip()
    except json.JSONDecodeError:
        text = str(final_result).strip()

    if text:
        print(text)
    else:
        # 若为空，仍输出 final_result 便于排查
        print(final_result)


if __name__ == "__main__":
    main()

