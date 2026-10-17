# -*- coding: utf-8 -*-
"""
猜数字小游戏 · 命令行版
========================================================
两种玩法：
  1. 我猜电脑 —— 电脑随机出题，你输入数字猜
  2. 电脑猜我 —— 你心里想一个数，电脑用二分法猜

运行方法：
  1) 按 Win + R，输入 cmd，回车，打开「命令提示符」
  2) 用 cd 命令进入本文件所在的文件夹，例如：
         cd /d C:\\Users\\Maryn\\WorkBuddy\\2026-10-16-22-16-10
  3) 运行本文件：
         python guess_number.py

代码结构（从上往下读就是完整逻辑）：
  一、常量       —— 想改规则只改这里
  二、通用工具   —— 分隔线、算次数上限、读输入、读反馈、选菜单
  三、玩法一     —— play_player_guesses()
  四、玩法二     —— play_computer_guesses()
  五、主流程     —— main()
========================================================
"""

import math
import random

# ==================================================
# 一、常量：想改规则，只动这一段
# ==================================================

# 三个难度：编号 -> (名字, 最小值, 最大值)
LEVELS = {
    1: ("简单", 1, 50),
    2: ("普通", 1, 100),
    3: ("困难", 1, 1000),
}

# 输入这些词就退出游戏
EXIT_WORDS = {"q", "quit", "exit", "退出"}

# 电脑猜你时，你的回答可以有多种写法，都能认出来
SAY_BIG = {"大", "大了", "d", "big"}                       # 我猜大了，答案更小
SAY_SMALL = {"小", "小了", "x", "small"}                   # 我猜小了，答案更大
SAY_HIT = {"中", "中了", "对", "对了", "y", "yes", "ok"}    # 猜对了


# ==================================================
# 二、通用小工具
# ==================================================

def hr(char="=", width=34):
    """打印一条分隔线，让输出看起来整齐。"""
    print(char * width)


def banner(text):
    """打印一个带上下分隔线的小标题。

    这里没有用 f"{text:^32}" 去居中，因为中文字符在命令行里占两个字符宽，
    Python 按字符个数补空格算不准，反而会歪。统一左缩进 2 格最整齐。
    """
    hr()
    print("  " + text)
    hr()


def max_attempts(low, high):
    """算出这个范围「理论上最多几次就能猜到」，再留 1 次余量。

    原理：每次猜中间值都能排除掉一半，所以次数 = log2(一共有多少个数)。
        1~50    共 50 个  → log2(50)  ≈ 5.64 → 向上取整 6 次
        1~100   共 100 个 → log2(100) ≈ 6.64 → 向上取整 7 次
        1~1000  共 1000 个→ log2(1000)= 9.97 → 向上取整 10 次

    末尾 +1 是故意放宽的：不要求玩家每一步都走最优路线，
    否则这游戏会变成「一步错、满盘输」，太苛刻了。
    """
    total = high - low + 1
    return math.ceil(math.log2(total)) + 1


def read_guess(low, high):
    """读取玩家输入的一个数字，并做检查。

    返回值是一个「元组」，用第一个元素表示结果状态：
        ("ok",    数字)   输入合法，可以拿去比较
        ("exit",  None)   玩家输入了 q，想退出游戏
        ("error", None)   输入不合法，本次不算次数，需要重新输入
    """
    text = input(f"请猜一个 {low} ~ {high} 的数字：").strip()

    if text.lower() in EXIT_WORDS:              # 想退出？
        return "exit", None

    try:
        guess = int(text)                       # 把输入的文字转成整数
    except ValueError:                          # 转不了（比如输入了 abc）
        print("  输入有误：只能输入整数，请重新输入\n")
        return "error", None

    if guess < low or guess > high:             # 数字超范围
        print(f"  输入有误：请输入 {low} ~ {high} 之间的数字\n")
        return "error", None

    return "ok", guess


def read_feedback():
    """电脑猜你的时候，读你的回答，返回 big / small / hit / exit。"""
    while True:
        text = input("  你回答（大 / 小 / 中，q 退出）：").strip().lower()

        if text in EXIT_WORDS:
            return "exit"
        if text in SAY_BIG:
            return "big"
        if text in SAY_SMALL:
            return "small"
        if text in SAY_HIT:
            return "hit"

        print("  没听懂，请输入「大」「小」「中」其中之一。")


def choose_mode():
    """选玩法，返回 "player" / "computer"；返回 None 表示想退出。"""
    hr()
    print("  1) 我猜电脑 —— 电脑出题，你来猜")
    print("  2) 电脑猜我 —— 你想数字，电脑来猜")
    print("  q) 退出")
    hr()

    while True:
        choice = input("请选择玩法（1 / 2）：").strip().lower()

        if choice in EXIT_WORDS:
            return None
        if choice == "1":
            return "player"
        if choice == "2":
            return "computer"

        print("  只能输入 1 或 2 哦。")


def choose_level():
    """选难度，返回 (名字, 最小值, 最大值)；输入 q 返回 None。"""
    print("\n请选择难度：")
    for key, (name, low, high) in LEVELS.items():
        print(f"  {key}) {name}   {low} ~ {high}   最多 {max_attempts(low, high)} 次机会")

    while True:
        choice = input("请输入 1 / 2 / 3：").strip().lower()

        if choice in EXIT_WORDS:
            return None
        if choice in ("1", "2", "3"):
            return LEVELS[int(choice)]

        print("  只能输入 1、2 或 3 哦。")


# ==================================================
# 三、玩法一：电脑出题，你来猜
# ==================================================

def play_player_guesses(level_name, low, high):
    """玩一局「我猜电脑」，返回 (结果, 猜了几次, 答案)。

    结果有三种：
        "win"   猜中了
        "lose"  次数用完还没猜中
        "exit"  玩家中途输入 q 退出
    """
    answer = random.randint(low, high)      # 第 1 步：电脑出题
    limit = max_attempts(low, high)         # 本局允许的次数上限
    count = 0                               # 已经猜了几次
    win_low, win_high = low, high           # 根据提示推断出的范围（小彩蛋）

    banner(f"我猜电脑 · {level_name}")
    print(f"我心里想了一个 {low} ~ {high} 的整数。")
    print(f"你最多可以猜 {limit} 次，随时输入 q 可以退出。\n")

    while count < limit:                    # 第 2 步：反复猜，直到猜中或次数用完
        status, guess = read_guess(low, high)

        if status == "exit":
            return "exit", count, answer
        if status == "error":
            continue                        # 输入不合法，不计次数，重新输入

        count += 1                          # 猜了一次，次数加 1

        # 第 3 步：比较大小，给出提示
        if guess > answer:
            win_high = min(win_high, guess - 1)     # 答案肯定比 guess 小
            print("  → 大了 ↓   再猜小一点")
        elif guess < answer:
            win_low = max(win_low, guess + 1)       # 答案肯定比 guess 大
            print("  → 小了 ↑   再猜大一点")
        else:
            return "win", count, answer             # 猜中了，本局结束

        print(f"  已猜 {count}/{limit} 次   可能范围：{win_low} ~ {win_high}\n")

    return "lose", count, answer


# ==================================================
# 四、玩法二：你心里想数字，电脑来猜
# ==================================================

def play_computer_guesses(level_name, low, high):
    """玩一局「电脑猜我」，返回 (结果, 猜了几次, 电脑最后猜的数)。

    结果有四种：
        "win"    电脑猜中了
        "lose"   次数用完还没猜中
        "cheat"  你的回答前后矛盾（范围被压成空的）
        "exit"   你中途输入 q 退出
    """
    limit = max_attempts(low, high)
    count = 0
    guess_low, guess_high = low, high       # 电脑当前认为的答案范围
    last_guess = None                       # 记住最后一次猜的数字

    banner(f"电脑猜我 · {level_name}")
    print(f"请在心里想一个 {low} ~ {high} 的整数，不要告诉我。")
    print("我每猜一个，你就回答：")
    print("  大 = 我猜大了（答案更小）")
    print("  小 = 我猜小了（答案更大）")
    print("  中 = 我猜对了\n")

    ready = input("想好了就按回车开始（输入 q 退出）：").strip().lower()
    if ready in EXIT_WORDS:
        return "exit", count, None

    # 只要范围还没空、次数还没用完，就继续猜
    while count < limit and guess_low <= guess_high:
        guess = (guess_low + guess_high) // 2     # 取中点，这就是二分法
        last_guess = guess
        count += 1

        print(f"\n  第 {count}/{limit} 次，我猜：{guess}")
        feedback = read_feedback()

        if feedback == "exit":
            return "exit", count, guess
        if feedback == "hit":
            return "win", count, guess
        if feedback == "big":            # 你说「大了」→ 答案比 guess 小
            guess_high = guess - 1
        else:                            # 你说「小了」→ 答案比 guess 大
            guess_low = guess + 1

        # 只有在范围还没被压空的时候才提示剩余区间，
        # 否则会打印出「1 ~ 0」这种看着很怪的东西
        if guess_low <= guess_high:
            print(f"     那答案就在 {guess_low} ~ {guess_high} 之间，"
                  f"我还剩 {limit - count} 次机会")

    if guess_low > guess_high:
        return "cheat", count, last_guess       # 范围被压空 = 回答自相矛盾
    return "lose", count, last_guess


# ==================================================
# 五、主流程
# ==================================================

def print_result(result, count, answer, limit, is_player):
    """把一局的结果打印成一个框。"""
    hr()

    if result == "win":
        if is_player:
            print(f"  猜中啦！答案就是 {answer}")
            print(f"  你一共猜了 {count} 次（上限 {limit} 次）")
        else:
            print(f"  猜对啦！你心里想的是 {answer}")
            print(f"  我只用了 {count} 次")

        if count <= limit - 1:      # 在理论最优次数内结束
            print("  这已经是很漂亮的成绩了 👍")

    elif result == "lose":
        if is_player:
            print(f"  次数用完了，答案是 {answer}")
            print(f"  提示：每次都猜中间值，最多 {limit - 1} 次就能猜到")
        else:
            print("  我没猜出来……你是不是中途改过答案？")

    elif result == "cheat":
        print("  你的回答前后矛盾了，我的范围被压成了空的。")
        print("  下次回答的时候按顺序来，就不会这样了 😄")

    hr()


def main():
    """程序入口：开场白 → 循环「选玩法 → 玩一局 → 要不要再来」。"""
    print()
    banner("猜 数 字 小 游 戏")
    print("两种玩法随便挑，任何时候输入 q 都能退出。\n")

    while True:                         # 外层循环：控制「要不要再来一局」
        mode = choose_mode()
        if mode is None:
            print("\n已退出，下次再来玩～")
            return

        level = choose_level()
        if level is None:
            print("\n已退出，下次再来玩～")
            return

        level_name, low, high = level
        limit = max_attempts(low, high)
        print()

        # 根据玩法调用不同的函数。两个函数的返回值格式是统一的，
        # 所以后面处理结果的代码只需要写一份。
        if mode == "player":
            result, count, answer = play_player_guesses(level_name, low, high)
        else:
            result, count, answer = play_computer_guesses(level_name, low, high)

        if result == "exit":
            print("\n已退出，下次再来玩～")
            return

        print_result(result, count, answer, limit, mode == "player")

        again = input("再来一局？（直接回车 = 再来，输入 n = 结束）：").strip().lower()
        if again == "n":
            print("拜拜～")
            return
        print()


# 这是 Python 的固定写法：只有直接运行本文件时才会执行 main()，
# 如果本文件被别的程序 import 导入，则不会自动开始游戏。
if __name__ == "__main__":
    # 最外层的兜底：按 Ctrl + C 或者输入流被意外断开时，
    # 看到的是这句中文提示，而不是一长串红色报错。
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n\n已退出，下次再来玩～")
