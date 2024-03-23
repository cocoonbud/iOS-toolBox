import os
import re
import threading
import time

stop_animation = False

def display_loading_animation():
    global stop_animation
    count = 1
    while not stop_animation:
        print(f"\r\033[32mSearching..." + "." * count + "\033[0m", end="")
        count = (count % 11) + 1
        time.sleep(0.5)

def find_macros(directory, macros):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(('.m', '.mm', '.h')):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                    for index, line in enumerate(lines, start=1):
                        if line.strip().startswith('//'):
                            continue

                        match = re.match(r'#define (\w+)', line)
                        if match:
                            macro_name = match.group(1)
                            macros[macro_name] = {'count': 0, 'file': file_path, 'line': index}

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(('.m', '.mm', '.h')):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                    for line in lines:
                        if line.strip().startswith('//'):
                            continue

                        for macro, info in macros.items():
                            if macro in line:
                                info['count'] += 1

def main():
    global stop_animation
    directory = input("请输入文件目录：")
    output_directory = input("请输入输出文件的目录：")
    output_file_path = os.path.join(output_directory, 'unused_macro.txt')
    macros = {}

    loading_thread = threading.Thread(target=display_loading_animation)
    loading_thread.start()

    find_macros(directory, macros)

    stop_animation = True
    loading_thread.join()

    # 输出未使用的宏定义及其位置到文件
    with open(output_file_path, 'w') as output_file:
        output_file.write("未使用的宏定义：\n")
        unused_macros = [macro for macro, info in macros.items() if info['count'] == 1]
        for macro in unused_macros:
            output_file.write(f"{macro} 定义位置： {macros[macro]['file']}:{macros[macro]['line']}\n")

    print(f"未使用的宏定义已写入到文件 {output_file_path}")

    # 自动打开输出文件
    os.system(f"open {output_file_path}")

if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    print(f"\n总的查找时间：{end_time - start_time} 秒")
