# AI原生架构设计文档 v2.0

> 人是核心资产，贡献即回报 - 打破岗位边界，释放组织活力

---

## 核心哲学

### 1. 人不是岗位工具，人是核心资产

**传统企业**：
```
张三 = 开发工程师
├── 只能做开发
├── 擅长招聘？抱歉，那不是你的工作
├── 发现销售机会？抱歉，去找销售部
└── 想做其他贡献？抱歉，要申请调岗
```

**AI原生企业**：
```
张三 = 核心资产
├── 开发能力 0.9
├── 产品能力 0.8
├── 市场洞察 0.7
├── 招聘能力 0.6
└── 所有能力都可以发挥，所有贡献都有回报
```

### 2. 贡献即回报，打破固定薪酬

**传统**：固定工资 + 绩效（很多时候绩效只看岗位职责）

**AI原生**：基于贡献价值的动态回报
- 销售一单 → 销售额的5%
- 节省成本 → 节省金额的10%
- 招聘成功 → 5000元奖励
- 发现风险 → 规避损失的20%

### 3. 组织是价值网络，不是层级结构

```
传统：
CEO → VP → 总监 → 经理 → 员工

AI原生：
价值网络（所有Actor平等）
├── Alpha-7 贡献 50000 → 获得 5000回报
├── Beta-3 贡献 30000 → 获得 3000回报
└── Gamma-5 贡献 10000 → 获得 1000回报
```

---

## 系统架构

### 整体架构图

```
┌──────────────────────────────────────────────────────────────┐
│                        用户界面层                              │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐              │
│  │ 对话输入框  │  │ 任务看板   │  │ 贡献仪表盘  │              │
│  │ (唯一入口)  │  │            │  │ (我的价值)  │              │
│  └────────────┘  └────────────┘  └────────────┘              │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                      API网关层                                │
│    POST /api/say    POST /api/ask    GET /api/my/contributions│
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                     AI Core (大脑)                            │
│  ┌─────────────┬─────────────┬─────────────┬──────────────┐ │
│  │ 意图理解    │ 实体提取    │ 任务生成    │ 智能分配     │ │
│  └─────────────┴─────────────┴─────────────┴──────────────┘ │
│  ┌─────────────┬─────────────┬─────────────┬──────────────┐ │
│  │ ⭐贡献评估  │ ⭐价值量化  │ ⭐回报计算  │ 能力成长     │ │
│  └─────────────┴─────────────┴─────────────┴──────────────┘ │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                      数据层                                   │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐              │
│  │ Events DB  │  │ Tasks DB   │  │ Actors DB  │              │
│  │ (事件流)    │  │ (任务池)    │  │ (能力图谱)  │              │
│  │ + 贡献价值  │  │            │  │ + 贡献记录  │              │
│  └────────────┘  └────────────┘  └────────────┘              │
│  ┌────────────┐  ┌────────────┐                               │
│  │ Rewards DB │  │ Knowledge  │                               │
│  │ (回报记录)  │  │ (知识库)    │                               │
│  └────────────┘  └────────────┘                               │
└──────────────────────────────────────────────────────────────┘
```

---

## 核心组件

### 1. Actor（能力个体）系统

#### 概念升级

Actor不是"员工"，是"能力集合体"：

```python
class Actor:
    """能力个体"""
    
    id: UUID
    display_name: str  # 匿名代号
    
    # ⭐ 能力图谱（多维度）
    capabilities: dict = {
        "开发": 0.95,      # 0-1分数
        "产品设计": 0.85,
        "市场洞察": 0.70,
        "招聘面试": 0.60,
        "商务谈判": 0.50
    }
    
    # 能力成长历史
    capability_history: List[dict] = [
        {
            "capability": "市场洞察",
            "previous": 0.60,
            "current": 0.70,
            "reason": "成功发现2个市场机会",
            "timestamp": "2026-03-06"
        }
    ]
    
    # ⭐ 贡献记录
    total_contributions: float = 50000  # 总贡献值
    contributions_by_type: dict = {
        "开发贡献": 30000,
        "采购优化": 10000,
        "人才推荐": 5000,
        "知识分享": 5000
    }
    
    # ⭐ 回报记录
    total_rewards: float = 5000  # 总回报
    available_rewards: float = 500  # 可兑现
    reward_history: List[dict] = [...]
    
    # 信任与声誉
    trust_score: float = 0.95
    reputation_score: float = 0.92
    
    # 工作状态
    current_tasks: List[UUID]
    availability: float = 0.8  # 可投入度
```

#### 能力标签体系

```python
CAPABILITY_TAXONOMY = {
    # 技术类
    "技术": {
        "开发": ["前端", "后端", "全栈", "移动端", "AI/ML"],
        "运维": ["服务器", "数据库", "云服务"],
        "安全": ["网络安全", "数据安全"]
    },
    
    # 产品类
    "产品": {
        "产品设计": ["需求分析", "原型设计", "用户体验"],
        "项目管理": ["进度管理", "资源协调"]
    },
    
    # 商业类
    "商业": {
        "销售": ["直销", "渠道", "大客户"],
        "市场": ["市场分析", "品牌推广", "内容营销"],
        "商务": ["谈判", "合作", "资源整合"]
    },
    
    # 资源类
    "资源": {
        "采购": ["供应商管理", "成本控制"],
        "人才": ["招聘", "面试", "培训"]
    },
    
    # 知识类
    "知识": {
        "内容": ["写作", "设计", "视频"],
        "培训": ["内部培训", "外部分享"]
    }
}
```

---

### 2. Event（贡献事件）系统

#### 概念升级

每个事件都是一次**贡献**，都有**价值**：

```python
class Event:
    """贡献事件"""
    
    id: UUID
    actor_id: UUID
    
    # 事件内容
    action: str
    content: str
    attachments: List[str]
    
    # AI理解
    ai_analysis: dict = {
        "intent": "provide_opportunity",
        "entities": {...},
        "confidence": 0.95
    }
    
    # ⭐⭐⭐ 贡献评估（核心新增）
    contribution_type: str = "purchase_saving"  # 贡献类型
    contribution_status: str = "pending"        # pending/verified/rejected
    contribution_value: float = 300.0           # 预估贡献价值
    value_confidence: float = 0.85              # 价值置信度
    value_currency: str = "CNY"                 # 货币单位
    
    # ⭐ 实际价值（验证后）
    actual_value: float = 280.0                 # 实际实现的价值
    value_realized_at: datetime                 # 价值实现时间
    
    # ⭐ 价值计算依据
    value_calculation: dict = {
        "basis": "cost_saving",                 # 价值基础
        "formula": "saving_amount × 30%",       # 计算公式
        "parameters": {
            "saving_amount": 1000,              # 节省金额
            "share_rate": 0.3                   # 分享比例
        }
    }
    
    # 关联
    related_events: List[UUID]
    related_tasks: List[UUID]
    beneficiaries: List[UUID] = ["company"]     # 受益方
    
    # 时间
    created_at: datetime
    verified_at: datetime                       # 验证时间
```

#### 贡献类型体系

```python
class ContributionType:
    """贡献类型"""
    
    # ===== 业务类贡献 =====
    
    # 销售相关
    SALES_OPPORTUNITY = "sales_opportunity"     # 提供销售线索
    SALES_CLOSE = "sales_close"                  # 完成销售
    CUSTOMER_RETENTION = "customer_retention"    # 客户留存
    
    # 采购相关
    PURCHASE_OPPORTUNITY = "purchase_opportunity"  # 发现采购机会
    PURCHASE_SAVING = "purchase_saving"             # 采购节省
    SUPPLIER_QUALITY = "supplier_quality"           # 供应商质量
    
    # 产品相关
    PRODUCT_DEVELOP = "product_develop"          # 产品开发
    PRODUCT_OPTIMIZE = "product_optimize"        # 产品优化
    BUG_FIX = "bug_fix"                          # 问题修复
    
    # ===== 人才类贡献 =====
    
    TALENT_INTRODUCE = "talent_introduce"        # 人才推荐
    INTERVIEW_PARTICIPATE = "interview_participate"  # 参与面试
    TRAINING_PROVIDE = "training_provide"        # 提供培训
    MENTORING = "mentoring"                      # 指导带教
    
    # ===== 资源类贡献 =====
    
    RESOURCE_PROVIDE = "resource_provide"        # 提供资源
    PARTNER_INTRODUCE = "partner_introduce"      # 引入合作伙伴
    INFORMATION_SHARE = "information_share"      # 信息分享
    
    # ===== 知识类贡献 =====
    
    KNOWLEDGE_SHARE = "knowledge_share"          # 知识分享
    DOCUMENT_WRITE = "document_write"            # 文档编写
    PROCESS_OPTIMIZE = "process_optimize"        # 流程优化
    TOOL_DEVELOP = "tool_develop"                # 工具开发
    
    # ===== 风险类贡献 =====
    
    RISK_ALERT = "risk_alert"                    # 风险预警
    ISSUE_DISCOVER = "issue_discover"            # 问题发现
    CRISIS_HANDLE = "crisis_handle"              # 危机处理
```

---

### 3. 贡献评估引擎

#### 价值评估算法

```python
class ContributionEvaluator:
    """贡献评估引擎"""
    
    async def evaluate(self, event: Event) -> dict:
        """评估贡献价值"""
        
        contribution_type = event.contribution_type
        value = 0
        confidence = 0
        
        # 1. 销售类贡献
        if contribution_type == "sales_opportunity":
            value, confidence = await self._evaluate_sales_opportunity(event)
        
        elif contribution_type == "sales_close":
            value, confidence = await self._evaluate_sales_close(event)
        
        # 2. 采购类贡献
        elif contribution_type == "purchase_saving":
            value, confidence = await self._evaluate_purchase_saving(event)
        
        # 3. 产品类贡献
        elif contribution_type == "product_develop":
            value, confidence = await self._evaluate_product_develop(event)
        
        # 4. 人才类贡献
        elif contribution_type == "talent_introduce":
            value, confidence = await self._evaluate_talent_introduce(event)
        
        # 5. 风险类贡献
        elif contribution_type == "risk_alert":
            value, confidence = await self._evaluate_risk_alert(event)
        
        return {
            "value": value,
            "confidence": confidence,
            "calculation_basis": self._get_calculation_basis(contribution_type)
        }
    
    async def _evaluate_purchase_saving(self, event: Event) -> tuple:
        """评估采购节省贡献"""
        
        # 从事件中提取数据
        saving_amount = event.ai_analysis.get("entities", {}).get("saving_amount", 0)
        confidence = event.ai_analysis.get("confidence", 0)
        
        # 计算贡献价值
        # 贡献 = 节省金额 × 贡献者分享比例
        share_rate = 0.3  # 贡献者获得节省金额的30%作为贡献值
        value = saving_amount * share_rate
        
        return value, confidence
    
    async def _evaluate_sales_close(self, event: Event) -> tuple:
        """评估销售成交贡献"""
        
        sales_amount = event.ai_analysis.get("entities", {}).get("sales_amount", 0)
        profit_margin = event.ai_analysis.get("entities", {}).get("profit_margin", 0.2)
        confidence = event.ai_analysis.get("confidence", 0)
        
        # 贡献 = 销售额 × 利润率 × 贡献比例
        profit = sales_amount * profit_margin
        value = profit * 0.5  # 贡献者获得利润的50%
        
        return value, confidence
    
    async def _evaluate_talent_introduce(self, event: Event) -> tuple:
        """评估人才推荐贡献"""
        
        talent_level = event.ai_analysis.get("entities", {}).get("talent_level", "normal")
        hired = event.ai_analysis.get("entities", {}).get("hired", False)
        confidence = event.ai_analysis.get("confidence", 0)
        
        if not hired:
            return 0, confidence  # 未录用无价值
        
        # 根据人才等级确定奖励
        level_rewards = {
            "senior": 10000,  # 高级人才
            "middle": 5000,   # 中级人才
            "normal": 2000    # 普通人才
        }
        
        value = level_rewards.get(talent_level, 2000)
        
        return value, confidence
    
    async def _evaluate_risk_alert(self, event: Event) -> tuple:
        """评估风险预警贡献"""
        
        risk_type = event.ai_analysis.get("entities", {}).get("risk_type", "normal")
        potential_loss = event.ai_analysis.get("entities", {}).get("potential_loss", 0)
        confidence = event.ai_analysis.get("confidence", 0)
        
        # 贡献 = 规避损失 × 贡献比例
        share_rate = 0.2  # 贡献者获得规避损失的20%
        value = potential_loss * share_rate
        
        return value, confidence
    
    async def _evaluate_product_develop(self, event: Event) -> tuple:
        """评估产品开发贡献"""
        
        # 基于时间投入和难度
        time_spent = event.ai_analysis.get("entities", {}).get("time_spent", 0)  # 小时
        difficulty = event.ai_analysis.get("entities", {}).get("difficulty", 1.0)
        confidence = event.ai_analysis.get("confidence", 0)
        
        # 时薪 × 时间 × 难度系数
        hourly_rate = 100  # 基础时薪
        value = hourly_rate * time_spent * difficulty
        
        return value, confidence
```

---

### 4. 回报计算系统

#### 回报类型

```python
class RewardType:
    """回报类型"""
    
    CASH_BONUS = "cash_bonus"              # 现金奖励
    PROFIT_SHARING = "profit_sharing"      # 利润分红
    STOCK_OPTIONS = "stock_options"        # 期权激励
    SKILL_POINTS = "skill_points"          # 技能点（提升能力）
    OPPORTUNITY = "opportunity"            # 更多机会（优先分配任务）
```

#### 回报计算引擎

```python
class RewardCalculator:
    """回报计算引擎"""
    
    # 回报杠杆（贡献值 → 回报）
    REWARD_LEVERAGE = {
        "cash_bonus": 0.1,         # 现金：贡献值的10%
        "profit_sharing": 0.4,     # 利润分红：贡献值的40%（4倍杠杆）
        "stock_options": 1.0,      # 期权：1:1转换
    }
    
    async def calculate(self, actor: Actor, contribution_value: float) -> dict:
        """计算回报"""
        
        rewards = {}
        
        # 1. 现金奖励
        cash = contribution_value * self.REWARD_LEVERAGE["cash_bonus"]
        if cash >= 10:  # 最低10元
            rewards["cash_bonus"] = cash
        
        # 2. 利润分红（更高杠杆）
        profit_sharing = contribution_value * self.REWARD_LEVERAGE["profit_sharing"]
        if profit_sharing >= 100:  # 最低100元
            rewards["profit_sharing"] = profit_sharing
        
        # 3. 技能点（提升能力）
        skill_points = contribution_value / 1000  # 每1000贡献值 = 1技能点
        rewards["skill_points"] = skill_points
        
        return rewards
    
    async def distribute(self, actor_id: UUID, rewards: dict):
        """发放回报"""
        
        # 记录回报历史
        for reward_type, amount in rewards.items():
            await self._create_reward_record(
                actor_id=actor_id,
                reward_type=reward_type,
                amount=amount,
                timestamp=datetime.now()
            )
        
        # 更新Actor的回报余额
        await self._update_actor_rewards(actor_id, rewards)
```

---

### 5. 能力成长系统

#### 能力提升算法

```python
class CapabilityGrowthEngine:
    """能力成长引擎"""
    
    async def update_capability(
        self, 
        actor: Actor, 
        capability: str, 
        contribution_value: float
    ):
        """更新能力分数"""
        
        current_score = actor.capabilities.get(capability, 0)
        
        # 能力提升 = 当前分数 + 贡献值 × 成长系数
        growth_rate = 0.0001  # 每贡献10000，能力提升1.0
        growth = contribution_value * growth_rate
        
        # 上限为1.0
        new_score = min(current_score + growth, 1.0)
        
        # 记录成长历史
        growth_record = {
            "capability": capability,
            "previous": current_score,
            "current": new_score,
            "growth": new_score - current_score,
            "reason": f"贡献价值 {contribution_value}",
            "timestamp": datetime.now()
        }
        
        # 更新Actor
        actor.capabilities[capability] = new_score
        actor.capability_history.append(growth_record)
        
        return new_score
```

---

## 工作流程

### 场景：开发者发现采购机会

```
1. Actor输入
   Alpha-7: "发现土豆供应商，价格0.7元/斤，市场价1元/斤"
   ↓
   
2. AI理解
   意图: provide_opportunity
   类型: purchase_opportunity
   实体: {
     item: "土豆",
     price: 0.7,
     market_price: 1.0,
     saving_rate: 0.3
   }
   ↓
   
3. 贡献评估
   预估价值: {
     potential_saving: 300元 (假设采购1000斤),
     share_rate: 0.3,
     contribution_value: 90元
   }
   置信度: 0.85
   状态: pending
   ↓
   
4. 生成验证任务
   Task-001: 验证供应商真实性
   分配给: Beta-3 (采购能力0.9)
   ↓
   
5. 验证执行
   Beta-3: "已验证，真实可靠"
   Beta-3获得验证贡献: +50元
   ↓
   
6. 采购执行
   公司决定采购1000斤
   实际节省: 300元
   ↓
   
7. 价值实现
   Alpha-7贡献值: +90元
   状态: verified
   实际价值: 280元 (实际节省略少于预估)
   ↓
   
8. 回报发放
   Alpha-7获得:
   - 现金: 9元
   - 利润分红: 36元 (可选择)
   - 技能点: 0.09
   ↓
   
9. 能力成长
   Alpha-7能力图谱:
   - 市场洞察: 0.70 → 0.71
   - 采购优化: 新增标签 0.50
```

---

## API设计

### 1. 提交贡献

```http
POST /api/contribute
Content-Type: application/json

{
  "type": "purchase_opportunity",
  "content": "发现土豆供应商，价格比市场低30%",
  "details": {
    "item": "土豆",
    "price": 0.7,
    "market_price": 1.0,
    "contact": "张经理"
  }
}
```

响应：
```json
{
  "event_id": "evt_001",
  "contribution_type": "purchase_opportunity",
  "estimated_value": 90,
  "confidence": 0.85,
  "status": "pending",
  "tasks_created": [
    {
      "id": "task_001",
      "type": "verify",
      "description": "验证供应商真实性"
    }
  ],
  "message": "感谢您的贡献！已创建验证任务。预估贡献价值90元。"
}
```

### 2. 查询我的贡献

```http
GET /api/my/contributions?period=this_month
```

响应：
```json
{
  "total_value": 15000,
  "contributions": [
    {
      "id": "evt_001",
      "type": "purchase_opportunity",
      "content": "发现土豆供应商...",
      "estimated_value": 90,
      "actual_value": 85,
      "status": "verified",
      "created_at": "2026-03-06T10:30:00Z"
    }
  ],
  "by_type": {
    "采购优化": 5000,
    "产品开发": 8000,
    "知识分享": 2000
  }
}
```

### 3. 查询我的回报

```http
GET /api/my/rewards
```

响应：
```json
{
  "total_rewards": 1500,
  "available_rewards": 500,
  "history": [
    {
      "type": "cash_bonus",
      "amount": 100,
      "source": "采购优化贡献",
      "timestamp": "2026-03-06T12:00:00Z"
    }
  ]
}
```

### 4. 兑现回报

```http
POST /api/rewards/redeem
Content-Type: application/json

{
  "amount": 500,
  "type": "cash_bonus"
}
```

---

## 数据模型

### 核心表结构

```sql
-- 参与者表
CREATE TABLE actors (
    id UUID PRIMARY KEY,
    display_name VARCHAR(50),
    capabilities JSONB DEFAULT '{}',
    capability_history JSONB DEFAULT '[]',
    total_contributions DECIMAL(12,2) DEFAULT 0,
    contributions_by_type JSONB DEFAULT '{}',
    total_rewards DECIMAL(12,2) DEFAULT 0,
    available_rewards DECIMAL(12,2) DEFAULT 0,
    trust_score DECIMAL(3,2) DEFAULT 0.5,
    reputation_score DECIMAL(3,2) DEFAULT 0.5,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 事件表
CREATE TABLE events (
    id UUID PRIMARY KEY,
    actor_id UUID REFERENCES actors(id),
    action VARCHAR(50),
    content TEXT,
    attachments JSONB DEFAULT '[]',
    ai_analysis JSONB DEFAULT '{}',
    
    -- 贡献评估
    contribution_type VARCHAR(50),
    contribution_status VARCHAR(20) DEFAULT 'pending',
    contribution_value DECIMAL(12,2),
    value_confidence DECIMAL(3,2),
    actual_value DECIMAL(12,2),
    value_realized_at TIMESTAMP,
    value_calculation JSONB DEFAULT '{}',
    
    -- 向量嵌入
    embeddings VECTOR(1536),
    
    -- 关联
    related_events UUID[] DEFAULT '{}',
    related_tasks UUID[] DEFAULT '{}',
    beneficiaries UUID[] DEFAULT '{}',
    
    created_at TIMESTAMP DEFAULT NOW(),
    verified_at TIMESTAMP
);

-- 回报表
CREATE TABLE rewards (
    id UUID PRIMARY KEY,
    actor_id UUID REFERENCES actors(id),
    event_id UUID REFERENCES events(id),
    reward_type VARCHAR(50),
    amount DECIMAL(12,2),
    status VARCHAR(20) DEFAULT 'pending',  -- pending/claimed/claimed
    created_at TIMESTAMP DEFAULT NOW(),
    claimed_at TIMESTAMP
);

-- 任务表
CREATE TABLE tasks (
    id UUID PRIMARY KEY,
    type VARCHAR(50),
    description TEXT,
    assigned_to UUID[],
    status VARCHAR(20) DEFAULT 'pending',
    priority INT DEFAULT 50,
    related_events UUID[] DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_events_actor ON events(actor_id);
CREATE INDEX idx_events_contribution_type ON events(contribution_type);
CREATE INDEX idx_events_contribution_status ON events(contribution_status);
CREATE INDEX idx_actors_contributions ON actors(total_contributions);
CREATE INDEX idx_rewards_actor ON rewards(actor_id);
```

---

## 核心价值

### 1. 每一滴付出都有回报

```
传统：
发现好机会 → "不是我的工作" → 机会流失

AI原生：
发现好机会 → 系统记录 → 贡献值+回报 → 激励继续贡献
```

### 2. 打破岗位边界

```
传统：
张三 = 开发工程师（单一角色）

AI原生：
张三 = {
  开发能力 0.9,
  产品能力 0.8,
  市场洞察 0.7,
  所有能力都可以发挥
}
```

### 3. 组织活力释放

```
传统：
员工只做岗位内的事 → 创新受限

AI原生：
员工主动寻找机会 → 人人都是创业者
- 开发可以卖产品
- HR可以省成本
- 销售可以招人
```

### 4. 公平透明

```
传统：
绩效看老板印象 → 不公平

AI原生：
贡献值客观计算 → 透明公正
每个人的贡献都有记录
每个人的回报都有依据
```

---

*"让每个人都是公司的合伙人，让每一滴汗水都有回报。"*
