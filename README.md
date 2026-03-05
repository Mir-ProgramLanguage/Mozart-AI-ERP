<h1 align="center">🎹 Mozart AI ERP</h1>

<p align="center">
  <strong>AI原生企业系统 - 打破传统ERP的一切概念</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/Vue-3.4+-green.svg" alt="Vue">
  <img src="https://img.shields.io/badge/FastAPI-0.109+-teal.svg" alt="FastAPI">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
  <img src="https://img.shields.io/badge/Status-开发中-orange.svg" alt="Status">
</p>

<p align="center">
  <a href="#-核心特性">特性</a> •
  <a href="#-快速开始">快速开始</a> •
  <a href="#-技术架构">架构</a> •
  <a href="#-api文档">API</a> •
  <a href="#-文档">文档</a>
</p>

---

## 💡 这是什么？

**这不是一个传统ERP的AI增强版，这是一个完全重新想象的企业管理系统。**

传统ERP让人去适应软件 —— 用户必须学习"采购单"、"借贷平衡"等概念，必须填写固定表单。

**Mozart AI ERP 让软件适应人：**

```
用户：今天买了20斤土豆700元

系统：✓ 已理解：采购记录，金额700元
      ✓ 风险判断：金额>500，需审核
      ✓ 已生成审批任务
      ✓ 已分配给审核员
```

**用户只需要自然说话，AI理解意图，自动处理一切。**

---

## ✨ 核心特性

### 🎭 Actor 匿名协作系统
- 人和AI机器人平等参与，只知代号（如 Alpha-7）
- 信任分数 + 能力模型驱动权限
- 支持虚拟AI员工协作

### 📋 任务驱动工作流
- 无传统模块概念（采购/销售/库存）
- 所有业务通过任务流转
- AI智能生成和分配任务

### 📊 Story 事件流存储
- 所有数据都是事件，灵活存储
- AI理解事件语义
- 向量化存储，语义搜索

### 🧠 AI Core 智能中枢
- 理解所有自然语言输入
- 智能判断权限和风险
- 协调所有参与者协作

### 💰 贡献价值系统
- AI量化每个参与者的贡献
- 贡献值自动转换为回报（现金/分红/技能点）
- 激励机制驱动高效协作

---

## 🚀 快速开始

### 环境要求

| 依赖 | 版本 |
|------|------|
| Python | 3.11+ |
| Node.js | 18+ |
| PostgreSQL | 15+ (with pgvector) |
| Redis | 7+ |
| Docker | 20+ (推荐) |

### Docker 启动（推荐）

```bash
# 克隆项目
git clone https://github.com/your-username/mozart-ai-erp.git
cd mozart-ai-erp

# 复制配置文件
cp .env.example .env

# 编辑配置，填写必要的环境变量
# DEEPSEEK_API_KEY=your-api-key

# 启动服务
docker-compose up -d
```

### 访问地址

| 服务 | 地址 |
|------|------|
| 前端界面 | http://localhost:3000 |
| API 接口 | http://localhost:8000 |
| API 文档 | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |

### 手动启动

<details>
<summary>点击展开详细步骤</summary>

#### 后端

```bash
cd backend
python -m venv venv
source venv/Scripts/activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端

```bash
cd frontend
npm install
npm run dev
```

</details>

---

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                        前端 (Vue 3)                          │
│  TDesign UI │ Pinia Store │ Axios API │ ECharts             │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP/WebSocket
┌─────────────────────────▼───────────────────────────────────┐
│                    后端 (FastAPI)                            │
├─────────────────────────────────────────────────────────────┤
│  AI Core        │  Actor System    │  Task Engine           │
│  ┌───────────┐  │  ┌────────────┐  │  ┌──────────────┐      │
│  │ Intent    │  │  │ Trust      │  │  │ Workflow     │      │
│  │ Entity    │  │  │ Permission │  │  │ Assignment   │      │
│  │ Risk      │  │  │ Identity   │  │  │ Tracking     │      │
│  └───────────┘  │  └────────────┘  │  └──────────────┘      │
├─────────────────────────────────────────────────────────────┤
│  Story Engine   │  Contribution    │  Reward System         │
│  ┌───────────┐  │  ┌────────────┐  │  ┌──────────────┐      │
│  │ Events    │  │  │ Evaluation │  │  │ Calculator   │      │
│  │ Vectors   │  │  │ Scoring    │  │  │ Distribution │      │
│  │ Search    │  │  │ History    │  │  │ Claims       │      │
│  └───────────┘  │  └────────────┘  │  └──────────────┘      │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                      数据层                                  │
│  PostgreSQL + pgvector │ Redis │ MinIO                      │
└─────────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                    外部服务                                  │
│  DeepSeek API (LLM) │ 腾讯云 OCR │ 向量模型                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📡 API 文档

### 统一输入接口

```http
POST /api/v1/say
Content-Type: application/json

{
  "content": "今天买了20斤土豆700元"
}
```

**响应：**
```json
{
  "understood": {
    "intent": "record_purchase",
    "entities": {"item": "土豆", "quantity": "20斤", "amount": 700}
  },
  "tasks_created": [{"type": "approve", "assigned_to": "Beta-3"}],
  "message": "我理解您记录了一笔采购。已创建审批任务。"
}
```

### 自然语言查询

```http
POST /api/v1/ask
Content-Type: application/json

{
  "question": "本月花了多少钱？"
}
```

**响应：**
```json
{
  "answer": "本月共支出15,230元，其中采购占80%。相比上月增长12%。",
  "data": {"total": 15230, "breakdown": {...}}
}
```

### 贡献系统

```http
POST /api/v1/contribute
GET  /api/v1/my/contributions
POST /api/v1/contributions/{id}/verify
GET  /api/v1/my/rewards
POST /api/v1/rewards/{id}/claim
```

---

## 📁 项目结构

```
mozart-ai-erp/
├── backend/                    # Python 后端
│   ├── app/
│   │   ├── ai/                 # AI Core 引擎
│   │   │   ├── intent/         # 意图识别
│   │   │   ├── entity/         # 实体提取
│   │   │   └── risk/           # 风险判断
│   │   ├── api/v1/             # API 路由
│   │   ├── models/             # 数据模型
│   │   │   ├── actor.py        # Actor 模型
│   │   │   ├── task.py         # 任务模型
│   │   │   ├── story.py        # 事件流模型
│   │   │   └── contribution.py # 贡献模型
│   │   ├── services/           # 业务服务
│   │   │   ├── central_ai_service.py      # 核心 AI 服务
│   │   │   ├── contribution_evaluator.py  # 贡献评估引擎
│   │   │   └── reward_calculator.py       # 回报计算引擎
│   │   └── core/               # 核心组件
│   ├── alembic/                # 数据库迁移
│   └── tests/                  # 测试
├── frontend/                   # Vue 前端
│   └── src/
│       ├── views/              # 页面组件
│       │   ├── Chat.vue        # AI 对话界面
│       │   ├── AIAgents.vue    # AI 员工管理
│       │   ├── Tasks.vue       # 任务看板
│       │   ├── Contributions.vue # 贡献仪表盘
│       │   └── Rewards.vue     # 回报中心
│       ├── components/         # 通用组件
│       ├── stores/             # Pinia 状态管理
│       └── api/                # API 封装
├── docs/                       # 文档
│   ├── AI_NATIVE_ARCHITECTURE.md  # AI 原生架构详解
│   ├── ARCHITECTURE.md            # 架构设计
│   └── USAGE_EXAMPLES.md          # 使用示例
├── log/                        # 开发日志
├── docker-compose.yml          # Docker 编排
└── README.md                   # 项目文档
```

---

## 🔄 与传统ERP对比

| 维度 | 传统 ERP | Mozart AI ERP |
|------|----------|---------------|
| **交互方式** | 填写固定表单 | 自然语言对话 |
| **用户概念** | 固定角色（采购员/销售员） | 匿名 Actor（人/AI 混编） |
| **数据结构** | 预定义表（采购表/销售表） | 事件流 + AI 语义理解 |
| **权限控制** | 预设权限角色 | AI 上下文动态判断 |
| **模块划分** | 采购/销售/库存/财务... | 无模块，只有任务流 |
| **决策方式** | 人决策 | AI 辅助 + 人确认 |
| **扩展性** | 需要二次开发 | 自动适应新场景 |
| **学习成本** | 需培训 | 零学习成本 |

---

## 📚 文档

- [AI 原生架构设计](./docs/AI_NATIVE_ARCHITECTURE.md) - 详细的技术架构说明
- [架构对比分析](./docs/ARCHITECTURE.md) - 传统 vs AI 原生架构对比
- [使用示例](./docs/USAGE_EXAMPLES.md) - 完整的业务场景示例
- [项目故事](./ProjectStory.md) - 架构演进历程

---

## 🗓️ 开发进度

### MVP 阶段（3周）

| 周次 | 目标 | 状态 |
|------|------|------|
| Week 1 | AI Core + 数据层 + 贡献系统 | ✅ 完成 |
| Week 2 | API + 基础前端 + 任务系统 | 🚧 进行中 |
| Week 3 | OCR集成 + 智能问答 + 测试优化 | ⏳ 待开始 |

详细计划见 [任务.md](./任务.md)

---

## ⚙️ 配置

复制 `.env.example` 到 `.env`：

```bash
# ===== AI 能力 =====
DEEPSEEK_API_KEY=your-deepseek-api-key
DEEPSEEK_MODEL=deepseek-chat
EMBEDDING_MODEL=text-embedding-3-small

# ===== 数据库 =====
DATABASE_URL=postgresql://mozart:password@localhost:5432/mozart_erp
# 开发环境可用 SQLite
# DATABASE_URL=sqlite:///./mozart.db

# ===== Redis =====
REDIS_URL=redis://localhost:6379/0

# ===== OCR 服务 =====
TENCENT_SECRET_ID=your-secret-id
TENCENT_SECRET_KEY=your-secret-key

# ===== 安全 =====
JWT_SECRET_KEY=your-jwt-secret-key
API_KEY_SALT=your-api-salt

# ===== 应用 =====
APP_NAME=Mozart AI ERP
DEBUG=true
```

---

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

---

## 📄 许可证

本项目采用 [MIT License](LICENSE) 许可证。

---

## 📞 联系方式

- 项目启动：2026-03-06
- MVP 预计完成：3周

---

<p align="center">
  <i>"让软件像人一样思考，而不是让人像软件一样思考。"</i>
</p>

<p align="center">
  Made with ❤️ by Mozart AI Team
</p>
