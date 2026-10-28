import os
from pathlib import Path
import shutil
import sys
from PIL import Image

# ================= 兼容打包后的 EXE 路径 =================
if getattr(sys, "frozen", False):
  # 运行的是 EXE 时，取 EXE 所在的真实文件夹
  BASE_DIR = Path(sys.executable).resolve().parent
else:
  # 运行的是 .py 脚本时
  BASE_DIR = Path(__file__).resolve().parent

RAW_DIR = BASE_DIR / "表情包"
RAW_DIR.mkdir(parents=True, exist_ok=True)

WECHAT_DIR = BASE_DIR / "微信表情包"
WECHAT_DIR.mkdir(parents=True, exist_ok=True)

MAX_SIZE = 500


def get_real_ext(file_path):
  try:
    with open(file_path, "rb") as f:
      header = f.read(6)
      if header.startswith(b"GIF87a") or header.startswith(b"GIF89a"):
        return ".gif"
      elif header.startswith(b"\x89PNG"):
        return ".png"
  except Exception:
    pass
  return ".jpg"


def convert_static_to_gif(src_path, dst_path):
  with Image.open(src_path) as img:
    w, h = img.size
    if max(w, h) > MAX_SIZE:
      scale = MAX_SIZE / max(w, h)
      w, h = int(w * scale), int(h * scale)
      img = img.resize((w, h), Image.Resampling.LANCZOS)

    if img.mode in ("RGBA", "LA"):
      background = Image.new("RGBA", img.size, (255, 255, 255))
      img = Image.alpha_composite(background, img.convert("RGBA"))

    img.convert("RGB").convert("P", palette=Image.Palette.ADAPTIVE).save(
        dst_path, "GIF"
    )


def main():
  print("=" * 60)
  print("【第一步：QQ表情提取与转码工具】")
  print("=" * 60)

  # 默认你的路径（给别人用时，如果不存在会提示输入）
  default_path = r"C:\Users\20574\Documents\Tencent Files\2057418859\nt_qq\nt_data\Emoji\personal_emoji\Ori"
  source_dir = Path(default_path)

  if not source_dir.exists():
    print("⚠️ 默认 QQ 路径不存在，请提供您自己的 QQ 表情缓存路径。")
    print(
        "👉 获取方式：电脑 QQ 设置 -> 存储管理 -> 打开文件夹 -> 进入"
        " nt_qq/nt_data/Emoji/personal_emoji/Ori"
    )
    user_input = input("\n请粘贴完整文件夹路径后按回车: ").strip('"').strip("'")
    source_dir = Path(user_input)

  if not source_dir.exists():
    print(f"\n❌ 错误：路径不存在 -> {source_dir}")
    input("\n按回车键退出...")
    return

  print(f"\n🚀 源目录确认无误，开始处理: {source_dir}\n")

  total_count = 0
  gif_count = 0
  converted_count = 0

  for file in source_dir.glob("*.jpg"):
    try:
      total_count += 1
      real_ext = get_real_ext(file)

      raw_target = RAW_DIR / f"{file.stem}{real_ext}"
      shutil.copy2(file, raw_target)

      wechat_target = WECHAT_DIR / f"{file.stem}.gif"
      if real_ext == ".gif":
        shutil.copy2(file, wechat_target)
        gif_count += 1
        print(f"[{total_count}] 动图原生复制: {file.name} -> .gif")
      else:
        convert_static_to_gif(file, wechat_target)
        converted_count += 1
        print(
            f"[{total_count}] 静态图转为GIF: {file.name} ({real_ext}) -> .gif"
        )

    except Exception as e:
      print(f"⚠️ 处理跳过: {file.name}, 错误: {e}")

  print("\n" + "=" * 60)
  print("🎉 全部处理完成！")
  print(f"📁 1. 原版文件夹【表情包】：共导出 {total_count} 个文件")
  print(f"📁 2. 微信文件夹【微信表情包】：共生成 {total_count} 个纯 .gif 文件")
  print("=" * 60)
  input("\n处理完成，请按回车键退出...")


if __name__ == "__main__":
  main()