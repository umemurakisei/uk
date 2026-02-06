# Image to Video (Windows `.exe` 対応)

1枚の画像から、**最大10分（600秒）** の MP4 動画を作るツールです。

## できること
- 画像を1枚指定するだけで MP4 を生成
- 動画長は `1〜600` 秒
- Windows では `.exe` を配布して **Python なし** で実行可能
- `ffmpeg` はアプリ内で自動解決されるため、別途インストール不要

## 前提
- 追加インストール不要（ダウンロード直後に実行可能）

## Python を使わずに実行する手順（Windows）
1. `dist\image_to_video.exe` を配置（配布済みバイナリを使用）
2. `cmd.exe` で次を実行

```bat
run_exe_no_python.bat --image input.jpg --output output.mp4 --duration 120
```

このスクリプトは `image_to_video.exe` を引数付きで実行します。

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
- 600秒超はエラーになります。


## API拡張（自動編集ワークフロー）
バックエンド API (`/uploads` → `/jobs`) では、`edit_instruction` を `POST /jobs` に渡すと、
指示文から編集プランを自動生成するようになりました。

- エフェクト / トランジション / 画面切り替え / テロップ / BGM などを含む
  **常時 2000 種類の編集機能カタログ**を内部保持
- アップロード画像と指示文を受けて、解析 → シーン分割 → セグメント生成 → 連結までを自動実行
- `duration_seconds` は従来どおり `1〜600` 秒
