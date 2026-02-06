# Image to Video (Windows `.exe` 対応)

1枚の画像から、**最大10分（600秒）** の MP4 動画を作るツールです。

## できること
- 画像を1枚指定するだけで MP4 を生成
- 動画長は `1〜600` 秒
- Windows では `.exe` にビルドして配布可能

## 前提
- Python 3.10+
- `ffmpeg` がインストールされ、PATH に通っていること

## 使い方（Python実行）
```bash
python image_to_video_app.py --image input.jpg --output output.mp4 --duration 120
```

## `.exe` を作る手順（Windows）
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
