"""
种子数据脚本 - 创建测试用户和初始数据

运行方式: python seed_data.py
"""

import sys
import os

# Windows 控制台编码设置
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.contribution import (
    Actor, Event, Task, ActorInteraction,
    ActorType, RewardType, RewardStatus, ContributionStatus,
    InteractionType, InteractionStatus
)
from app.models.notification import Notification
from app.core.security import get_password_hash

# 先创建所有表
Base.metadata.create_all(bind=engine)


def create_test_users(db: Session):
    """创建测试用户"""
    print("📋 创建测试用户...")
    
    users_data = [
        {
            "username": "admin",
            "email": "admin@company.com",
            "password": "admin123",
            "is_superuser": True,
            "display_name": "系统管理员",
            "capabilities": {"管理": 0.95, "技术": 0.8, "产品": 0.7}
        },
        {
            "username": "zhangsan",
            "email": "zhangsan@company.com",
            "password": "123456",
            "is_superuser": False,
            "display_name": "张三",
            "capabilities": {"开发": 0.9, "前端": 0.85, "后端": 0.8}
        },
        {
            "username": "lisi",
            "email": "lisi@company.com",
            "password": "123456",
            "is_superuser": False,
            "display_name": "李四",
            "capabilities": {"产品": 0.85, "设计": 0.8, "运营": 0.75}
        },
        {
            "username": "wangwu",
            "email": "wangwu@company.com",
            "password": "123456",
            "is_superuser": False,
            "display_name": "王五",
            "capabilities": {"运营": 0.9, "市场": 0.85, "销售": 0.8}
        }
    ]
    
    created_users = []
    for user_data in users_data:
        # 检查用户是否已存在
        existing = db.query(User).filter(User.username == user_data["username"]).first()
        if existing:
            print(f"  ⚠️  用户 {user_data['username']} 已存在，跳过")
            created_users.append(existing)
            continue
        
        # 创建用户
        user = User(
            username=user_data["username"],
            email=user_data["email"],
            hashed_password=get_password_hash(user_data["password"]),
            is_superuser=user_data["is_superuser"],
            is_active=True
        )
        db.add(user)
        db.flush()  # 获取user.id
        
        # 创建对应的Actor
        actor = Actor(
            display_name=user_data["display_name"],
            actor_type=ActorType.HUMAN,
            user_id=user.id,
            capabilities=user_data["capabilities"],
            total_contributions=0,
            total_rewards=0,
            available_rewards=0,
            trust_score=0.8,
            reputation_score=0.75
        )
        db.add(actor)
        db.flush()
        
        # 更新用户的actor_id
        user.actor_id = actor.id
        
        created_users.append(user)
        print(f"  ✅ 创建用户: {user.username} ({user.email}) -> Actor: {actor.display_name}")
    
    db.commit()
    return created_users


def create_ai_agents(db: Session):
    """创建虚拟AI员工"""
    print("\n🤖 创建虚拟AI员工...")
    
    ai_agents_data = [
        {
            "display_name": "AI助手-小莫",
            "ai_config": {
                "role": "AI助手",
                "description": "公司的智能助手，擅长文案撰写、数据分析和日常事务处理",
                "capabilities": ["文案", "分析", "整理", "翻译"],
                "system_prompt": "你是公司AI助手小莫，负责帮助员工完成各种任务。回复要简洁专业。",
                "model": "deepseek",
                "temperature": 0.7
            },
            "capabilities": {"文案": 0.95, "分析": 0.9, "翻译": 0.85, "整理": 0.9}
        },
        {
            "display_name": "AI开发助手-代码侠",
            "ai_config": {
                "role": "开发助手",
                "description": "专业的开发助手，擅长代码编写、代码审查和技术方案设计",
                "capabilities": ["编程", "代码审查", "技术方案", "调试"],
                "system_prompt": "你是开发助手代码侠，帮助团队解决技术问题。提供清晰的代码示例和解决方案。",
                "model": "deepseek",
                "temperature": 0.3
            },
            "capabilities": {"编程": 0.92, "代码审查": 0.88, "技术方案": 0.85}
        },
        {
            "display_name": "AI产品助手-产品喵",
            "ai_config": {
                "role": "产品助手",
                "description": "产品经理助手，擅长需求分析、用户研究和产品规划",
                "capabilities": ["需求分析", "用户研究", "产品规划", "竞品分析"],
                "system_prompt": "你是产品助手产品喵，帮助产品团队进行需求分析和规划。回复要结构化、有逻辑。",
                "model": "deepseek",
                "temperature": 0.5
            },
            "capabilities": {"需求分析": 0.9, "用户研究": 0.88, "产品规划": 0.85}
        }
    ]
    
    created_agents = []
    for agent_data in ai_agents_data:
        # 检查是否已存在
        existing = db.query(Actor).filter(Actor.display_name == agent_data["display_name"]).first()
        if existing:
            print(f"  ⚠️  AI员工 {agent_data['display_name']} 已存在，跳过")
            created_agents.append(existing)
            continue
        
        actor = Actor(
            display_name=agent_data["display_name"],
            actor_type=ActorType.AI_AGENT,
            ai_config=agent_data["ai_config"],
            capabilities=agent_data["capabilities"],
            total_contributions=0,
            total_rewards=0,
            available_rewards=0,
            trust_score=0.95,
            reputation_score=0.9
        )
        db.add(actor)
        db.flush()
        created_agents.append(actor)
        print(f"  ✅ 创建AI员工: {actor.display_name}")
    
    db.commit()
    return created_agents


def create_sample_tasks(db: Session, users):
    """创建示例任务"""
    print("\n📝 创建示例任务...")
    
    # 获取所有Actor
    actors = db.query(Actor).filter(Actor.actor_type == ActorType.HUMAN).all()
    if not actors:
        print("  ⚠️  没有找到Actor，跳过任务创建")
        return []
    
    tasks_data = [
        {
            "type": "开发",
            "description": "完成用户登录模块的开发",
            "priority": 80,
            "status": "pending"
        },
        {
            "type": "产品",
            "description": "编写产品需求文档PRD v1.0",
            "priority": 75,
            "status": "in_progress"
        },
        {
            "type": "运营",
            "description": "策划618促销活动方案",
            "priority": 70,
            "status": "pending"
        },
        {
            "type": "设计",
            "description": "设计新版首页UI",
            "priority": 65,
            "status": "pending"
        },
        {
            "type": "开发",
            "description": "修复支付模块bug",
            "priority": 90,
            "status": "pending"
        }
    ]
    
    created_tasks = []
    for i, task_data in enumerate(tasks_data):
        # 检查是否已存在相同描述的任务
        existing = db.query(Task).filter(Task.description == task_data["description"]).first()
        if existing:
            print(f"  ⚠️  任务 '{task_data['description'][:20]}...' 已存在，跳过")
            created_tasks.append(existing)
            continue
        
        # 分配给不同的人
        assigned_actor = actors[i % len(actors)]
        
        task = Task(
            type=task_data["type"],
            description=task_data["description"],
            priority=task_data["priority"],
            status=task_data["status"],
            assigned_to=[str(assigned_actor.id)],
            deadline=datetime.now() + timedelta(days=7)
        )
        db.add(task)
        db.flush()
        created_tasks.append(task)
        print(f"  ✅ 创建任务: [{task.type}] {task.description[:30]}... -> {assigned_actor.display_name}")
    
    db.commit()
    return created_tasks


def create_sample_events(db: Session, users):
    """创建示例贡献事件"""
    print("\n📊 创建示例贡献事件...")
    
    # 获取所有Actor
    actors = db.query(Actor).filter(Actor.actor_type == ActorType.HUMAN).all()
    if not actors:
        print("  ⚠️  没有找到Actor，跳过事件创建")
        return []
    
    events_data = [
        {
            "action": "contribute",
            "content": "完成了用户认证模块的开发，实现了JWT登录、权限验证等功能",
            "contribution_type": "开发",
            "contribution_value": 85.5
        },
        {
            "action": "contribute",
            "content": "撰写了产品需求文档，包含10个核心功能的详细规划",
            "contribution_type": "产品",
            "contribution_value": 72.0
        },
        {
            "action": "contribute",
            "content": "优化了数据库查询性能，响应时间从500ms降低到50ms",
            "contribution_type": "优化",
            "contribution_value": 95.0
        },
        {
            "action": "say",
            "content": "在团队会议中提出了新的架构方案建议",
            "contribution_type": "建议",
            "contribution_value": 25.0
        },
        {
            "action": "contribute",
            "content": "修复了生产环境的关键bug，避免了潜在的数据丢失",
            "contribution_type": "修复",
            "contribution_value": 100.0
        }
    ]
    
    created_events = []
    for i, event_data in enumerate(events_data):
        actor = actors[i % len(actors)]
        
        event = Event(
            actor_id=actor.id,
            action=event_data["action"],
            content=event_data["content"],
            contribution_type=event_data["contribution_type"],
            contribution_value=event_data["contribution_value"],
            contribution_status=ContributionStatus.VERIFIED,
            ai_analysis={
                "understanding": f"识别到{event_data['contribution_type']}类型贡献",
                "value_factors": ["难度", "影响范围", "完成质量"],
                "confidence": 0.85
            }
        )
        db.add(event)
        db.flush()
        
        # 更新Actor的贡献值
        current = actor.total_contributions or Decimal('0')
        actor.total_contributions = current + Decimal(str(event_data["contribution_value"]))
        actor.contribution_count = (actor.contribution_count or 0) + 1
        
        created_events.append(event)
        print(f"  ✅ 创建事件: [{event.contribution_type}] 价值 {event.contribution_value} -> {actor.display_name}")
    
    db.commit()
    return created_events


def create_sample_notifications(db: Session, users):
    """创建示例通知"""
    print("\n🔔 创建示例通知...")
    
    # 获取Actor列表
    actors = db.query(Actor).filter(Actor.actor_type == ActorType.HUMAN).all()
    if not actors:
        print("  ⚠️  没有Actor，跳过通知创建")
        return []
    
    notifications_data = [
        {
            "title": "欢迎使用Mozart AI ERP系统",
            "message": "系统已成功初始化，您可以开始使用了！",
            "notification_type": "system"
        },
        {
            "title": "新任务分配",
            "message": "您有一个新的开发任务需要处理",
            "notification_type": "task_assigned"
        },
        {
            "title": "贡献已验证",
            "message": "您的贡献「用户认证模块开发」已被验证，贡献值：85.5",
            "notification_type": "contribution_verified"
        }
    ]
    
    created_notifications = []
    for i, notif_data in enumerate(notifications_data):
        actor = actors[i % len(actors)]
        
        notification = Notification(
            recipient_id=actor.id,
            title=notif_data["title"],
            message=notif_data["message"],
            notification_type=notif_data["notification_type"],
            is_read=False
        )
        db.add(notification)
        db.flush()
        created_notifications.append(notification)
        print(f"  ✅ 创建通知: {notif_data['title']} -> {actor.display_name}")
    
    db.commit()
    return created_notifications


def main():
    """主函数"""
    print("=" * 60)
    print("🌱 Mozart AI ERP 种子数据初始化")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # 1. 创建测试用户
        users = create_test_users(db)
        
        # 2. 创建虚拟AI员工
        ai_agents = create_ai_agents(db)
        
        # 3. 创建示例任务
        tasks = create_sample_tasks(db, users)
        
        # 4. 创建示例贡献事件
        events = create_sample_events(db, users)
        
        # 5. 创建示例通知
        notifications = create_sample_notifications(db, users)
        
        print("\n" + "=" * 60)
        print("✨ 种子数据初始化完成！")
        print("=" * 60)
        print(f"\n📊 数据统计:")
        print(f"   用户: {len(users)}")
        print(f"   AI员工: {len(ai_agents)}")
        print(f"   任务: {len(tasks)}")
        print(f"   贡献事件: {len(events)}")
        print(f"   通知: {len(notifications)}")
        
        print("\n🔐 测试账号:")
        print("   管理员: admin / admin123")
        print("   员工: zhangsan / 123456")
        print("   员工: lisi / 123456")
        print("   员工: wangwu / 123456")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
