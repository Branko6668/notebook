from flask import Flask, render_template, flash, redirect, url_for, session, request, logging, send_from_directory, jsonify
from mysql_util import MysqlUtil
from passlib.hash import sha256_crypt
from functools import wraps
import time
from forms import RegisterForm, ArticleForm
import os
import markdown2

app = Flask(__name__)

# 登录检查装饰器 - 确保这个定义在所有路由之前
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('请先登录', 'danger')
            return redirect(url_for('login'))
    return wrap

# 首页
@app.route('/')
def index():
    if 'logged_in' in session:
        try:
            db = MysqlUtil()
            # 获取用户ID
            user_sql = "SELECT id FROM users WHERE username = %s"
            user = db.fetchone_with_params(user_sql, (session['username'],))
            if not user:
                return redirect(url_for('login'))
            
            # 获取最近笔记
            recent_sql = """
                SELECT a.*, u.username as author_name 
                FROM articles a
                JOIN users u ON a.author_id = u.id
                WHERE a.author_id = %s 
                ORDER BY a.create_date DESC 
                LIMIT 5
            """
            recent_articles = db.fetchall_with_params(recent_sql, (user['id'],)) or []
            
            # 获取收藏笔记
            favorite_sql = """
                SELECT a.*, u.username as author_name, f.create_date as favorite_date
                FROM articles a
                JOIN users u ON a.author_id = u.id
                JOIN favorites f ON a.id = f.article_id
                WHERE f.user_id = %s
                ORDER BY f.create_date DESC 
                LIMIT 5
            """
            favorite_articles = db.fetchall_with_params(favorite_sql, (user['id'],)) or []
            return render_template('home.html', 
                                recent_articles=recent_articles,
                                favorite_articles=favorite_articles)
        except Exception as e:
            print(f"获取数据失败：{e}")
            flash('获取数据失败', 'danger')
            return render_template('home.html', 
                                recent_articles=[],
                                favorite_articles=[])
    return redirect(url_for('login'))

# 关于我们
@app.route('/about')
def about():
    return render_template('about.html') # 渲染模板

# 笔记列表
@app.route('/articles')
@is_logged_in
def articles():
    try:
        db = MysqlUtil()
        # 获取用户ID
        user_sql = "SELECT id FROM users WHERE username = %s"
        user = db.fetchone_with_params(user_sql, (session['username'],))
        if not user:
            return redirect(url_for('login'))
            
        # 获取文章列表
        sql = """
            SELECT a.*, u.username as author_name,
                   CASE WHEN f.id IS NOT NULL THEN 1 ELSE 0 END as is_favorited
            FROM articles a
            JOIN users u ON a.author_id = u.id
            LEFT JOIN favorites f ON a.id = f.article_id AND f.user_id = %s
            WHERE a.author_id = %s
            ORDER BY a.create_date DESC
        """
        articles = db.fetchall_with_params(sql, (user['id'], user['id'])) or []
        return render_template('articles.html', articles=articles)
    except Exception as e:
        print(f"获取笔记失败：{e}")
        flash('获取笔记失败：' + str(e), 'danger')
        return render_template('articles.html', articles=[])

# 笔记详情
@app.route('/article/<string:id>/')
def article(id):
    db = MysqlUtil()
    # 更新访问量
    db.update("UPDATE articles SET views = views + 1 WHERE id = '%s'" % id)
    sql = "SELECT * FROM articles WHERE id = '%s'" % (id)
    article = db.fetchone(sql)
    return render_template('article.html', article=article)


# 用户注册
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form) # 实例化表单类
    if request.method == 'POST' and form.validate(): # 如果提交表单，并字段验证通过
        # 获取字段内容
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data)) # 对密码进行加密

        db = MysqlUtil() # 实例化数据库操作类
        sql = "INSERT INTO users(email,username,password) \
               VALUES ('%s', '%s', '%s')" % (email,username,password) # user表中插入记录
        db.insert(sql)

        flash('您已注册成功，请先登录', 'success') # 闪存信息
        return redirect(url_for('login')) # 跳转到登录页面

    return render_template('register.html', form=form) # 渲染模板

# 用户登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']
        
        db = MysqlUtil()
        sql = "SELECT * FROM users WHERE username = '%s'" % username
        result = db.fetchone(sql)
        
        if result:
            password = result['password']
            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['username'] = username
                flash('登录成功', 'success')
                return redirect(url_for('index'))  # 改为跳转到主页
            else:
                flash('密码错误', 'danger')
                return render_template('login.html')
        else:
            flash('用户名不存在', 'danger')
            return render_template('login.html')
    return render_template('login.html')

# 退出
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('您已成功退出', 'success')   # 闪存信息
    return redirect(url_for('login')) # 跳转到登录页面

# 控制台
@app.route('/dashboard')
@is_logged_in
def dashboard():
    db = MysqlUtil() # 实例化数据库操作类
    sql = "SELECT * FROM articles WHERE author = '%s' ORDER BY create_date DESC" % (session['username']) # 根据用户名查找用户笔记信息
    result = db.fetchall(sql) # 查找所有笔记
    if result: # 如果笔记存在，赋值给articles变量
        return render_template('dashboard.html', articles=result)
    else:      # 如果笔记不存在，提示暂无笔记
        msg = '暂无笔记信息'
        return render_template('dashboard.html', msg=msg)

# 添加笔记
@app.route('/add_article', methods=['GET', 'POST'])
@is_logged_in
def add_article():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        
        if title and content:
            try:
                db = MysqlUtil()
                # 获取用户ID
                user_sql = "SELECT id FROM users WHERE username = %s"
                user = db.fetchone_with_params(user_sql, (session['username'],))
                if not user:
                    flash('用户验证失败，请重新登录', 'danger')
                    return redirect(url_for('login'))
                
                # 插入文章
                sql = """
                    INSERT INTO articles (title, content, author_id) 
                    VALUES (%s, %s, %s)
                """
                if db.insert_with_params(sql, (title, content, user['id'])):
                    flash('创建成功', 'success')
                    return redirect(url_for('articles'))
                else:
                    flash('创建失败：数据库操作失败', 'danger')
                    return render_template('add_article.html')
                    
            except Exception as e:
                print(f"添加笔记失败：{e}")
                flash('创建失败：' + str(e), 'danger')
                return render_template('add_article.html')
        else:
            flash('标题和内容不能为空', 'danger')
            return render_template('add_article.html')
            
    return render_template('add_article.html')

# 编辑笔记
@app.route('/edit_article/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_article(id):
    try:
        db = MysqlUtil()
        # 获取用户ID
        user_sql = "SELECT id FROM users WHERE username = %s"
        user = db.fetchone_with_params(user_sql, (session['username'],))
        if not user:
            flash('用户验证失败', 'danger')
            return redirect(url_for('login'))
        
        # 获取文章信息
        fetch_sql = """
            SELECT a.*, u.username as author_name 
            FROM articles a
            JOIN users u ON a.author_id = u.id
            WHERE a.id = %s AND a.author_id = %s
        """
        article = db.fetchone_with_params(fetch_sql, (id, user['id']))
        
        if not article:
            flash('笔记不存在', 'danger')
            return redirect(url_for('articles'))
        
        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']
            
            if title and content:
                try:
                    update_sql = """
                        UPDATE articles 
                        SET title = %s, content = %s 
                        WHERE id = %s AND author_id = %s
                    """
                    if db.execute_with_params(update_sql, (title, content, id, user['id'])):
                        flash('笔记更新成功', 'success')
                        return redirect(url_for('articles'))
                    else:
                        flash('更新失败', 'danger')
                        return render_template('edit_article.html', article=article)
                except Exception as e:
                    flash('更新失败：' + str(e), 'danger')
                    return render_template('edit_article.html', article=article)
            else:
                flash('标题和内容不能为空', 'danger')
                return render_template('edit_article.html', article=article)
        
        # GET 请求，显示编辑表单
        return render_template('edit_article.html', article=article)
    except Exception as e:
        flash('获取笔记失败：' + str(e), 'danger')
        return redirect(url_for('articles'))

# 删除笔记
@app.route('/delete_article/<string:id>', methods=['POST'])
@is_logged_in
def delete_article(id):
    try:
        db = MysqlUtil()
        # 获取用户ID
        user_sql = "SELECT id FROM users WHERE username = %s"
        user = db.fetchone_with_params(user_sql, (session['username'],))
        if not user:
            return jsonify({'status': 'error', 'message': '用户验证失败'})
        
        # 检查文章是否存在且属于当前用户
        check_sql = """
            SELECT id FROM articles 
            WHERE id = %s AND author_id = %s
        """
        article = db.fetchone_with_params(check_sql, (id, user['id']))
        if not article:
            return jsonify({'status': 'error', 'message': '笔记不存在或无权限删除'})
        
        # 删除文章（favorites表的记录会因为外键约束自动删除）
        sql = "DELETE FROM articles WHERE id = %s AND author_id = %s"
        if db.execute_with_params(sql, (id, user['id'])):
            return jsonify({'status': 'success', 'message': '删除成功'})
        else:
            return jsonify({'status': 'error', 'message': '删除失败'})
    except Exception as e:
        print(f"删除笔记失败：{e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

# 如果还没有这个路由，也添加它
@app.route('/static/<path:filename>')
def serve_static(filename):
    response = send_from_directory('static', filename)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

@app.route('/favorite/<string:id>', methods=['POST'])
@is_logged_in
def favorite_article(id):
    try:
        db = MysqlUtil()
        # 获取用户ID
        user_sql = "SELECT id FROM users WHERE username = %s"
        user = db.fetchone_with_params(user_sql, (session['username'],))
        if not user:
            return jsonify({'status': 'error', 'message': '用户验证失败'})
        
        # 检查文章是否存在
        article_sql = "SELECT id FROM articles WHERE id = %s"
        article = db.fetchone_with_params(article_sql, (id,))
        if not article:
            return jsonify({'status': 'error', 'message': '笔记不存在'})
        
        # 检查是否已收藏
        check_sql = "SELECT id FROM favorites WHERE user_id = %s AND article_id = %s"
        existing = db.fetchone_with_params(check_sql, (user['id'], id))
        
        if existing:
            # 取消收藏
            delete_sql = "DELETE FROM favorites WHERE user_id = %s AND article_id = %s"
            if db.execute_with_params(delete_sql, (user['id'], id)):
                return jsonify({'status': 'success', 'action': 'unfavorited', 'message': '取消收藏成功'})
            else:
                return jsonify({'status': 'error', 'message': '取消收藏失败'})
        else:
            # 添加收藏
            sql = "INSERT INTO favorites(user_id, article_id) VALUES (%s, %s)"
            if db.insert_with_params(sql, (user['id'], id)):
                return jsonify({'status': 'success', 'action': 'favorited', 'message': '收藏成功'})
            else:
                return jsonify({'status': 'error', 'message': '收藏失败'})
    except Exception as e:
        print(f"收藏操作失败：{e}")
        return jsonify({'status': 'error', 'message': str(e)})

# 添加收藏笔记列表路由
@app.route('/favorites')
@is_logged_in
def favorite_list():
    try:
        db = MysqlUtil()
        # 获取用户ID
        user_sql = "SELECT id FROM users WHERE username = %s"
        user = db.fetchone_with_params(user_sql, (session['username'],))
        if not user:
            return redirect(url_for('login'))
            
        sql = """
            SELECT a.*, u.username as author_name, f.create_date as favorite_date,
                   1 as is_favorited
            FROM articles a
            JOIN users u ON a.author_id = u.id
            JOIN favorites f ON a.id = f.article_id
            WHERE f.user_id = %s
            ORDER BY f.create_date DESC
        """
        articles = db.fetchall_with_params(sql, (user['id'],)) or []
        return render_template('favorites.html', articles=articles)
    except Exception as e:
        flash('获取收藏失败：' + str(e), 'danger')
        return render_template('favorites.html', articles=[])

@app.route('/preview/<string:id>')
@is_logged_in
def preview_article(id):
    try:
        db = MysqlUtil()
        # 获取用户ID
        user_sql = "SELECT id FROM users WHERE username = %s"
        user = db.fetchone_with_params(user_sql, (session['username'],))
        if not user:
            return redirect(url_for('login'))
        
        # 获取文章
        sql = """
            SELECT a.*, u.username as author_name 
            FROM articles a
            JOIN users u ON a.author_id = u.id
            WHERE a.id = %s AND a.author_id = %s
        """
        article = db.fetchone_with_params(sql, (id, user['id']))
        
        if article:
            # 将Markdown转换为HTML
            markdown_content = markdown2.markdown(article['content'], extras=['fenced-code-blocks', 'tables'])
            return render_template('preview_article.html', article=article, markdown_content=markdown_content)
        else:
            flash('笔记不存在', 'danger')
            return redirect(url_for('articles'))
    except Exception as e:
        flash('获取笔记失败：' + str(e), 'danger')
        return redirect(url_for('articles'))

def reset_database():
    try:
        db = MysqlUtil()
        # 删除现有表
        db.execute("DROP TABLE IF EXISTS favorites")
        db.execute("DROP TABLE IF EXISTS articles")
        db.execute("DROP TABLE IF EXISTS users")
        
        # 重新创建表
        init_db()
        flash('数据库已重置', 'success')
    except Exception as e:
        flash(f'数据库重置失败：{e}', 'danger')

# 可以添加一个重置路由（仅在开发环境使用）
@app.route('/reset_db')
def reset_db():
    reset_database()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(debug=True)














