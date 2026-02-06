# Image to Video (Windows `.exe` 対応)

1枚の画像から、**最大10分（600秒）** の MP4 動画を作るツールです。

## できること
- 画像を1枚指定するだけで MP4 を生成
- 動画長は `1〜600` 秒（未指定時は10秒）
- 出力ファイル名は未指定時に自動で `<画像名>_video.mp4`
- Windows では `.exe` を配布して **Python なし** で実行可能

## 前提
- `ffmpeg` がインストールされ、PATH に通っていること
  - または `tools\ffmpeg\bin\ffmpeg.exe` を同梱していること

## Python を使わずに実行する手順（Windows）
1. `dist\image_to_video.exe` を配置（配布済みバイナリを使用）
2. `cmd.exe` で次を実行

```bat
run_exe_no_python.bat
```

引数なし実行時は、対話形式で以下を入力するだけです。
- 画像パス（必須）
- 動画の長さ（任意、Enterで10秒）

引数を使う場合（任意）:

```bat
run_exe_no_python.bat --image input.jpg --duration 120 --output output.mp4
```

## 使い方（Python実行・開発者向け）
```bash
python image_to_video_app.py --image input.jpg
```

オプション（任意）:
- `--duration 120`
- `--output output.mp4`

## `.exe` を作る手順（Windows / 開発者向け）
`cmd.exe` で以下を実行:

```bat
build_exe.bat
```

成功すると以下が生成されます。

- `dist\image_to_video.exe`

## 注意
- 本ツールはローカルの `ffmpeg` を呼び出します。
- 600秒超はエラーになります。
