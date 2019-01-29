import sys
import threading


class ConsoleProgress:
    def __init__(self):
        self.lock = threading.Lock()
        self.progress = {}

    def on_update(self, start, current, end, length):
        with self.lock:
            progress = self.progress
            progress[(start, end)] = current

            fill = "█"
            not_fill = "-"
            total = 50

            finished = 0
            fill_pos = set()
            s_points = set()
            e_points = set()
            print('\rDownload Progress: ', end='')
            for r, c in progress.items():
                s, e = r
                finished += c - s
                s_points.add(s)
                e_points.add(e)
                i1 = int(s / length * total)
                i2 = int(c / length * total)
                while i1 <= i2:
                    fill_pos.add(i1)
                    i1 += 1
            for num in range(0, total + 1):
                c = fill if num in fill_pos else not_fill
                print(c, end='')
            percent = int(finished / length * 100)
            print(' {}%'.format(percent), end='')
            sys.stdout.flush()
            if finished == length and s_points ^ e_points == {0, length}:
                print('\n')
