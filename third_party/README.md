# third_party/README.md
# Third-Party Model Storage

This directory holds upstream AI generation models integrated into GenOTT V2 as execution backends:
- `wan/`: Official WAN open-source repository
- `hunyuanvideo/`: HunyuanVideo backend source
- `cogvideox/`: CogVideoX backend source
- `ltx-video/`: LTX Video backend source
- `mochi/`: Mochi backend source

Do NOT modify third-party upstream files directly. All adapter logic, prompt compilation, and runtime routing must exist within `engine/`.
