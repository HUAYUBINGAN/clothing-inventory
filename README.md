# 服装店库存管理系统

本地轻量化的服装店库存管理系统，使用 Python + Flask + SQLite 实现，无需安装复杂数据库。

## 功能特性

- 📊 **库存统计**：商品总数、库存价值、低库存预警
- 🏷️ **分类管理**：添加、修改、删除分类
- 📦 **商品管理**：添加、修改、删除商品，支持搜索
- 💰 **销售记录**：记录销售、采购、调整等交易
- 📈 **数据统计**：实时统计面板
- 💾 **数据持久化**：SQLite 数据库，数据自动保存

## 技术栈

- **Python 3.8+**（本项目用 uv 3.12.15）
- **Flask** - Web 框架
- **SQLite** - 轻量级数据库
- **HTML/CSS/JS** - 前端界面

## 快速开始

### 方式一：一键启动（推荐）

双击项目根目录下的 **`start.bat`** 即可。它会自动用项目虚拟环境（`.venv`，已装好 Flask）启动，无需手动配置依赖。

启动成功后打开浏览器访问：`http://127.0.0.1:5000`

### 方式二：手动启动（用虚拟环境）

依赖装在项目的 `.venv` 虚拟环境里。在终端中：

```bash
cd D:\test\clothing-inventory
# 激活虚拟环境
.venv\Scripts\activate
# 运行
python app.py
# 退出虚拟环境
deactivate
```

> **为什么不用全局 `pip install`？**
> 你终端里的 `python` 是 uv 管理的，它禁止往全局环境装包（报 `externally-managed-environment`，PEP 668 设计行为）。依赖应装到项目 `.venv` 里，这样各项目互不干扰。

## 项目结构

```
clothing-inventory/
├── app.py              # 主应用文件
├── requirements.txt    # 依赖列表
├── .venv/              # 虚拟环境（已装 Flask）
├── templates/
│   └── index.html      # 前端页面
├── data/
│   └── inventory.db    # 数据库文件
├── start.bat           # 一键启动脚本
└── README.md           # 说明文档
```

## API 接口

### 统计

- `GET /api/stats` - 获取库存统计

### 分类

- `GET /api/categories` - 获取所有分类
- `POST /api/categories` - 创建分类
- `PUT /api/categories/<id>` - 更新分类
- `DELETE /api/categories/<id>` - 删除分类

### 商品

- `GET /api/products` - 获取所有商品
- `POST /api/products` - 创建商品
- `PUT /api/products/<id>` - 更新商品
- `DELETE /api/products/<id>` - 删除商品

### 交易

- `GET /api/transactions` - 获取所有交易
- `POST /api/transactions` - 创建交易

## 数据库设计

### categories 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| name | TEXT | 分类名 |
| description | TEXT | 分类描述 |

### products 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| name | TEXT | 商品名 |
| sku | TEXT | 商品编号 |
| category_id | INTEGER | 分类ID |
| unit | TEXT | 单位（默认"件"） |
| price | REAL | 售价 |
| cost | REAL | 成本 |
| quantity | INTEGER | 库存数量 |
| low_stock_threshold | INTEGER | 低库存预警阈值 |
| created_at | TEXT | 创建时间 |
| updated_at | TEXT | 更新时间 |

### transactions 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| product_id | INTEGER | 商品ID |
| type | TEXT | 类型（sale/purchase/adjust） |
| quantity | INTEGER | 数量 |
| unit_price | REAL | 单价 |
| total | REAL | 总额 |
| customer | TEXT | 客户 |
| created_at | TEXT | 创建时间 |

## 使用说明

### 添加商品

1. 点击"添加商品"按钮
2. 填写 SKU、分类、价格、成本、库存
3. 点击保存

### 销售商品

1. 点击"销售记录"
2. 选择商品、填写数量
3. 确认销售

### 搜索

在搜索框输入 SKU 或商品名，实时过滤列表。

## 常见问题

### Q: 为什么 `pip install` 报 `externally-managed-environment`？

A: 你的全局 `python` 是 uv 管理的，它禁止往全局环境装包（PEP 668 设计行为）。正确做法是用项目的 `.venv` 虚拟环境装依赖，或双击 `start.bat` 一键启动。

### Q: 如何备份数据？

A: 直接复制 `data/inventory.db` 文件即可。

### Q: 如何导入数据？

A: 使用 SQLite 工具导入 CSV。

### Q: 支持多用户吗？

A: 当前为单用户模式，可后续扩展。

## 许可证

MIT License
