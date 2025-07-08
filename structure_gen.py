import os

def list_tree(path='.', level=0, max_level=2, prefix=''):
    if level > max_level:
        return

    entries = sorted(os.listdir(path))
    for i, entry in enumerate(entries):
        full_path = os.path.join(path, entry)
        connector = '└── ' if i == len(entries) - 1 else '├── '
        print(prefix + connector + entry)

        if os.path.isdir(full_path) and not entry.startswith('.'):
            new_prefix = prefix + ('    ' if i == len(entries) - 1 else '│   ')
            list_tree(full_path, level + 1, max_level, new_prefix)

if __name__ == '__main__':
    print("📁 项目结构（最多 2 层）：\n")
    list_tree('.', max_level=2)
