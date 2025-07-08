import sys
import os
import webbrowser

def main():
    # 获取程序运行路径
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))
    
    # 初始化便携式数据库
    db_path = os.path.join(application_path, 'data')
    os.makedirs(db_path, exist_ok=True)
    
    # 启动便携式 MySQL
    portabledb.init_database(db_path)
    
    # 获取可用端口
    port = get_free_port()
    
    # 启动应用
    app = create_app()
    url = f'http://localhost:{port}'
    
    # 打开浏览器
    webbrowser.open(url)
    
    print(f'笔记本已启动，请访问: {url}')
    app.run(port=port)

if __name__ == '__main__':
    main() 