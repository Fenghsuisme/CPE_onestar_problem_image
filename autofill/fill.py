import sys
import os
import subprocess
import zipfile
import shutil

def open_nano(filepath):
    subprocess.call(['nano', filepath])

def remove_trailing_empty_lines(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    stripped = content.rstrip('\n')
    with open(filepath, 'w') as f:
        f.write(stripped + '\n' if stripped else '')

def main():
    if len(sys.argv) < 2:
        print("用法: python3 fill.py 資料夾名")
        sys.exit(1)

    folder = sys.argv[1]
    os.makedirs(folder, exist_ok=True)

    index = 1
    while True:
        for ext in ['in', 'out']:
            filename = f"{index}.{ext}"
            filepath = os.path.join(folder, filename)

            print(f"\n正在編輯: {filename}")
            open_nano(filepath)
            remove_trailing_empty_lines(filepath)
            print(f"已儲存: {filename}")

            if ext == 'out':
                ans = input("\n繼續生成下一組？(y 繼續 / 其他停止): ").strip().lower()
                if ans != 'y':
                    script_dir = os.path.dirname(os.path.abspath(__file__))
                    zip_path = os.path.join(script_dir, f"{folder}.zip")
                    with zipfile.ZipFile(zip_path, 'w') as zf:
                        for fname in sorted(os.listdir(folder)):
                            zf.write(os.path.join(folder, fname), fname)
                    done_dir = os.path.join(script_dir, "done")
                    os.makedirs(done_dir, exist_ok=True)
                    shutil.move(folder, os.path.join(done_dir, folder))
                    print(f"已壓縮：{zip_path}")
                    print(f"已移至：done/{folder}")
                    print("停止生成。")
                    sys.exit(0)

        index += 1

if __name__ == '__main__':
    main()
