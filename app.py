from flask import Flask, render_template, flash, redirect, url_for, session, request
import os
import sys
import socket
import webbrowser
from forms import ArticleForm, RegisterForm
from mysql_util import MysqlUtil
from portabledb import init_database

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key'
    
    # 路由和视图函数定义
    @app.route('/')
    def index():
        return render_template('index.html')
    
    # 其他路由...
    
    return app

def get_free_port():
    sock = socket.socket()
    sock.bind(('', 0))
    port = sock.getsockname()[1]
    sock.close()
    return port

def init_db():
    try:
        db = MysqlUtil()
        with open('notebook.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()
            # 分割SQL命令，但保留CREATE TABLE语句的完整性
            sql_commands = [cmd.strip() for cmd in sql_script.split(';') if cmd.strip()]
            
            for command in sql_commands:
                try:
                    if 'CREATE TABLE' in command.upper():
                        # 如果是CREATE TABLE语句，添加IF NOT EXISTS
                        command = command.replace('CREATE TABLE', 'CREATE TABLE IF NOT EXISTS')
                    db.execute(command + ';')
                except Exception as e:
                    if 'already exists' not in str(e).lower():
                        print(f"执行SQL命令失败：{e}\nSQL: {command}")
                        
    except Exception as e:
        print(f"初始化数据库失败：{e}")
        # 不抛出异常，让应用继续运行

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
    init_database(db_path)
    
    # 初始化数据库表
    init_db()
    
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
