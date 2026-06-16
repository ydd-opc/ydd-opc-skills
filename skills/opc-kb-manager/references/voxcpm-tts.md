# VoxCPM2 TTS — Installation & Voice Optimization

## Installation

```bash
pip install voxcpm
```

Requires Python ≥ 3.10 (<3.13), PyTorch ≥ 2.5.0.

## Model Download

**HuggingFace** (slow from China):
```python
from voxcpm import VoxCPM
model = VoxCPM.from_pretrained("openbmb/VoxCPM2")
```

**ModelScope** (faster from China, ~7MB/s):
```python
from modelscope import snapshot_download
snapshot_download("OpenBMB/VoxCPM2", local_dir="./pretrained_models/VoxCPM2")

from voxcpm import VoxCPM
model = VoxCPM.from_pretrained(
    "./pretrained_models/VoxCPM2",
    local_files_only=True,
    load_denoiser=False,
)
```

## Hardware Requirements

- **GPU**: CUDA 12.0+ required for GPU acceleration. CUDA 10.2 is too old.
- **RAM**: 4.7GB for model weights + ~4GB for inference = ~8-10GB free RAM minimum.
  - User's machine: 16GB total, only 58MB free → failed to load.
- **CPU only**: Works but very slow (~10x slower). Loading takes 3-5 min, generation takes 5-10 min per sentence.

## Voice Description Optimization

**English descriptions work better than Chinese.** VoxCPM's training data has more English voice tags.

### Good descriptions:
```
(male, warm and confident, slightly faster pace, like a podcaster talking to a friend, genuine and conversational)
```

### Avoid:
- Don't say "带一点感情" — too vague, model doesn't know what that means.
- Don't use custom pause markers like 【停顿】— model reads them as text.

### Punctuation for Pauses

VoxCPM reads punctuation naturally:
- Period (。): longest pause, natural sentence break
- Em dash (——): brief mid-sentence pause
- Comma (，): short pause
- Paragraph breaks: long transition pauses

Write short sentences separated by 。 to create natural rhythm. Avoid long multi-clause sentences.

## Voice Design (No Reference Audio)

```python
wav = model.generate(
    text="(A young man, warm and friendly, confident tone)大家好，欢迎收看本期内容。",
    cfg_value=2.0,
    inference_timesteps=10,
)
```

## Online Demo

https://voxcpm.modelbest.cn/ — fastest way to test voice quality without local setup.
