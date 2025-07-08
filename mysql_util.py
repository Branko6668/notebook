import pymysql   # 引入pymysql模块
import traceback # 引入python中的traceback模块，跟踪错误
import sys       # 引入sys模块

class MysqlUtil():
    def __init__(self):
        self.db = None
        self.cursor = None
        self.connect()

    def connect(self):
        try:
            # 先尝试不指定数据库连接
            self.db = pymysql.connect(
                host="localhost",
                user="root",
                password="200249",
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            self.cursor = self.db.cursor()
            
            # 测试连接
            self.cursor.execute("SELECT VERSION()")
            version = self.cursor.fetchone()
            print(f"MySQL版本: {version}")
            
            # 创建数据库（如果不存在）
            self.cursor.execute("CREATE DATABASE IF NOT EXISTS notebook DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            self.cursor.execute("USE notebook")
            
            # 测试数据库是否可用
            self.cursor.execute("SHOW TABLES")
            tables = self.cursor.fetchall()
            print(f"当前表: {tables}")
            
        except Exception as e:
            print(f"数据库连接失败：{e}")
            raise
        finally:
            if self.cursor:
                self.cursor.close()
            if self.db:
                self.db.close()
            
            # 重新连接到指定的数据库
            self.db = pymysql.connect(
                host="localhost",
                user="root",
                password="200249",
                database="notebook",
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            self.cursor = self.db.cursor()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.db and self.db.open:
            self.db.close()

    def execute(self, sql):
        try:
            if not self.db or not self.db.open:
                self.connect()
            self.cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise
        finally:
            self.close()

    def fetchall(self, sql):
        try:
            if not self.db or not self.db.open:
                self.connect()
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            print(f"查询失败：{e}")
            return None
        finally:
            self.close()

    def fetchone(self, sql):
        try:
            if not self.db or not self.db.open:
                self.connect()
            self.cursor.execute(sql)
            result = self.cursor.fetchone()
            return result
        except Exception as e:
            print(f"查询失败：{e}")
            return None
        finally:
            self.close()

    def insert(self, sql):
        try:
            if not self.db or not self.db.open:
                self.connect()
            self.cursor.execute(sql)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(f"插入失败：{e}")
            print(f"SQL语句：{sql}")
            # 打印完整的错误堆栈
            import traceback
            traceback.print_exc()
            return False
        finally:
            self.close()

    def update(self, sql):
        try:
            self.execute(sql)
            return True
        except Exception as e:
            print(f"更新失败：{e}")
            return False

    def delete(self, sql):
        try:
            self.execute(sql)
            return True
        except Exception as e:
            print(f"删除失败：{e}")
            return False

    def insert_with_params(self, sql, params):
        try:
            if not self.db or not self.db.open:
                self.connect()
            self.cursor.execute(sql, params)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(f"参数化插入失败：{e}")
            print(f"SQL语句：{sql}")
            print(f"参数：{params}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            self.close()

    def fetchall_with_params(self, sql, params):
        try:
            if not self.db or not self.db.open:
                self.connect()
            self.cursor.execute(sql, params)
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            print(f"参数化查询失败：{e}")
            print(f"SQL语句：{sql}")
            print(f"参数：{params}")
            return None
        finally:
            self.close()

    def fetchone_with_params(self, sql, params):
        try:
            if not self.db or not self.db.open:
                self.connect()
            self.cursor.execute(sql, params)
            result = self.cursor.fetchone()
            return result
        except Exception as e:
            print(f"参数化查询失败：{e}")
            print(f"SQL语句：{sql}")
            print(f"参数：{params}")
            return None
        finally:
            self.close()

    def execute_with_params(self, sql, params):
        try:
            if not self.db or not self.db.open:
                self.connect()
            self.cursor.execute(sql, params)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(f"参数化执行失败：{e}")
            print(f"SQL语句：{sql}")
            print(f"参数：{params}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            self.close()