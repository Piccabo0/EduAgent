# EduAgent Web Interface

这是EduAgent智能教育助手的Web界面，提供了一个现代化的问答交互体验。

## 功能特点

- 🤖 智能问答：基于RAG技术的教育智能体
- 💬 实时聊天：流畅的对话体验
- 📱 响应式设计：支持桌面和移动设备
- 🎨 现代UI：美观的用户界面
- 📊 系统状态：实时显示系统运行状态
- 💾 历史记录：保存聊天历史

## 文件结构

```
web/
├── index.html          # 主页面
├── styles.css          # 样式文件
├── script.js           # JavaScript逻辑
├── app.py              # Flask后端服务器
├── requirements.txt    # Python依赖
└── README.md          # 说明文档
```

## 快速启动

### 方法：手动启动

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 启动服务器：
```bash
python app.py
```

3. 访问网页：
打开浏览器访问 http://localhost:5000

## 系统要求

- Python 3.7+
- 现代浏览器（Chrome、Firefox、Safari、Edge）
- 2GB+ 内存（如果使用完整的EduAgent功能）

## 使用说明

1. **提问**：在底部输入框输入问题，按回车或点击发送按钮
2. **示例问题**：点击右侧示例问题可快速提问
3. **清除记录**：点击聊天标题栏的垃圾箱图标清除历史
4. **系统状态**：右侧显示实时系统状态

## 运行模式

- **生产模式**：连接完整的EduAgent后端，提供完整功能
- **演示模式**：使用预设回答，适合演示和测试

## 技术栈

### 前端
- HTML5 + CSS3
- Vanilla JavaScript
- Font Awesome图标
- Inter字体

### 后端
- Python Flask
- Flask-CORS（跨域支持）
- EduAgent模块集成

## API接口

- `POST /api/ask`：提交问题获取答案
- `GET /api/status`：获取系统状态
- `GET /api/health`：健康检查

## 自定义配置

可以通过修改以下文件进行自定义：

- `styles.css`：修改界面样式
- `script.js`：修改前端逻辑
- `app.py`：修改后端配置

## 故障排除

1. **端口占用**：修改app.py中的端口号
2. **依赖缺失**：运行 `pip install -r requirements.txt`
3. **EduAgent模块错误**：检查父目录中的EduAgent模块
4. **网络问题**：检查防火墙和代理设置

## 开发模式

启动开发服务器（自动重载）：
```bash
export FLASK_ENV=development  # Linux/Mac
set FLASK_ENV=development     # Windows
python app.py
```

## 部署

生产环境部署建议使用Gunicorn：
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```
