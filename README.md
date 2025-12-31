# AeroVision 飞机图片标注系统

一个专业的飞机图片标注工具，用于构建飞机识别数据集。支持标注飞机机型、航空公司、注册号，以及飞机和注册号的边界框位置，可导出为 YOLO 格式数据。

## ✨ 功能特性

- 🖼️ **图片标注**：支持标注飞机整体和注册号的边界框
- 🏷️ **多维度标签**：机型、航空公司、注册号、清晰度、遮挡程度
- 📊 **数据统计**：按机型、航空公司统计标注数量
- 📤 **数据导出**：支持导出为 CSV 格式
- 🔒 **多人协作**：图片锁定机制，防止多人同时标注同一张图片
- 🎨 **现代化界面**：基于 Vue 3 的深色主题 UI

## 🛠️ 技术栈

### 后端
- Python 3.8+
- Flask - Web 框架
- SQLite - 数据库
- Flask-CORS - 跨域支持

### 前端
- Vue 3 - 前端框架
- Vite - 构建工具
- Axios - HTTP 客户端

## 📁 项目结构

```
AeroVision-Label-System/
├── app.py                 # Flask 后端入口
├── database.py            # 数据库操作模块
├── requirements.txt       # Python 依赖
├── labels.db              # SQLite 数据库
├── data/                  # 预置数据
│   ├── airlines.json      # 航空公司列表
│   └── aircraft_types.json # 机型列表
├── images/                # 待标注图片目录
├── labeled/               # 已标注图片目录
└── frontend/              # 前端项目
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── App.vue
        ├── main.js
        ├── api/           # API 接口
        ├── components/    # Vue 组件
        │   ├── BoundingBox.vue    # 边界框绘制
        │   ├── ImageLabeler.vue   # 标注主界面
        │   ├── LabelForm.vue      # 标注表单
        │   ├── LabelList.vue      # 已标注列表
        │   └── StatsPanel.vue     # 统计面板
        └── styles/        # 样式文件
```

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+
- npm 或 yarn

### 安装步骤

#### 1. 克隆项目

```bash
git clone https://github.com/AeroVision-Lab/AeroVision-Label-System.git
cd AeroVision-Label-System
```

#### 2. 安装后端依赖

```bash
pip install -r requirements.txt
```

#### 3. 安装前端依赖

```bash
cd frontend
npm install
```

#### 4. 准备图片

将待标注的飞机图片放入 `images/` 目录。支持的格式：
- JPG / JPEG
- PNG
- BMP
- WebP

### 运行项目

#### 启动后端服务

```bash
# 在项目根目录
python app.py
```

后端默认运行在 `http://localhost:5000`

#### 启动前端开发服务

```bash
# 在 frontend 目录
cd frontend
npm run dev
```

前端默认运行在 `http://localhost:3000`

## 📖 使用说明

### 标注流程

1. **选择图片**：系统自动加载 `images/` 目录下的待标注图片
2. **绘制边界框**：
   - 点击"飞机区域"按钮，在图片上拖拽绘制飞机的边界框
   - 点击"注册号区域"按钮，在图片上拖拽绘制注册号的边界框
3. **填写标注信息**：
   - 选择机型（如 A320、B738 等）
   - 选择航空公司
   - 输入注册号
   - 设置清晰度（0-1）
   - 设置遮挡程度（0-1）
4. **提交标注**：点击提交按钮完成标注

### 文件命名规则

标注完成后，图片会自动移动到 `labeled/` 目录，并按以下规则重命名：

```
{机型代码}-{序号}.{原扩展名}
```

例如：`A320-0001.jpg`、`B738-0002.png`

### 数据导出

在"已标注"页面可以导出所有标注数据为 CSV 格式，包含以下字段：

| 字段 | 说明 |
|------|------|
| file_name | 新文件名 |
| type_id | 机型代码 |
| type_name | 机型名称 |
| airline_id | 航空公司代码 |
| airline_name | 航空公司名称 |
| clarity | 清晰度 (0-1) |
| block | 遮挡程度 (0-1) |
| registration | 注册号 |

## ⚙️ 配置选项

可以通过环境变量或 `.env` 文件配置以下选项：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `IMAGES_DIR` | 待标注图片目录 | `./images` |
| `LABELED_DIR` | 已标注图片目录 | `./labeled` |
| `DATABASE_PATH` | 数据库文件路径 | `./labels.db` |

示例 `.env` 文件：

```env
IMAGES_DIR=./images
LABELED_DIR=./labeled
DATABASE_PATH=./labels.db
```

## 🔧 预置数据

### 航空公司

系统预置了 40+ 家主流航空公司，包括：
- 中国航司：国航、东航、南航、海航、厦航、川航、深航、春秋、吉祥等
- 国际航司：新航、国泰、阿联酋、卡塔尔、汉莎、法航、英航、美航等

### 机型

系统预置了 50+ 种常见机型，包括：
- 空客：A319/A320/A321/A330/A350/A380 系列
- 波音：737/747/757/767/777/787 系列
- 中国商飞：C919、ARJ21
- 其他：E190/E195、CRJ 系列、ATR72、新舟60

如需添加更多航司或机型，可编辑 `data/airlines.json` 和 `data/aircraft_types.json` 文件。

## 🤝 多人协作

系统支持多人同时使用，通过图片锁定机制防止冲突：

- 当一个用户正在标注某张图片时，该图片会被锁定
- 其他用户无法同时标注被锁定的图片
- 锁定会在 10 分钟后自动释放（防止用户异常退出导致死锁）
- 用户断开连接时会自动释放其持有的所有锁

## 📝 API 接口

### 图片相关

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/images` | 获取待标注图片列表 |
| GET | `/api/images/<filename>` | 获取图片文件 |
| GET | `/api/labeled-images/<filename>` | 获取已标注图片文件 |

### 标注相关

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/labels` | 获取已标注列表（分页） |
| GET | `/api/labels/<id>` | 获取单个标注记录 |
| POST | `/api/labels` | 创建标注记录 |
| PUT | `/api/labels/<id>` | 更新标注记录 |
| DELETE | `/api/labels/<id>` | 删除标注记录 |
| GET | `/api/labels/export` | 导出标注数据 |

### 基础数据

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/airlines` | 获取航空公司列表 |
| GET | `/api/aircraft-types` | 获取机型列表 |
| GET | `/api/stats` | 获取统计信息 |

## 📄 许可证

本项目采用 GPL-3.0 许可证，详情请参阅 [LICENSE](LICENSE) 文件。

## 🙏 致谢

感谢所有为航空数据集建设做出贡献的朋友们！

## 联系我们
如有任何问题或建议，欢迎通过以下方式联系我们：
- 邮箱：(<5712.cg8@gmail.com>)[mailto:5712.cg8@gmail.com]
