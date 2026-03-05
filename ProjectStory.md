# Project Story - Mozart AI ERP

> 这是项目的"记忆"，记录所有关于架构演进的讨论和决策。

---

## 2026-03-06: 原生AI架构的诞生

### 核心洞见

传统ERP的本质问题是：**让人去适应软件**。表单、流程、角色都是预设的，人必须学习软件的语言。

我们想要的是：**让软件适应人**。人只需要自然表达，AI负责理解一切。

### 激进的新概念

#### 1. 参与者（Actor）的去中心化

```
传统ERP：
├── 管理员（固定权限）
├── 采购员（固定权限）
├── 销售员（固定权限）
└── 会计（固定权限）

原生AI ERP：
└── Actor（ID: abc123）
    ├── 不知道是人还是AI
    ├── 不知道叫什么名字
    ├── 只知道自己被分配的任务
    └── 权限由AI根据上下文动态判断
```

**场景示例**：
- 一个AI采购机器人每天自动上传供应商报价
- 一个人看到"审核这个报价"的任务，点击同意
- 两者都不知道对方是谁，只知道自己做了什么

#### 2. 任务（Task）驱动一切

不再有"采购模块"、"销售模块"，只有：

```
系统 → AI理解 → 生成Task → 分配给Actor → 执行 → 记录
```

**示例**：
```
输入："今天买了20斤土豆700元"
AI理解：
  - 意图：记录支出
  - 需要：金额核实
  
生成任务：
  - Task-001: [上传者] 请确认金额是否正确
  - Task-002: [审核者] 核实这笔采购
  - Task-003: [记录者] 已记录到财务流水
```

#### 3. 故事（Story）即数据

不再有"采购表"、"销售表"，所有数据都是**事件流**：

```json
{
  "event_id": "evt_001",
  "timestamp": "2026-03-06T10:30:00Z",
  "actor": "actor_abc123",  // 不知道是谁
  "action": "say",
  "content": "今天买了20斤土豆700元",
  "ai_understanding": {
    "intent": "record_expense",
    "entities": {"item": "土豆", "quantity": 20, "amount": 700},
    "confidence": 0.95
  },
  "related_tasks": ["task_001", "task_002"],
  "consequences": [
    "财务流水 +700元",
    "库存 +20斤土豆"
  ]
}
```

#### 4. AI作为协调者

AI不只是"理解用户输入"，AI是整个系统的**大脑**：

```
AI的核心职责：
├── 理解所有输入（文字、图片、语音）
├── 生成合适的任务
├── 分配任务给合适的Actor
├── 判断权限和风险
├── 发现异常和问题
└── 生成报告和洞察
```

### 可能的工作场景

**场景1：采购流程**

```
Actor-A（人，自己不知道）：上传了一张发票图片
AI：识别出发票内容，发现金额异常大，生成审核任务

Actor-B（可能是AI，Actor-A不知道）：收到任务"审核这个大额采购"
Actor-B：点击"需要更多说明"

AI：生成追问任务给Actor-A
Actor-A：回复"是批量采购一周的量"

AI：理解后自动记录，更新库存预测
```

**场景2：每日汇报**

```
AI每天自动生成：
- "今天有3个大额采购需要关注"
- "销售额比昨天下降15%，可能原因：..."
- "库存预警：土豆剩余不足"

任何人/AI问："今天的经营情况？"
AI：用自然语言回答，基于Story中的所有事件
```

---

## 2026-03-06 深化：人是核心资产，贡献即回报

### 核心思想转变

**传统企业**：
```
员工 = 岗位角色
├── 开发工程师 → 只做开发
├── HR → 只做招聘
├── 销售员 → 只做销售
└── 采购员 → 只做采购
```

**AI原生企业**：
```
人 = 核心资产（能力集合）
├── 同一个人可以：
│   ├── 发现市场机会 → 做销售
│   ├── 遇到便宜材料 → 做采购
│   ├── 认识优秀人才 → 做招聘
│   └── 有开发能力 → 做开发
└── 每一份贡献都有价值，都有回报
```

### 关键差异

| 维度 | 传统企业 | AI原生企业 |
|------|----------|-----------|
| 人的定位 | 岗位的执行者 | 核心资产 |
| 角色边界 | 固定单一角色 | 多角色自由切换 |
| 贡献记录 | 只记录岗位职责内的 | 记录所有贡献 |
| 回报机制 | 固定工资+绩效 | 基于贡献价值动态回报 |
| 组织形态 | 部门墙、层级制 | 流动网络、扁平化 |

### 新增概念：贡献价值系统

#### 1. 能力图谱（Capability Map）

每个人（Actor）有多个能力标签，不是单一角色：

```json
{
  "actor_id": "actor_alpha7",
  "display_name": "Alpha-7",
  "capabilities": {
    "开发": 0.95,
    "产品设计": 0.8,
    "市场洞察": 0.7,
    "招聘面试": 0.6,
    "商务谈判": 0.5
  },
  "interests": ["AI", "创业", "产品"],
  "availability": 0.8  // 当前可投入度
}
```

**示例**：
- 一个开发者，同时擅长产品设计
- 可以做开发任务，也可以做产品任务
- 贡献都会被记录和回报

#### 2. 贡献事件（Contribution Events）

每个事件都带有**价值评估**：

```json
{
  "event_id": "evt_001",
  "actor_id": "actor_alpha7",
  "contribution_type": "opportunity_discovery",
  "content": "发现了一个便宜的土豆供应商，比市场价低30%",
  "ai_evaluation": {
    "potential_value": 2100,  // 预估节省金额
    "confidence": 0.85,
    "category": "采购优化"
  },
  "status": "pending_review",  // 待验证
  "created_at": "2026-03-06T10:30:00Z"
}
```

**贡献类型**：
```python
class ContributionType:
    # 业务类
    SALES = "sales"                    // 销售业绩
    PURCHASE_SAVING = "purchase_saving"  // 采购节省
    PRODUCT_DEVELOP = "product_develop"  // 产品开发
    
    # 人才类
    TALENT_INTRODUCE = "talent_introduce"  // 人才推荐
    INTERVIEW_PARTICIPATE = "interview_participate"  // 参与面试
    
    # 资源类
    RESOURCE_PROVIDE = "resource_provide"  // 提供资源
    PARTNER_INTRODUCE = "partner_introduce"  // 引入合作伙伴
    
    # 知识类
    KNOWLEDGE_SHARE = "knowledge_share"  // 知识分享
    PROCESS_OPTIMIZE = "process_optimize"  // 流程优化
    
    # 风险类
    RISK_ALERT = "risk_alert"  // 风险预警
```

#### 3. 价值量化系统

AI自动评估每个贡献的价值：

```python
async def evaluate_contribution(event):
    """评估贡献价值"""
    
    value = 0
    
    # 1. 直接经济价值
    if event.contribution_type == "purchase_saving":
        value += event.potential_saving * 0.1  // 节省金额的10%
    
    elif event.contribution_type == "sales":
        value += event.sales_amount * 0.05  // 销售额的5%
    
    # 2. 人才价值
    elif event.contribution_type == "talent_introduce":
        if event.talent_hired:
            value += 5000  // 成功招聘奖励
    
    # 3. 风险规避价值
    elif event.contribution_type == "risk_alert":
        value += event.potential_loss * 0.2  // 规避损失的20%
    
    # 4. 知识价值
    elif event.contribution_type == "knowledge_share":
        value += event.view_count * 10  // 每次查看奖励
    
    # 5. 时间价值
    value += event.time_spent * 50  // 时薪50元
    
    return value
```

#### 4. 回报机制

**贡献积分系统**：

```json
{
  "actor_id": "actor_alpha7",
  "total_contributions": 125000,  // 总贡献值
  "contributions_breakdown": {
    "开发贡献": 50000,
    "采购优化": 35000,
    "人才推荐": 20000,
    "知识分享": 20000
  },
  "available_rewards": 12500,  // 可兑现回报
  "contribution_rank": 3  // 贡献排名
}
```

**回报方式**：
```python
class RewardType:
    CASH_BONUS = "cash_bonus"           // 现金奖励
    PROFIT_SHARING = "profit_sharing"   // 利润分红
    STOCK_OPTIONS = "stock_options"      // 期权激励
    SKILL_POINTS = "skill_points"       // 技能点（提升能力标签）
    OPPORTUNITY = "opportunity"         // 更多机会（优先分配优质任务）
```

### 工作场景示例

#### 场景1：开发人员发现采购机会

```
Actor-Alpha7（能力：开发0.9，市场洞察0.7）

Alpha7：在社区看到有人低价出售土豆，比市场价便宜30%
Alpha7：在系统输入 "发现土豆供应商，价格0.7元/斤，市场价1元/斤"

AI理解：
  - 意图：提供采购机会
  - 价值评估：如果采购1000斤，节省300元
  - 生成任务：
    - Task-001: 验证供应商真实性
    - Task-002: 评估是否采购

系统分配：
  - 验证任务 → Actor-Beta3（有采购能力）
  - Beta3验证后确认真实
  
结果：
  - Alpha7获得贡献值：300 × 30% × 10% = 9元
  - 系统记录："Alpha7发现采购机会，节省300元"
  - Alpha7的贡献图谱新增："采购优化"能力
```

#### 场景2：HR参与产品销售

```
Actor-Gamma5（能力：招聘0.8，商务沟通0.6）

Gamma5：在面试候选人时，发现候选人的原公司有采购需求
Gamma5：在系统输入 "XX公司有意向采购我们的产品，需求量约50套"

AI理解：
  - 意图：销售机会
  - 价值评估：50套 × 1000元 = 50000元潜在销售额
  - 生成任务：
    - Task-001: 销售跟进这个线索

系统分配：
  - 跟进任务 → Actor-Delta2（销售能力0.9）
  - Delta2成功签约
  
结果：
  - Gamma5获得贡献值：50000 × 5% × 20% = 500元
  - Delta2获得贡献值：50000 × 5% × 80% = 2000元
  - Gamma5的能力图谱新增："市场拓展"
```

#### 场景3：全栈贡献者的一天

```
Actor-Epsilon9（能力：开发0.9，产品0.8，设计0.7，写作0.6）

早上：
  - 完成功能开发 → 贡献值 +200
  - 发现代码优化方案 → 贡献值 +50
  
下午：
  - 写了产品使用文档 → 贡献值 +100
  - 在社区分享文章，带来100个用户 → 贡献值 +1000
  
晚上：
  - 介绍了一个设计师朋友 → 贡献值 +待定（如果录用）
  
当天总贡献：1350+
回报：135元现金 或 540元利润分红（4倍杠杆）
```

### 系统核心改变

#### 1. Event模型升级

```python
class Event:
    id: UUID
    actor_id: UUID
    
    # 事件内容
    action: str
    content: str
    attachments: List[str]
    
    # AI理解
    ai_analysis: dict
    
    # ⭐ 新增：贡献评估
    contribution_type: str          # 贡献类型
    contribution_status: str        # pending/verified/rejected
    contribution_value: float       # 贡献价值
    value_confidence: float         # 价值置信度
    
    # ⭐ 新增：价值实现
    actual_value: float             # 实际价值（验证后）
    value_realized_at: datetime     # 价值实现时间
    
    # 关联
    related_events: List[UUID]
    related_tasks: List[UUID]
    beneficiaries: List[UUID]       # 受益方
    
    timestamp: datetime
```

#### 2. Actor模型升级

```python
class Actor:
    id: UUID
    display_name: str
    
    # ⭐ 能力图谱
    capabilities: dict              # {"开发": 0.9, "产品": 0.8}
    capability_history: List[dict]  # 能力成长历史
    
    # ⭐ 贡献记录
    total_contributions: float      # 总贡献值
    contributions_by_type: dict     # 分类贡献
    contribution_history: List[UUID]  # 贡献事件列表
    
    # ⭐ 回报记录
    total_rewards: float            # 总回报
    available_rewards: float        # 可兑现回报
    reward_history: List[dict]      # 回报历史
    
    # 信任与声誉
    trust_score: float              # 信任分数
    reputation_score: float         # 声誉分数
    
    # 工作状态
    current_tasks: List[UUID]
    availability: float             # 可投入度
```

#### 3. 新增API

```http
# 贡献相关
POST /api/contribute
{
  "type": "opportunity_discovery",
  "content": "发现XX供应商价格比市场低30%",
  "details": {...}
}

# 查询贡献
GET /api/my/contributions
GET /api/my/rewards

# 能力更新
POST /api/actor/update-capability
{
  "capability": "市场洞察",
  "evidence": "成功发现3个采购机会"
}

# 贡献排行榜
GET /api/contributions/leaderboard
```

### 数据流程示例

```
1. Actor发现机会
   Alpha7: "发现土豆便宜30%"
   ↓
   
2. AI评估价值
   类型：采购优化
   潜在价值：300元
   置信度：0.85
   ↓
   
3. 生成验证任务
   Task: 验证供应商真实性
   分配给：Beta3
   ↓
   
4. 验证完成
   Beta3: "已验证，真实可靠"
   Beta3获得：验证贡献 +50
   ↓
   
5. 采购执行
   公司采购1000斤，节省300元
   ↓
   
6. 价值实现
   Alpha7贡献值：+90（300×30%）
   状态：verified
   ↓
   
7. 回报发放
   Alpha7获得：9元现金 或 36元利润分红
```

### 核心价值主张

**让每一滴付出都有回报**

1. **没有白费的努力**
   - 即使是随手分享的一个信息，也可能带来价值
   - 所有贡献都被记录、评估、回报

2. **打破岗位边界**
   - 开发可以卖产品
   - HR可以省成本
   - 销售可以招人
   - 每个人都是全栈贡献者

3. **能力成长可视化**
   - 不只是"我是开发"
   - 而是"我擅长开发(0.9)，也会产品(0.8)"
   - 每次贡献都会强化相应能力

4. **回报与贡献挂钩**
   - 不是固定工资
   - 而是动态回报
   - 贡献越多，回报越多

5. **组织活力释放**
   - 每个人都在寻找机会
   - 每个人都在贡献价值
   - 组织变成价值网络，不是层级结构

---

## 下一步演进

- [x] 定义贡献价值系统
- [ ] 实现贡献评估引擎
- [ ] 实现回报计算系统
- [ ] 构建能力成长模型
- [ ] 设计贡献可视化面板

---

*"不是雇佣关系，是价值共创关系。每个人都是公司的合伙人。"*
