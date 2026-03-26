# HW04 作业说明
本目录用于提交本次“HW04”作业内容，包含三项任务：任务一大模型生成口播文稿、任务二剪映声音克隆说明、任务三开源语音识别调研与本地实现（Vosk）。

## 文件说明
- `text_gen.md`：任务一，使用大模型生成口播科普短文。
- `jianying.md`：任务二，剪映声音克隆的操作与导出说明（含替代路径）。
- `asr_report.md`：任务三，开源语音识别调研、方案对比与本地实现说明。
- `experiment_log.md`：实验记录初稿（环境、结果、延迟与错误观察）。
- `asr_demo/`：本地语音识别演示代码与依赖。

## asr_demo 安装与运行
`asr_demo` 目录下提供了 `recognize_file.py`（识别音频文件）与 `recognize_mic.py`（麦克风实时识别）。

```bash
cd HW04/asr_demo
pip install -r requirements.txt
python recognize_file.py test.wav
python recognize_mic.py
```

> 注意：
> 1. 请先在 `HW04/asr_demo/models/vosk-model` 放置你下载好的 Vosk 模型目录（本仓库不包含模型文件）。
> 2. `python recognize_file.py test.wav` 需要 `test.wav` 为单声道、16-bit PCM 的 wav 文件；不符合时脚本会报错并提示原因。

