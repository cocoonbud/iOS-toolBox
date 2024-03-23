import os
import time

def find_header_refs(file_path):
    header_refs = []
    seen_headers = set()  # 用以记录已经出现过的引用头文件
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith('#import "') or line.startswith('#import <'):
                header_ref = line
                header = extract_header_name(header_ref)
                if header not in seen_headers:
                    header_refs.append(header_ref)
                    seen_headers.add(header)
    return header_refs

def extract_header_name(header_ref):
    if '"' in header_ref:
        return header_ref.split('"')[1].split('.')[0].lower()
    elif '<' in header_ref:
        return header_ref.split('<')[1].split('/')[0].split('.')[0].lower()

def sort_and_group_headers(header_refs):
    header_groups = {'view': [], 'cell': [], 'btn': [], 'vc': [], 'model': [], 'helper': [], 'plus': [], 'others': []}

    for header_ref in header_refs:
        header = extract_header_name(header_ref)

        if header.endswith('view'):
            header_groups['view'].append(header_ref)
        elif header.endswith('cell'):
            header_groups['cell'].append(header_ref)
        elif any(header.endswith(suffix) for suffix in ['btn', 'button']):
            header_groups['btn'].append(header_ref)
        elif any(header.endswith(suffix) for suffix in ['vc', 'viewcontroller', 'controller']):
            header_groups['vc'].append(header_ref)
        elif header.endswith('model'):
            header_groups['model'].append(header_ref)
        elif any(substring in header for substring in ['helper', 'manager']):
            header_groups['helper'].append(header_ref)
        elif '+' in header:
            header_groups['plus'].append(header_ref)
        else:
            header_groups['others'].append(header_ref)

    sorted_header_groups = [header_groups['view'],
                            header_groups['cell'],
                            header_groups['btn'],
                            header_groups['vc'],
                            header_groups['model'],
                            header_groups['helper'],
                            header_groups['plus']]

    # 对每个组内的头文件引用进行排序
    for group in sorted_header_groups:
        group.sort(key=lambda x: extract_header_name(x))

    header_groups['others'].sort(key=lambda x: extract_header_name(x))
    sorted_header_groups.append(header_groups['others'])

    return sorted_header_groups

def start_processing(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if any(file.endswith(suffix) for suffix in ['.m', '.mm', '.h']):
                file_path = os.path.join(root, file)
                print(f"处理文件: {file_path}")
                header_refs = find_header_refs(file_path)

                # 如果头文件引用数目少于 5 个，则跳过此文件
                if len(header_refs) < 5:
                    print(f"跳过文件 {file_path}，头文件引用数目少于 5 个")
                    continue

                sorted_header_groups = sort_and_group_headers(header_refs)

                # 读取文件内容
                with open(file_path, 'r') as f:
                    lines = f.readlines()

                # 查找插入排序后的起始位置
                first_import_position = -1
                last_import_position = -1
                for i, line in enumerate(lines):
                    if line.startswith('#import "') or line.startswith('#import <'):
                        if first_import_position == -1:
                            first_import_position = i
                        last_import_position = i

                # 删除原始的引用头文件
                del lines[first_import_position:last_import_position + 1]

                count = len(sorted_header_groups)
                # 插入sort后的头文件引用
                for i in range(count):
                    group = sorted_header_groups[i]
                    if group:
                        if i == count - 1:
                            lines.insert(first_import_position, '\n'.join(group) + '\n')
                        else:
                            lines.insert(first_import_position, '\n'.join(group) + '\n' + '\n')
                            first_import_position += 1

                # 把修改后的内容写回文件
                with open(file_path, 'w') as f:
                    f.writelines(lines)

def main():
    target_dir = input("请输入目标文件夹路径: ")
    start_time = time.time()
    start_processing(target_dir)
    end_time = time.time()
    print(f"处理完成，总共耗时: {end_time - start_time:.2f} 秒")

if __name__ == "__main__":
    main()

