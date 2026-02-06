# Image to Video (Windows `.exe` 対応)

1枚の画像から、**最大10分（600秒）** の MP4 動画を作るツールです。

## できること
- 画像を1枚指定するだけで MP4 を生成
- 動画長は `1〜600` 秒
- Windows では `.exe` を配布して **Python なし** で実行可能

## 前提
- `ffmpeg` がインストールされ、PATH に通っていること
  - もしくは `run_exe_no_python.bat` が自動ダウンロードするローカル ffmpeg を使用

## Python を使わずに実行する手順（Windows）
1. `dist\image_to_video.exe` を配置（配布済みバイナリを使用）
2. `cmd.exe` で次を実行

```bat
run_exe_no_python.bat --image input.jpg --output output.mp4 --duration 120
```

このスクリプトは以下を行います。
- `ffmpeg` が PATH にあればそれを使用
- なければ `tools\ffmpeg` に自動ダウンロードして使用
- `image_to_video.exe` を引数付きで実行

## 使い方（Python実行・開発者向け）
```bash
python image_to_video_app.py --image input.jpg --output output.mp4 --duration 120
```

## `.exe` を作る手順（Windows / 開発者向け）
`cmd.exe` で以下を実行:

```bat
build_exe.bat
```

成功すると以下が生成されます。

- `dist\image_to_video.exe`

## `.exe` の実行例
```bat
dist\image_to_video.exe --image input.jpg --output output.mp4 --duration 300
```

## 注意
- 本ツールはローカルの `ffmpeg` を呼び出します。
- 600秒超はエラーになります。
