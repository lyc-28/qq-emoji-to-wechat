from pathlib import Path
import subprocess
import time
import pyautogui

# 1. 开启安全保护
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.2

# 2. 表情包所在文件夹
EMOJI_DIR = Path(__file__).resolve().parent / "微信表情包"


def copy_file_to_clipboard(file_path):
  """利用系统内置的 PowerShell 把文件作为文件流拷入剪贴板 (保留 GIF 动图原画)"""
  cmd = f'Set-Clipboard -LiteralPath "{file_path}"'
  subprocess.run(
      ["powershell", "-NoProfile", "-Command", cmd],
      check=True,
      creationflags=subprocess.CREATE_NO_WINDOW,
  )


def main():
  emoji_files = [
      f for f in EMOJI_DIR.iterdir() if f.suffix.lower() in [".gif", ".jpg", ".png"]
  ]
  total = len(emoji_files)
  if total == 0:
    print("❌ 表情包文件夹中没有找到图片！")
    return

  print(f"📦 共找到 {total} 个表情包。")
  print("=" * 50)
  print("【第一步：校准微信输入框】")
  print("请在 5 秒内切换到电脑微信【文件传输助手】，把鼠标停在【输入文字的空白区域】不要动...")
  for i in range(5, 0, -1):
    print(f"倒计时 {i} 秒...")
    time.sleep(1)

  input_pos = pyautogui.position()
  print(f"✅ 记录输入框坐标: {input_pos}")

  # 自动发送第一张作为测试校准图
  print("\n🚀 正在发送第 1 张图片进行校准...")
  first_file = emoji_files[0]
  copy_file_to_clipboard(first_file.resolve())
  pyautogui.click(input_pos)
  pyautogui.hotkey("ctrl", "v")
  time.sleep(0.5)
  pyautogui.press("enter")
  time.sleep(1.0)  # 等待图片发送完成显示在聊天框中

  print("=" * 50)
  print("【第二步：校准表情菜单位置】")
  print("👉 现在刚发出的图片已经出现在输入框右上方了。")
  print(
      "👉 请在 6 秒内：鼠标【右键点击】刚发出的图片，然后把鼠标悬停在弹出的【添加到表情】那一行上，不要动！"
  )
  for i in range(6, 0, -1):
    print(f"倒计时 {i} 秒...")
    time.sleep(1)

  menu_pos = pyautogui.position()
  pyautogui.click(menu_pos)
  print(f"✅ 记录菜单坐标: {menu_pos}，第 1 张表情添加成功！")

  # 确定聊天框中最新图片右键的相对位置
  img_click_pos = (menu_pos.x - 40, menu_pos.y - 20)

  print("=" * 50)
  print("🎉 校准完成！3 秒后开始全自动导入，中途终止请直接把鼠标【猛甩到屏幕最左上角】！")
  time.sleep(3)

  # 开始全自动循环添加剩余的所有表情
  for idx, file_path in enumerate(emoji_files[1:], start=2):
    try:
      # 1. 拷贝文件到剪贴板
      copy_file_to_clipboard(file_path.resolve())

      # 2. 点击输入框并粘贴发送
      pyautogui.click(input_pos)
      pyautogui.hotkey("ctrl", "v")
      time.sleep(0.3)
      pyautogui.press("enter")

      # 3. 等待微信发出图片渲染完成
      time.sleep(0.8)

      # 4. 右键点击最新的一张图片
      pyautogui.rightClick(img_click_pos)
      time.sleep(0.3)

      # 5. 点击“添加到表情”
      pyautogui.click(menu_pos)
      time.sleep(0.5)

      print(f"[{idx}/{total}] 成功导入: {file_path.name}")

    # ================= 关键修复区域 =================
    except pyautogui.FailSafeException:
      print("\n🛑 【紧急制动触发】检测到鼠标移动到屏幕最左上角，已强行终止！")
      return  # 立刻彻底退出函数，绝不再执行下一个
    except KeyboardInterrupt:
      print("\n🛑 用户手动终止程序！")
      return
    except Exception as e:
      print(f"[{idx}/{total}] 失败跳过: {file_path.name}, 错误: {e}")
    # ===============================================

  print("\n🏁 全部表情处理完毕！")


if __name__ == "__main__":
  main()