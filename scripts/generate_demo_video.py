"""Generate the original silent lesson demo with FFmpeg. No external media."""

from pathlib import Path
import shutil
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
output = root / "frontend/public/demo/web-welcome.mp4"
output.parent.mkdir(parents=True, exist_ok=True)
font = Path("C:/Windows/Fonts/segoeui.ttf")
prefix = (
    "fontfile='" + str(font).replace("\\", "/").replace(":", "\\:") + "':"
    if font.exists()
    else ""
)
filters = [
    "drawbox=x=50:y=55:w=860:h=430:color=white@0.07:t=fill",
    f"drawtext={prefix}text='LearnHub - Web Foundations':fontsize=38:fontcolor=white:x=85:y=95",
    f"drawtext={prefix}text='HTML  -  Structure':fontsize=30:fontcolor=white:x=85:y=205:enable='gte(t,0)'",
    f"drawtext={prefix}text='CSS   -  Style':fontsize=30:fontcolor=white:x=85:y=275:enable='gte(t,4)'",
    f"drawtext={prefix}text='JavaScript  -  Interaction':fontsize=30:fontcolor=white:x=85:y=345:enable='gte(t,8)'",
    "drawbox=x=85:y=435:w=790:h=5:color=white@0.2:t=fill",
    "drawbox=x=85:y=435:w=790:h=5:color=0x84c2af:t=fill:enable='gte(t,11)'",
]
subprocess.run(
    [
        shutil.which("ffmpeg") or "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        "color=c=0x1c4e43:s=960x540:r=24:d=12",
        "-vf",
        ",".join(filters),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        "-an",
        str(output),
    ],
    check=True,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.PIPE,
)
print(output)
