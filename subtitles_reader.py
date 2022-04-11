import time
import os


def time_convert(sec):
    minutes = sec // 60
    seconds = sec % 60
    hours = minutes // 60
    minutes = minutes % 60

    return [int(hours), int(minutes), round(seconds, 3)]


def run():
    os.system("cls")
    with open('subs.vtt', 'r', encoding="utf-8") as file:
        lines = file.readlines()
    i = 1

    print("To start press Enter...")
    print("To stop press CTRL+C...")
    input()

    os.system("cls")

    for j in range(5, 0, -1):
        print(f"Starting in {j}")
        time.sleep(1)
        os.system("cls")

    start_time = time.time()
    while True:
        for index in range(len(lines)):
            if str(i) == lines[index].strip():
                end_time = time.time()

                time_lapsed = end_time - start_time
                time_now = time_convert(time_lapsed)

                hours = time_now[0]
                minutes = time_now[1]
                seconds = time_now[2]

                timing_hours = int(lines[index + 1][:2])
                timing_minutes = int(lines[index + 1][3:5])
                timing_seconds = float(lines[index + 1][6:12])

                end_timing_hours = int(lines[index + 1][17:19])
                end_timing_minutes = int(lines[index + 1][20:22])
                end_timing_seconds = float(lines[index + 1][23:29])

                if hours >= timing_hours and minutes >= timing_minutes and seconds >= timing_seconds:
                    # print(end_timing_hours, end_timing_minutes, end_timing_seconds)
                    # print(timing_hours, timing_minutes, timing_seconds)
                    # print(hours, minutes, seconds)

                    print(lines[index + 2] + lines[index + 3], end="")
                    i += 1
                    end_time = round((end_timing_hours * 60 * 60) + (end_timing_minutes * 60) + end_timing_seconds, 3)
                    current_time = round((timing_hours * 60 * 60) + (timing_minutes * 60) + timing_seconds, 3)
                    time.sleep(end_time - current_time - 0.1)
                    if i % 2 == 0:
                        os.system("cls")

        time.sleep(0.01)
