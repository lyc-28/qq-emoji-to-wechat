from pathlib import Path
import subprocess
import sys
import time
import pyautogui

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.2

# ================= 兼容打包后的 EXE 路径 =================
if getattr(sys, "frozen", False):
  BASE_DIR = Path(sys.executable).resolve().parent
else:
  BASE_DIR = Path(__file__).resolve().parent

EMOJI_DIR = BASE_DIR / "微信表情包"


def copy_file_to_clipboard(file_path):
  cmd = f'Set-Clipboard -LiteralPath "{file_path}"'
  subprocess.run(
      ["powershell", "-NoProfile", "-Command", cmd],
      check=True,
      creationflags=subprocess.CREATE_NO_WINDOW,
  )


def main():
  print("=" * 60)
  print("【第二步：微信表情全自动录入工具】")
  print("=" * 60)

  if not EMOJI_DIR.exists():
    print(f"❌ 找不到目录: {EMOJI_DIR}")
    print("👉 请先运行第一步 get.exe 生成表情包！")
    input("\n按回车退出...")
    return

  emoji_files = [
      f for f in EMOJI_DIR.iterdir() if f.suffix.lower() in [".gif", ".jpg", ".png"]
  ]
  total = len(emoji_files)
  if total == 0:
    print("❌ 【微信表情包】文件夹中没有找到任何表情！")
    input("\n按回车退出...")
    return

  print(f"📦 共找到 {total} 个待导入表情包。")
  print("=" * 50)
  print("【第一步：校准微信输入框】")
  print("请在 5 秒内切换到电脑微信【文件传输助手】，把鼠标停在【输入文字的空白区域】不要动...")
  for i in range(5, 0, -1):
    print(f"倒计时 {i} 秒...")
    time.sleep(1)

  input_pos = pyautogui.position()
  print(f"✅ 记录输入框坐标: {input_pos}")

  print("\n🚀 正在发送第 1 张图片进行校准...")
  first_file = emoji_files[0]
  copy_file_to_clipboard(first_file.resolve())
  pyautogui.click(input_pos)
  pyautogui.hotkey("ctrl", "v")
  time.sleep(0.5)
  pyautogui.press("enter")
  time.sleep(1.0)

  print("=" * 50)
  print("【第二步：校准表情菜单位置】")
  print(
      "👉 请在 6 秒内：鼠标【右键点击】刚发出的图片，然后把鼠标悬停在弹出的【添加到表情】那一行上，不要动！"
  )
  for i in range(6, 0, -1):
    print(f"倒计时 {i} 秒...")
    time.sleep(1)

  menu_pos = pyautogui.position()
  pyautogui.click(menu_pos)
  print(f"✅ 记录菜单坐标: {menu_pos}，第 1 张表情添加成功！")

  img_click_pos = (menu_pos.x - 40, menu_pos.y - 20)

  print("=" * 50)
  print("🎉 校准完成！3 秒后开始全自动导入，中途如需紧急叫停请将鼠标【猛甩至屏幕最左上角】！")
  time.sleep(3)

  for idx, file_path in enumerate(emoji_files[1:], start=2):
    try:
      copy_file_to_clipboard(file_path.resolve())
      pyautogui.click(input_pos)
      pyautogui.hotkey("ctrl", "v")
      time.sleep(0.3)
      pyautogui.press("enter")
      time.sleep(0.8)

      pyautogui.rightClick(img_click_pos)
      time.sleep(0.3)
      pyautogui.click(menu_pos)
      time.sleep(0.5)

      print(f"[{idx}/{total}] 成功导入: {file_path.name}")

    except pyautogui.FailSafeException:
      print("\n🛑 【紧急制动触发】检测到鼠标移动到屏幕最左上角，已强行终止！")
      input("\n按回车退出...")
      return
    except KeyboardInterrupt:
      print("\n🛑 用户手动终止程序！")
      input("\n按回车退出...")
      return
    except Exception as e:
      print(f"[{idx}/{total}] 失败跳过: {file_path.name}, 错误: {e}")

  print("\n🏁 全部表情处理完毕！")
  input("\n按回车退出程序...")


if __name__ == "__main__":
  main()