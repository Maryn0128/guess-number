"""
猜数字小游戏（命令行版）
========================================================
运行方法：
  1) 按 Win + R，输入 cmd，回车，打开「命令提示符」
  2) 用 cd 命令进入本文件所在的文件夹，例如：
         cd /d C:\\Users\\Maryn\\WorkBuddy\\2026-10-16-22-16-10
  3) 运行本文件：
         python guess_number.py

游戏规则：电脑随机想一个 1~100 的整数，你每次输入一个数字，
程序告诉你「大了」或「小了」，直到你猜中，并显示总共猜了几次。
========================================================
"""

import random

# ---------- 全局常量（放在最上面，想改难度只改这里） ----------
LOW = 1          # 数字范围的下限
HIGH = 100       # 数字范围的上限
EXIT_WORDS = {"q", "quit", "exit", "退出"}   # 输入这些词就退出游戏


def make_answer():
    """让电脑随机出一个答案（闭区间 [LOW, HIGH] 上的整数）"""
    return random.randint(LOW, HIGH)


def read_guess():
    """
    读取玩家输入的一个数字，并做检查。

    返回值是一个「元组」，用第一个元素表示结果状态：
        ("ok",    数字)   输入合法，可以拿去比较
        ("exit",  None)   玩家输入了 q，想退出游戏
        ("error", None)   输入不合法，本次不算次数，需要重新输入
    """
    text = input("请猜一个数字：").strip()      # strip() 去掉首尾的空格和回车

    if text.lower() in EXIT_WORDS:             # 想退出？
        return "exit", None

    try:
        guess = int(text)                      # 把输入的文字转成整数
    except ValueError:                         # 转不了（比如输入了 abc）就报错
        print("  输入有误：只能输入整数，请重新输入\n")
        return "error", None

    if guess < LOW or guess > HIGH:             # 数字超范围
        print(f"  输入有误：请输入 {LOW} ~ {HIGH} 之间的数字\n")
        return "error", None

    return "ok", guess


def play_one_round():
    """
    完整地玩一局游戏。
    正常结束时返回「本局猜的次数」；玩家中途输入 q 则返回 None。
    """
    answer = make_answer()          # 第 1 步：电脑出题
    count = 0                       # 第 2 步：计数器，记录猜了几次
    low, high = LOW, HIGH           # 记录根据提示收窄后的可能范围（小彩蛋）

    while True:                     # 第 3 步：反复猜，直到猜中或退出
        status, guess = read_guess()

        if status == "exit":
            return None             # 玩家想退出，直接结束本局
        if status == "error":
            continue                # 输入不合法，不计次数，重新输入

        count += 1                  # 第 4 步：猜了一次，次数加 1

        # 第 5 步：把玩家的数字和答案比较，给出提示
        if guess > answer:
            print("  → 大了 ↓   再猜小一点")
            high = min(high, guess - 1)     # 答案肯定比 guess 小
        elif guess < answer:
            print("  → 小了 ↑   再猜大一点")
            low = max(low, guess + 1)       # 答案肯定比 guess 大
        else:
            # 猜中了，本局结束
            print()
            print("=" * 30)
            print(f"  猜中啦！答案就是 {answer}")
            print(f"  你一共猜了 {count} 次")
            if count <= 7:
                print("  很厉害，这已经接近最优策略了！")
            print("=" * 30)
            return count

        # 没猜中，显示进度，然后进入下一次循环
        print(f"  已猜 {count} 次   可能范围：{low} ~ {high}\n")


def main():
    """程序入口：显示开场白，然后一局一局地玩下去"""
    print("=" * 30)
    print("         猜数字小游戏")
    print("=" * 30)
    print(f"我心里想了一个 {LOW} ~ {HIGH} 的整数，你来猜猜看。")
    print("每猜一次，我会告诉你「大了」还是「小了」。")
    print("随时输入 q 可以退出。")
    print()

    try:
        while True:                 # 外层循环：控制「要不要再来一局」
            count = play_one_round()

            if count is None:       # 玩家主动退出
                print("\n已退出，下次再来玩～")
                break

            again = input("再来一局？（直接回车 = 再来，输入 n = 结束）：").strip().lower()
            if again == "n":
                print("拜拜～")
                break
            print()                 # 空一行，让下一局看起来清爽一点
    except (KeyboardInterrupt, EOFError):
        # 玩家按了 Ctrl + C，或者输入被意外中断：
        # 这里捕获一下，避免屏幕上出现一堆看不懂的英文报错
        print("\n\n已退出，下次再来玩～")


# 这是 Python 的固定写法：只有直接运行本文件时才会执行 main()，
# 如果本文件被别的程序 import 导入，则不会自动开始游戏。
if __name__ == "__main__":
    main()
