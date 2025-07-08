import os
import subprocess
import atexit
import time
import pymysql
from pymysql.constants import CLIENT

class PortableMySQL:
    def __init__(self, base_path):
        self.base_path = base_path
        self.mysql_path = os.path.join(base_path, 'mysql')
        self.data_path = os.path.join(base_path, 'data')
        self.mysql_process = None

    def init_database(self):
        # 初始化数据库文件
        if not os.path.exists(self.data_path):
            self._initialize_mysql()
        
        # 启动 MySQL
        self._start_mysql()
        
        # 注册程序退出时关闭数据库
        atexit.register(self._stop_mysql)
        
        # 等待数据库启动
        self._wait_for_mysql()

    def _initialize_mysql(self):
        # 初始化 MySQL 数据目录
        subprocess.run([
            os.path.join(self.mysql_path, 'bin', 'mysqld'),
            '--initialize-insecure',
            f'--datadir={self.data_path}'
        ])

    def _start_mysql(self):
        # 启动 MySQL 服务器
        self.mysql_process = subprocess.Popen([
            os.path.join(self.mysql_path, 'bin', 'mysqld'),
            f'--datadir={self.data_path}',
            '--skip-networking=0',
            '--port=3306'
        ])

    def _stop_mysql(self):
        if self.mysql_process:
            self.mysql_process.terminate()
            self.mysql_process.wait()

    def _wait_for_mysql(self):
        max_attempts = 30
        for _ in range(max_attempts):
            try:
                conn = pymysql.connect(
                    host='localhost',
                    user='root',
                    password='',
                    client_flag=CLIENT.MULTI_STATEMENTS
                )
                conn.close()
                return
            except pymysql.Error:
                time.sleep(1)
        raise Exception("MySQL 启动失败")

def init_database(base_path):
    mysql = PortableMySQL(base_path)
    mysql.init_database() 