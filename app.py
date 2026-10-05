#!/usr/bin/env python3
"""
服装店库存管理系统
本地轻量级，使用 Flask + SQLite
"""

import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, jsonify

# 项目路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'inventory.db')

# 初始化 Flask 应用
app = Flask(__name__)

# 确保数据目录存在
os.makedirs(DATA_DIR, exist_ok=True)


def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化数据库表"""
    conn = get_db()
    cursor = conn.cursor()
    
    # 创建分类表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            created_at TEXT DEFAULT (datetime('now'))
        )
    ''')
    
    # 创建商品表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            category_id INTEGER,
            price REAL NOT NULL DEFAULT 0,
            cost REAL NOT NULL DEFAULT 0,
            quantity INTEGER NOT NULL DEFAULT 0,
            low_stock_threshold INTEGER NOT NULL DEFAULT 10,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )
    ''')
    
    # 创建交易表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            type TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            note TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')
    
    conn.commit()
    conn.close()


@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')


# ==================== 统计 API ====================

@app.route('/api/stats')
def get_stats():
    """获取库存统计"""
    conn = get_db()
    cursor = conn.cursor()
    
    # 商品总数
    cursor.execute('SELECT COUNT(*) as total FROM products')
    total_products = cursor.fetchone()['total']
    
    # 库存总数
    cursor.execute('SELECT COALESCE(SUM(quantity), 0) as total FROM products')
    total_quantity = cursor.fetchone()['total']
    
    # 库存价值
    cursor.execute('SELECT COALESCE(SUM(quantity * price), 0) as total FROM products')
    total_value = cursor.fetchone()['total']
    
    # 低库存商品
    cursor.execute('''
        SELECT COUNT(*) as total 
        FROM products 
        WHERE quantity > 0 AND quantity <= low_stock_threshold
    ''')
    low_stock_count = cursor.fetchone()['total']
    
    # 缺货商品
    cursor.execute('SELECT COUNT(*) as total FROM products WHERE quantity = 0')
    out_of_stock_count = cursor.fetchone()['total']
    
    # 销售总额
    cursor.execute('''
        SELECT COALESCE(SUM(t.quantity * p.price), 0) as total 
        FROM transactions t
        JOIN products p ON t.product_id = p.id
        WHERE t.type = 'sale'
    ''')
    total_sales = cursor.fetchone()['total']
    
    conn.close()
    
    return jsonify({
        'total_products': total_products,
        'total_quantity': total_quantity,
        'total_value': round(total_value, 2),
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
        'total_sales': round(total_sales, 2)
    })


# ==================== 分类 API ====================

@app.route('/api/categories')
def get_categories():
    """获取所有分类"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM categories ORDER BY id')
    categories = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({'categories': categories})


@app.route('/api/categories', methods=['POST'])
def create_category():
    """创建分类"""
    data = request.get_json()
    name = data.get('name', '').strip()
    
    if not name:
        return jsonify({'error': '分类名称不能为空'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('INSERT INTO categories (name) VALUES (?)', (name,))
        conn.commit()
        category_id = cursor.lastrowid
        conn.close()
        return jsonify({'id': category_id, 'name': name}), 201
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': '分类已存在'}), 400


@app.route('/api/categories/<int:id>', methods=['PUT'])
def update_category(id):
    """更新分类"""
    data = request.get_json()
    name = data.get('name', '').strip()
    
    if not name:
        return jsonify({'error': '分类名称不能为空'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('UPDATE categories SET name = ? WHERE id = ?', (name, id))
        conn.commit()
        conn.close()
        return jsonify({'id': id, 'name': name})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': '分类名已存在'}), 400


@app.route('/api/categories/<int:id>', methods=['DELETE'])
def delete_category(id):
    """删除分类"""
    conn = get_db()
    cursor = conn.cursor()
    
    # 检查是否有商品使用该分类
    cursor.execute('SELECT COUNT(*) as count FROM products WHERE category_id = ?', (id,))
    count = cursor.fetchone()['count']
    
    if count > 0:
        conn.close()
        return jsonify({'error': f'该分类下有 {count} 个商品，无法删除'}), 400
    
    cursor.execute('DELETE FROM categories WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'message': '删除成功'})


# ==================== 商品 API ====================

@app.route('/api/products')
def get_products():
    """获取所有商品"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.*, c.name as category_name
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        ORDER BY p.id DESC
    ''')
    products = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(products)


@app.route('/api/products', methods=['POST'])
def create_product():
    """创建商品"""
    data = request.get_json()
    
    sku = data.get('sku', '').strip()
    name = data.get('name', '').strip()
    category_id = data.get('category_id')
    price = float(data.get('price', 0))
    cost = float(data.get('cost', 0))
    quantity = int(data.get('quantity', 0))
    low_stock_threshold = int(data.get('low_stock_threshold', 10))
    
    if not sku:
        return jsonify({'error': 'SKU 不能为空'}), 400
    if not name:
        return jsonify({'error': '商品名称不能为空'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO products (sku, name, category_id, price, cost, quantity, low_stock_threshold)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (sku, name, category_id, price, cost, quantity, low_stock_threshold))
        conn.commit()
        product_id = cursor.lastrowid
        conn.close()
        return jsonify({'id': product_id, 'message': '创建成功'}), 201
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'SKU 已存在'}), 400


@app.route('/api/products/<int:id>', methods=['PUT'])
def update_product(id):
    """更新商品"""
    data = request.get_json()
    
    sku = data.get('sku')
    name = data.get('name')
    category_id = data.get('category_id')
    price = data.get('price')
    cost = data.get('cost')
    quantity = data.get('quantity')
    low_stock_threshold = data.get('low_stock_threshold')
    
    updates = []
    params = []
    
    if sku is not None:
        updates.append('sku = ?')
        params.append(sku)
    if name is not None:
        updates.append('name = ?')
        params.append(name)
    if category_id is not None:
        updates.append('category_id = ?')
        params.append(category_id)
    if price is not None:
        updates.append('price = ?')
        params.append(float(price))
    if cost is not None:
        updates.append('cost = ?')
        params.append(float(cost))
    if quantity is not None:
        updates.append('quantity = ?')
        params.append(int(quantity))
    if low_stock_threshold is not None:
        updates.append('low_stock_threshold = ?')
        params.append(int(low_stock_threshold))
    
    if not updates:
        return jsonify({'error': '没有可更新的数据'}), 400
    
    updates.append('updated_at = ?')
    params.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    params.append(id)
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(f'UPDATE products SET {", ".join(updates)} WHERE id = ?', params)
        conn.commit()
        conn.close()
        return jsonify({'message': '更新成功'})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'SKU 已存在'}), 400


@app.route('/api/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    """删除商品"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM products WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'message': '删除成功'})


# ==================== 交易 API ====================

@app.route('/api/transactions')
def get_transactions():
    """获取交易记录"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT t.*, p.name as product_name
        FROM transactions t
        LEFT JOIN products p ON t.product_id = p.id
        ORDER BY t.id DESC
        LIMIT 100
    ''')
    transactions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(transactions)


@app.route('/api/transactions', methods=['POST'])
def create_transaction():
    """创建交易记录"""
    data = request.get_json()
    
    product_id = data.get('product_id')
    t_type = data.get('type')
    quantity = int(data.get('quantity', 0))
    note = data.get('note', '').strip()
    
    if not product_id:
        return jsonify({'error': '商品ID不能为空'}), 400
    if t_type not in ['sale', 'purchase', 'adjust']:
        return jsonify({'error': '交易类型无效'}), 400
    if quantity <= 0:
        return jsonify({'error': '数量必须大于0'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    # 获取商品当前库存
    cursor.execute('SELECT quantity FROM products WHERE id = ?', (product_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return jsonify({'error': '商品不存在'}), 404
    
    current_quantity = row['quantity']
    
    # 销售：检查库存是否足够
    if t_type == 'sale' and current_quantity < quantity:
        conn.close()
        return jsonify({'error': f'库存不足，当前库存：{current_quantity}'}), 400
    
    # 更新库存
    if t_type == 'sale':
        new_quantity = current_quantity - quantity
    elif t_type == 'purchase':
        new_quantity = current_quantity + quantity
    else:  # adjust
        new_quantity = current_quantity + quantity
    
    # 插入交易记录
    cursor.execute('''
        INSERT INTO transactions (product_id, type, quantity, note)
        VALUES (?, ?, ?, ?)
    ''', (product_id, t_type, quantity, note))
    
    # 更新商品库存
    cursor.execute('UPDATE products SET quantity = ?, updated_at = ? WHERE id = ?', 
                  (new_quantity, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), product_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': '交易成功', 'new_quantity': new_quantity}), 201


# ==================== 启动 ====================

if __name__ == '__main__':
    init_db()
    print('👕 服装店库存管理系统启动中...')
    print('访问 http://127.0.0.1:5000')
    app.run(debug=False, host='0.0.0.0', port=5000)
