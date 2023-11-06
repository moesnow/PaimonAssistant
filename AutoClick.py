import tkinter as tk
import threading
import pyautogui
import time
import keyboard
import pygetwindow as gw
import cv2
import numpy as np

game_title_name = "原神"
start_4k = cv2.imread("img/start_4k.png", cv2.IMREAD_GRAYSCALE)
select_4k = cv2.imread("img/select_4k.png", cv2.IMREAD_GRAYSCALE)
start_1080 = cv2.imread("img/start_1080.png", cv2.IMREAD_GRAYSCALE)
select_1080 = cv2.imread("img/select_1080.png", cv2.IMREAD_GRAYSCALE)


class AutoClickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("派蒙剧情助手")

        # 设置窗口关闭时的处理函数
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 设置窗口大小
        self.root.geometry("500x220")

        self.is_clicking = False
        self.hotkey_enabled = False

        self.stop_event = threading.Event()  # 用于通知线程停止

        # self.start_button = tk.Button(root, text="开始点击", command=self.start_clicking)
        # self.start_button.pack(pady=10)

        # self.stop_button = tk.Button(root, text="停止点击", command=self.stop_clicking)
        # self.stop_button.pack()

        # self.hotkey_label = tk.Label(root, text="快捷键：F12")
        # self.hotkey_label.pack()

        self.status_label = tk.Label(root, text="\n打开原神“自动”剧情后自动开始运行\n支持1080p和4k\n")
        self.status_label.pack()

        self.status_label = tk.Label(root, text="自动点击状态：已停止", fg="red")
        self.status_label.pack()

        # self.hotkey_thread = threading.Thread(target=self.listen_hotkey)
        # self.hotkey_thread.start()

        self.hotkey_thread = threading.Thread(target=self.listen_game)
        self.hotkey_thread.start()

    def is_application_fullscreen(self):
        if self.windows:
            window = self.windows[0]
            screen_width, screen_height = pyautogui.size()
            is_fullscreen = (window.width, window.height) == (screen_width, screen_height)
            return is_fullscreen
        return False

    def get_window_region(self):
        if self.windows:
            window = self.windows[0]
            return (window.left, window.top, window.width, window.height)

    def take_screenshot(self):
        self.windows = pyautogui.getWindowsWithTitle(game_title_name)
        if self.is_application_fullscreen():
            screenshot = pyautogui.screenshot()
        else:
            screenshot = pyautogui.screenshot(region=self.get_window_region())
        return screenshot

    def start_clicking(self):
        self.is_clicking = True
        self.status_label.config(text="自动点击状态：运行中", fg="green")
        threading.Thread(target=self.click_thread).start()

    def stop_clicking(self):
        self.is_clicking = False
        self.status_label.config(text="自动点击状态：已停止", fg="red")

    def listen_hotkey(self):
        while not self.stop_event.is_set():
            if keyboard.is_pressed("F12"):
                self.toggle_clicking()
                time.sleep(0.2)

    def listen_game(self):
        while not self.stop_event.is_set():
            try:
                window = gw.getWindowsWithTitle(game_title_name)
                if window and window[0].isActive:
                    print("游戏激活")
                    screenshot = cv2.cvtColor(np.array(self.take_screenshot()), cv2.COLOR_RGB2GRAY)
                    if self.windows[0].height > 1440:
                        result = cv2.matchTemplate(screenshot, start_4k, cv2.TM_CCOEFF_NORMED)
                    else:
                        result = cv2.matchTemplate(screenshot, start_1080, cv2.TM_CCOEFF_NORMED)
                    _, max_val, _, _ = cv2.minMaxLoc(result)
                    print(max_val)
                    if max_val > 0.9 and not self.is_clicking:
                        self.start_clicking()
                    else:
                        if self.windows[0].height > 1440:
                            result = cv2.matchTemplate(screenshot, select_4k, cv2.TM_CCOEFF_NORMED)
                        else:
                            result = cv2.matchTemplate(screenshot, select_1080, cv2.TM_CCOEFF_NORMED)
                        _, max_val, _, max_loc = cv2.minMaxLoc(result)
                        if max_val > 0.9:
                            top_left = (max_loc[0] + self.windows[0].left, max_loc[1] + self.windows[0].top)
                            pyautogui.click(top_left)
                            # self.start_clicking()
                        elif self.is_clicking:
                            self.stop_clicking()
                else:
                    self.stop_clicking()
                time.sleep(0.5)
            except Exception as e:
                print(e)

    def toggle_clicking(self):
        if self.is_clicking:
            self.stop_clicking()
        else:
            self.start_clicking()

    def click_thread(self):
        while self.is_clicking:
            pyautogui.click()
            time.sleep(0.1)

    def on_closing(self):
        # 设置停止事件，终止hotkey_thread线程
        self.stop_event.set()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClickerApp(root)
    root.mainloop()
