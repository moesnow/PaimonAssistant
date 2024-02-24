import tkinter as tk
import pyautogui
import time
import pygetwindow as gw
import cv2
import numpy as np

game_title_name = "原神"
start_4k = cv2.imread("img/start_4k.png", cv2.IMREAD_GRAYSCALE)
select_4k = cv2.imread("img/select_4k.png", cv2.IMREAD_GRAYSCALE)
continue_4k = cv2.imread("img/continue_4k.png", cv2.IMREAD_GRAYSCALE)
start_1080 = cv2.imread("img/start_1080.png", cv2.IMREAD_GRAYSCALE)
select_1080 = cv2.imread("img/select_1080.png", cv2.IMREAD_GRAYSCALE)
continue_1080 = cv2.imread("img/continue_1080.png", cv2.IMREAD_GRAYSCALE)


class AutoClickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("派蒙剧情助手")

        # 设置窗口大小
        self.root.geometry("500x220")

        self.is_clicking = False

        self.status_label = tk.Label(root, text="\n打开原神“自动”剧情后自动开始运行\n支持1080p和4k\n")
        self.status_label.pack()

        self.status_label = tk.Label(root, text="自动点击状态：已停止", fg="red")
        self.status_label.pack()

        self.check_game_status()

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
        if not self.is_clicking:
            self.is_clicking = True
            self.status_label.config(text="自动点击状态：运行中", fg="green")
            self.click()

    def stop_clicking(self):
        if self.is_clicking:
            self.is_clicking = False
            self.status_label.config(text="自动点击状态：已停止", fg="red")

    def check_game_status(self):
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
            if max_val > 0.9:
                self.start_clicking()
                if self.windows[0].height > 1440:
                    result = cv2.matchTemplate(screenshot, select_4k, cv2.TM_CCOEFF_NORMED)
                else:
                    result = cv2.matchTemplate(screenshot, select_1080, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, max_loc = cv2.minMaxLoc(result)
                if max_val > 0.8:
                    top_left = (max_loc[0] + self.windows[0].left, max_loc[1] + self.windows[0].top)
                    pyautogui.click(top_left)
            else:
                self.stop_clicking()
                if self.windows[0].height > 1440:
                    result = cv2.matchTemplate(screenshot, continue_4k, cv2.TM_CCOEFF_NORMED)
                else:
                    result = cv2.matchTemplate(screenshot, continue_1080, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, max_loc = cv2.minMaxLoc(result)
                if max_val > 0.8:
                    top_left = (max_loc[0] + self.windows[0].left, max_loc[1] + self.windows[0].top)
                    pyautogui.click(top_left)
        else:
            self.stop_clicking()
        # 定时检查游戏状态
        self.root.after(500, self.check_game_status)

    def toggle_clicking(self):
        if self.is_clicking:
            self.stop_clicking()
        else:
            self.start_clicking()

    def click(self):
        if self.is_clicking:
            pyautogui.click()
            time.sleep(0.2)
            self.root.after(10, self.click)


if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClickerApp(root)
    root.mainloop()
