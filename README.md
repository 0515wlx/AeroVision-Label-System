# AeroVision Label System

飞机图片标注系统 - 一个用于标注飞机图片的 Web 应用，支持多人协作、机型识别、航司标记和机身注册号区域标注。

## 功能特性

### 核心功能
- 📷 **图片标注**：支持多种图片格式（jpg, jpeg, png, gif, bmp, webp）
- ✈️ **机型识别**：预置常见机型数据，支持自定义添加
- 🏢 **航司管理**：预置主要航空公司，支持扩展
- 🎯 **区域标注**：支持标注机身注册号区域（YOLO 格式）
- 📊 **数据统计**：实时统计已标注、未标注和跳过的图片数量
- 🔒 **协作锁定**：多人协作时防止冲突，自动锁定正在标注的图片

### 新增功能 ✨
- ⏭️ **跳过废图**：可以标记废图并永久隐藏，不再显示在待标注列表中
- 📈 **跳过统计**：统计面板显示跳过的图片数量
- 📤 **配置导出**：支持导出航司和机型配置为 JSON 格式

### 数据导出
- **CSV 导出**：导出标注数据为 CSV 格式，支持 Excel 打开
- **YOLO 导出**：导出 YOLO 格式的标注文件（zip 压缩包）
- **配置导出**：导出航司配置（airlines.json）和机型配置（aircraft_types.json）

## 技术栈

### 后端
- **Flask**：轻量级 Web 框架
- **SQLite**：嵌入式数据库
- **Python 3.x**

### 前端
- **Vue 3**：渐进式 JavaScript 框架
- **Vite**：快速的前端构建工具
- **原生 JavaScript**：Canvas 绘图和交互

## 项目结构

```
AeroVision-Label-System/
├── app.py                  # Flask 后端主文件
├── database.py             # 数据库操作模块
├── requirements.txt        # Python 依赖
├── labels.db              # SQLite 数据库
├── .env                   # 环境变量配置（可选）
├── data/                  # 预置数据
│   ├── airlines.json      # 航司数据
│   └── aircraft_types.json # 机型数据
├── images/                # 待标注图片目录
├── labeled/               # 已标注图片目录
└── frontend/              # 前端项目
    ├── index.html
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── App.vue
        ├── main.js
        ├── components/    # Vue 组件
        └── styles/        # 样式文件
```

## 快速开始

### 环境要求
- Python 3.7+
- Node.js 14+
- npm 或 yarn

### 后端安装

1. 克隆项目
```bash
git clone <repository-url>
cd AeroVision-Label-System
```

2. 安装 Python 依赖
```bash
pip install -r requirements.txt
```

3. 配置环境变量（可选）
```bash
# 创建 .env 文件
IMAGES_DIR=./images
LABELED_DIR=./labeled
DATABASE_PATH=./labels.db
FLASK_PORT=5000
FLASK_DEBUG=false
```

4. 启动后端服务
```bash
python app.py
```

后端服务将在 `http://localhost:5000` 启动

### 前端安装

1. 进入前端目录
```bash
cd frontend
```

2. 安装依赖
```bash
npm install
# 或
yarn install
```

3. 启动开发服务器
```bash
npm run dev
# 或
yarn dev
```

4. 构建生产版本
```bash
npm run build
# 或
yarn build
```

前端开发服务器将在 `http://localhost:5173` 启动

## 使用说明

### 1. 准备图片
将待标注的飞机图片放入 `images/` 目录

### 2. 开始标注
1. 在浏览器中打开前端页面
2. 系统会自动分配一个用户 ID（用于协作锁定）
3. 从待标注列表中选择图片
4. 填写标注信息：
   - 机型（必填）
   - 航司（必填）
   - 清晰度（0-1）
   - 遮挡程度（0-1）
   - 机身注册号（必填）
   - 注册号区域（在图片上框选）

### 3. 跳过废图
- 如果遇到无法标注的废图，点击"跳过该图"按钮
- 跳过的图片将永久隐藏，不再显示在待标注列表中
- 统计面板会显示已跳过的图片数量

### 4. 查看统计
统计面板显示：
- 已标注数量
- 未标注数量
- 已跳过数量
- 按机型统计
- 按航司统计

### 5. 导出数据

#### 导出标注数据
- **CSV 格式**：访问 `http://localhost:5000/api/labels/export`
- **YOLO 格式**：访问 `http://localhost:5000/api/labels/export-yolo`

#### 导出配置数据
- **航司配置**：访问 `http://localhost:5000/api/export/airlines`
- **机型配置**：访问 `http://localhost:5000/api/export/aircraft-types`

## API 文档

### 图片相关

#### 获取待标注图片列表
```http
GET /api/images?user_id=<user_id>
```

#### 跳过图片
```http
POST /api/images/skip
Content-Type: application/json

{
  "filename": "image.jpg",
  "user_id": "user123"
}
```

### 标注相关

#### 创建标注
```http
POST /api/labels
Content-Type: application/json

{
  "original_file_name": "image.jpg",
  "type_id": "A320",
  "type_name": "空客A320",
  "airline_id": "CCA",
  "airline_name": "中国国航",
  "clarity": 0.9,
  "block": 0.1,
  "registration": "B-1234",
  "registration_area": "0.5 0.5 0.2 0.1"
}
```

#### 导出标注数据
```http
GET /api/labels/export          # CSV 格式
GET /api/labels/export-yolo     # YOLO 格式
```

### 配置相关

#### 获取航司列表
```http
GET /api/airlines
```

#### 获取机型列表
```http
GET /api/aircraft-types
```

#### 导出配置
```http
GET /api/export/airlines         # 导出航司配置
GET /api/export/aircraft-types   # 导出机型配置
```

### 统计相关

#### 获取统计信息
```http
GET /api/stats
```

返回示例：
```json
{
  "total_labeled": 100,
  "unlabeled": 50,
  "skipped": 10,
  "by_type": {
    "A320": 30,
    "B738": 25
  },
  "by_airline": {
    "CCA": 40,
    "CSN": 35
  }
}
```

## 数据库结构

### labels 表
存储标注记录
- `id`: 主键
- `file_name`: 标注后的文件名
- `original_file_name`: 原始文件名
- `type_id`: 机型代码
- `type_name`: 机型名称
- `airline_id`: 航司代码
- `airline_name`: 航司名称
- `clarity`: 清晰度
- `block`: 遮挡程度
- `registration`: 机身注册号
- `registration_area`: 注册号区域（YOLO 格式）
- `created_at`: 创建时间

### skipped_images 表
存储跳过的废图
- `id`: 主键
- `filename`: 文件名
- `user_id`: 跳过的用户
- `skipped_at`: 跳过时间

### airlines 表
存储航司信息
- `id`: 主键
- `code`: 航司代码（ICAO）
- `name`: 航司名称

### aircraft_types 表
存储机型信息
- `id`: 主键
- `code`: 机型代码
- `name`: 机型名称

### image_locks 表
存储图片锁（用于多人协作）
- `id`: 主键
- `filename`: 文件名
- `user_id`: 锁定的用户
- `locked_at`: 锁定时间

## 文件命名规则

标注后的图片文件命名格式：`{机型代码}-{序号}.{扩展名}`

例如：
- `A320-0001.jpg`
- `B738-0042.png`
- `B77W-0123.jpeg`

序号从 0001 开始，每个机型独立计数。

## 多人协作

### 图片锁机制
- 用户开始标注图片时自动获取锁
- 锁定的图片其他用户无法标注
- 锁定超时时间：10 分钟
- 用户离开页面时自动释放所有锁

### 心跳机制
- 每隔一段时间自动刷新锁的过期时间
- 防止标注过程中锁被意外释放

## 配置说明

### 预置数据
系统预置了常见的航司和机型数据，位于 `data/` 目录：
- `airlines.json`: 包含 40+ 主要航空公司
- `aircraft_types.json`: 包含 50+ 常见机型

### 自定义配置
1. 直接编辑 JSON 文件添加新的航司或机型
2. 重启后端服务，系统会自动加载
3. 也可以通过前端界面动态添加
4. 使用导出功能备份当前配置

### 环境变量
- `IMAGES_DIR`: 待标注图片目录（默认：./images）
- `LABELED_DIR`: 已标注图片目录（默认：./labeled）
- `DATABASE_PATH`: 数据库文件路径（默认：./labels.db）
- `FLASK_PORT`: 后端服务端口（默认：5000）
- `FLASK_DEBUG`: 调试模式（默认：false）

## 常见问题

### Q: 如何批量导入图片？
A: 直接将图片文件复制到 `images/` 目录即可。

### Q: 标注数据保存在哪里？
A: 标注数据保存在 SQLite 数据库（labels.db）中，图片文件移动到 `labeled/` 目录。

### Q: 如何备份数据？
A: 备份以下内容即可：
- `labels.db` 数据库文件
- `labeled/` 目录中的所有图片
- 使用导出功能导出 CSV、JSON 等格式的数据

### Q: 跳过的图片可以恢复吗？
A: 可以直接在数据库的 `skipped_images` 表中删除对应记录，图片将重新显示。

### Q: 支持哪些图片格式？
A: 支持 jpg, jpeg, png, gif, bmp, webp 格式。

### Q: 多人同时标注会冲突吗？
A: 不会，系统有图片锁机制，同一张图片只能被一个用户标注。

## 开发计划

- [ ] 支持批量导入标注数据
- [ ] 支持撤销跳过操作
- [ ] 添加图片预览缩略图
- [ ] 支持键盘快捷键
- [ ] 添加用户权限管理
- [ ] 支持标注历史记录
- [ ] 添加数据校验和质量检查

## 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题或建议，请通过 GitHub Issues 联系。

