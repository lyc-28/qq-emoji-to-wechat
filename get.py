from pathlib import Path
import shutil
from PIL import Image

# ================= 路径配置 =================
# 1. QQ 表情缓存源目录
SOURCE_DIR = Path(
    r"C:\Users\你的电脑用户名\Documents\Tencent Files\2057418859\nt_qq\nt_data\Emoji\personal_emoji\Ori"
)

# 2. 目标文件夹 A：原格式纯净归档（包含真 GIF、PNG、JPG）
RAW_DIR = Path(__file__).resolve().parent / "表情包"
RAW_DIR.mkdir(parents=True, exist_ok=True)

# 3. 目标文件夹 B：为微信定制的 100% 纯 GIF 目录
WECHAT_DIR = Path(__file__).resolve().parent / "微信表情包"
WECHAT_DIR.mkdir(parents=True, exist_ok=True)

# 微信防拦截最大边长
MAX_SIZE = 500


def get_real_ext(file_path):
  """通过文件头二进制字节判断真实格式"""
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
  """将静态图片（JPG/PNG等）微缩并转换为单帧 GIF"""
  with Image.open(src_path) as img:
    w, h = img.size
    # 尺寸超标等比缩小
    if max(w, h) > MAX_SIZE:
      scale = MAX_SIZE / max(w, h)
      w, h = int(w * scale), int(h * scale)
      img = img.resize((w, h), Image.Resampling.LANCZOS)

    # 处理透明通道，避免转 GIF 时背景变黑
    if img.mode in ("RGBA", "LA"):
      background = Image.new("RGBA", img.size, (255, 255, 255))
      img = Image.alpha_composite(background, img.convert("RGBA"))

    # 转成调色板模式保存为 GIF
    img.convert("RGB").convert("P", palette=Image.Palette.ADAPTIVE).save(
        dst_path, "GIF"
    )


def main():
  if not SOURCE_DIR.exists():
    print(f"❌ 找不到 QQ 目录，请检查路径: {SOURCE_DIR}")
    return

  print("🚀 开始一键整理 QQ 表情包到两个目标目录...\n")

  total_count = 0
  gif_count = 0
  converted_count = 0

  for file in SOURCE_DIR.glob("*.jpg"):
    try:
      total_count += 1
      real_ext = get_real_ext(file)

      # --- 1. 保存到【表情包】文件夹（保持原始格式） ---
      raw_target = RAW_DIR / f"{file.stem}{real_ext}"
      shutil.copy2(file, raw_target)

      # --- 2. 保存到【微信表情包】文件夹（全部统一为 GIF） ---
      wechat_target = WECHAT_DIR / f"{file.stem}.gif"

      if real_ext == ".gif":
        # 原生动图直接复制
        shutil.copy2(file, wechat_target)
        gif_count += 1
        print(f"[{total_count}] 动图原生复制: {file.name} -> .gif")
      else:
        # 静态图转为单帧 GIF 存入
        convert_static_to_gif(file, wechat_target)
        converted_count += 1
        print(
            f"[{total_count}] 静态图转为GIF: {file.name} ({real_ext}) -> .gif"
        )

    except Exception as e:
      print(f"⚠️ 处理跳过: {file.name}, 错误: {e}")

  print("\n" + "=" * 50)
  print("🎉 全部处理完成！")
  print(f"📁 1. 原版文件夹【表情包】：共导出 {total_count} 个原格式文件")
  print(f"📁 2. 微信文件夹【微信表情包】：共生成 {total_count} 个纯 .gif 文件")
  print(f"   - 其中原生动图: {gif_count} 个")
  print(f"   - 静态转GIF图:  {converted_count} 个")


if __name__ == "__main__":
  main()