"""
基于AutoGen v0.4的出海顾问团队多智能体应用
包含多个专业智能体，协作为企业提供全面的出海方案
"""

from typing import List, cast, Dict, Any, Optional
import asyncio
import json
import os
from datetime import datetime

import chainlit as cl
import yaml
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.messages import TextMessage
from autogen_core.models import ChatCompletionClient

# PDF生成相关导入
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.pdfbase import pdfmetrics
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("警告：reportlab未安装，PDF生成功能将不可用。请运行：pip install reportlab")


def load_prompt_from_file(filename: str) -> str:
    """从prompts目录加载prompt文件"""
    prompt_path = os.path.join("prompts", filename)
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"警告：未找到prompt文件 {prompt_path}")
        return ""


def format_document_content(user_message: str, expert_analysis: Dict[str, str]) -> Dict[str, str]:
    """
    对专家分析内容进行格式规整，形成标准建议书格式
    
    Args:
        user_message: 用户原始需求
        expert_analysis: 各专家分析结果字典
    
    Returns:
        Dict[str, str]: 格式化后的文档内容
    """
    formatted_content = {}
    
    # 文档结构定义
    document_structure = {
        "executive_summary": "执行摘要",
        "enterprise_analysis": "企业现状分析",
        "market_analysis": "目标市场分析", 
        "strategic_planning": "出海战略规划",
        "operations_planning": "运营实施方案",
        "marketing_strategy": "营销推广策略",
        "legal_compliance": "法律合规要求",
        "financial_planning": "财务规划方案",
        "implementation_timeline": "实施时间表",
        "risk_assessment": "风险评估与应对",
        "conclusion": "结论与建议"
    }
    
    # 专家映射
    expert_mapping = {
        "enterprise_knowledge_expert": "enterprise_analysis",
        "market_analysis_expert": "market_analysis",
        "strategic_planning_expert": "strategic_planning",
        "operations_planning_expert": "operations_planning",
        "marketing_promotion_expert": "marketing_strategy",
        "legal_compliance_expert": "legal_compliance",
        "financial_planning_expert": "financial_planning",
        "implementation_planning_expert": "implementation_timeline",
        "solution_expert": "risk_assessment",
        "senior_advisory_expert": "conclusion"
    }
    
    # 处理各专家内容
    for expert_key, content in expert_analysis.items():
        if expert_key in expert_mapping:
            section_key = expert_mapping[expert_key]
            
            # 清理内容，移除智能体标识
            cleaned_content = content
            for prefix in ["【企业知识专家】", "【市场分析专家】", "【战略规划专家】", 
                          "【运营规划专家】", "【营销推广专家】", "【法律合规专家】", 
                          "【财务规划专家】", "【实施计划专家】", "【方案专家】", "【资深顾问专家】"]:
                cleaned_content = cleaned_content.replace(prefix, "").strip()
            
            # 格式化内容
            formatted_content[section_key] = cleaned_content
    
    # 生成执行摘要
    executive_summary = f"""
# 企业出海方案执行摘要

## 项目背景
{user_message}

## 方案概述
本方案基于多领域专家的专业分析，为企业提供全面的海外市场拓展指导。方案涵盖了从市场分析到实施落地的各个环节，确保企业能够系统性地推进海外业务发展。

## 核心建议
- 市场进入策略：根据目标市场特点制定差异化进入策略
- 运营体系设计：建立适合海外市场的运营模式和组织架构
- 风险管控机制：建立完善的法律合规和财务风险管控体系
- 实施路径规划：制定分阶段、可操作的实施计划

## 预期成果
通过本方案的实施，企业将获得：
1. 清晰的市场定位和竞争优势
2. 完善的海外运营体系
3. 有效的风险管控机制
4. 可执行的实施路径
"""
    
    formatted_content["executive_summary"] = executive_summary
    
    # 添加风险评估与应对（如果方案专家没有提供）
    if "risk_assessment" not in formatted_content:
        formatted_content["risk_assessment"] = """
# 风险评估与应对

## 主要风险识别
1. **市场风险**：目标市场环境变化、竞争加剧
2. **运营风险**：海外运营成本超预期、人才短缺
3. **法律风险**：合规要求变化、知识产权保护
4. **财务风险**：汇率波动、资金流动性风险

## 风险应对策略
1. **建立风险监控机制**：定期评估市场环境和运营状况
2. **制定应急预案**：针对各类风险制定详细的应对预案
3. **加强合规管理**：建立专业的法律合规团队
4. **优化财务结构**：采用多元化的融资和风险对冲策略
"""
    
    # 添加结论与建议（如果资深顾问专家没有提供）
    if "conclusion" not in formatted_content:
        formatted_content["conclusion"] = """
# 结论与建议

## 方案总结
本出海方案基于多领域专家的专业分析，为企业提供了全面的海外拓展指导。方案涵盖了从市场分析到实施落地的各个环节，确保企业能够系统性地推进海外业务发展。

## 实施建议
1. **分阶段实施**：按照方案中的时间表，分阶段推进各项措施
2. **持续优化**：根据实施过程中的反馈，持续优化方案内容
3. **资源保障**：确保人力、财力等资源的充分投入
4. **风险管控**：建立完善的风险监控和应对机制

## 后续支持
建议企业建立专门的海外业务团队，负责方案的实施和后续优化工作。同时，可以考虑寻求专业咨询机构的持续支持。
"""
    
    return formatted_content


def generate_overseas_plan_pdf(user_message: str, expert_analysis: Dict[str, str]) -> str:
    """
    生成出海方案PDF文档
    
    Args:
        user_message: 用户原始需求
        expert_analysis: 各专家分析结果字典
    
    Returns:
        str: PDF文件路径
    """
    if not PDF_AVAILABLE:
        raise ImportError("reportlab未安装，无法生成PDF")
    
    # 首先进行文档格式规整
    formatted_content = format_document_content(user_message, expert_analysis)
    
    # 创建输出目录
    output_dir = "outputs"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"overseas_plan_{timestamp}.pdf"
    filepath = os.path.join(output_dir, filename)
    
    # 创建PDF文档
    doc = SimpleDocTemplate(filepath, pagesize=A4)
    story = []
    
    # 注册中文字体
    try:
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.pdfbase.cidfonts import UnicodeCIDFont
        
        # 注册Unicode中文字体
        pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
        chinese_font = 'STSong-Light'
    except:
        try:
            # 备用方案：使用系统字体
            if os.path.exists('/System/Library/Fonts/PingFang.ttc'):  # macOS
                pdfmetrics.registerFont(TTFont('PingFang', '/System/Library/Fonts/PingFang.ttc'))
                chinese_font = 'PingFang'
            elif os.path.exists('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'):  # Linux
                pdfmetrics.registerFont(TTFont('DejaVu', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
                chinese_font = 'DejaVu'
            elif os.path.exists('C:/Windows/Fonts/simsun.ttc'):  # Windows
                pdfmetrics.registerFont(TTFont('SimSun', 'C:/Windows/Fonts/simsun.ttc'))
                chinese_font = 'SimSun'
            else:
                chinese_font = 'Helvetica'  # 默认字体
        except:
            chinese_font = 'Helvetica'  # 默认字体
    
    # 获取样式
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1,  # 居中
        textColor=colors.darkblue,
        fontName=chinese_font
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        spaceBefore=20,
        textColor=colors.darkblue,
        fontName=chinese_font
    )
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName=chinese_font,
        fontSize=10,
        leading=14
    )
    
    # 添加标题
    story.append(Paragraph("企业出海方案建议书", title_style))
    story.append(Spacer(1, 20))
    
    # 添加生成时间
    story.append(Paragraph(f"生成时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}", normal_style))
    story.append(Spacer(1, 20))
    
    # 按标准格式添加各章节内容
    document_structure = [
        ("executive_summary", "执行摘要"),
        ("enterprise_analysis", "企业现状分析"),
        ("market_analysis", "目标市场分析"),
        ("strategic_planning", "出海战略规划"),
        ("operations_planning", "运营实施方案"),
        ("marketing_strategy", "营销推广策略"),
        ("legal_compliance", "法律合规要求"),
        ("financial_planning", "财务规划方案"),
        ("implementation_timeline", "实施时间表"),
        ("risk_assessment", "风险评估与应对"),
        ("conclusion", "结论与建议")
    ]
    
    for section_key, section_title in document_structure:
        if section_key in formatted_content:
            story.append(Paragraph(section_title, heading_style))
            
            content = formatted_content[section_key]
            
            # 处理长文本，避免PDF生成问题
            if len(content) > 2000:
                # 分段处理长文本
                paragraphs = content.split('\n\n')
                for para in paragraphs:
                    if para.strip():
                        story.append(Paragraph(para.strip(), normal_style))
                        story.append(Spacer(1, 5))
            else:
                story.append(Paragraph(content, normal_style))
            
            story.append(Spacer(1, 15))
    
    # 生成PDF
    doc.build(story)
    
    return filepath


class OverseasAdvisorySwarm:
    """出海顾问团队智能体群组"""
    
    def __init__(self, model_config: Dict[str, Any]):
        """初始化顾问团队"""
        self.model_config = model_config
        self.model_client = self._create_model_client(model_config)
        self.agents: Dict[str, AssistantAgent] = {}
        self.team: Optional[SelectorGroupChat] = None
        self.agent_call_count: Dict[str, int] = {}  # 跟踪每个智能体的调用次数
        self.max_calls_per_agent = 3  # 每个智能体最多调用3次
        self._setup_agents()
        self._setup_team()
    
    def _create_model_client(self, model_config: Dict[str, Any]) -> ChatCompletionClient:
        """创建模型客户端"""
        return ChatCompletionClient.load_component(model_config)

    def _setup_agents(self):
        """设置各个专业智能体"""
        
        # 企业知识智能体
        self.agents['enterprise_knowledge'] = AssistantAgent(
            name="enterprise_knowledge_expert",
            model_client=self.model_client,
            system_message=load_prompt_from_file("enterprise_knowledge_expert.txt"),
        )
        
        # 市场分析智能体
        self.agents['market_analysis'] = AssistantAgent(
            name="market_analysis_expert",
            model_client=self.model_client,
            system_message=load_prompt_from_file("market_analysis_expert.txt"),
        )
        
        # 战略规划智能体
        self.agents['strategic_planning'] = AssistantAgent(
            name="strategic_planning_expert",
            model_client=self.model_client,
            system_message=load_prompt_from_file("strategic_planning_expert.txt"),
        )
        
        # 运营规划智能体
        self.agents['operations_planning'] = AssistantAgent(
            name="operations_planning_expert",
            model_client=self.model_client,
            system_message=load_prompt_from_file("operations_planning_expert.txt"),
        )
        
        # 营销推广智能体
        self.agents['marketing_promotion'] = AssistantAgent(
            name="marketing_promotion_expert",
            model_client=self.model_client,
            system_message=load_prompt_from_file("marketing_promotion_expert.txt"),
        )
        
        # 法律合规智能体
        self.agents['legal_compliance'] = AssistantAgent(
            name="legal_compliance_expert",
            model_client=self.model_client,
            system_message=load_prompt_from_file("legal_compliance_expert.txt"),
        )
        
        # 财务规划智能体
        self.agents['financial_planning'] = AssistantAgent(
            name="financial_planning_expert",
            model_client=self.model_client,
            system_message=load_prompt_from_file("financial_planning_expert.txt"),
        )
        
        # 实施计划智能体
        self.agents['implementation_planning'] = AssistantAgent(
            name="implementation_planning_expert",
            model_client=self.model_client,
            system_message=load_prompt_from_file("implementation_planning_expert.txt"),
        )
        
        # 方案专家智能体（选择器和评估者）
        self.agents['solution_expert'] = AssistantAgent(
            name="solution_expert",
            model_client=self.model_client,
            system_message=load_prompt_from_file("solution_expert.txt"),
        )
        
        # 资深顾问智能体（最终协调者）
        self.agents['senior_advisor'] = AssistantAgent(
            name="senior_advisory_expert",
            model_client=self.model_client,
            system_message=load_prompt_from_file("senior_advisory_expert.txt"),
        )
        
        # 初始化调用次数计数器
        for agent_name in self.agents.keys():
            self.agent_call_count[agent_name] = 0
    
    def _setup_team(self):
        """设置团队协作"""
        # 获取所有智能体
        participants = list(self.agents.values())
        
        # 设置终止条件 - 只有当资深顾问专家确认所有专家都达到满意水平时才结束
        termination_condition = TextMentionTermination("出海方案完成")
        
        # 创建选择器团队 - 使用更详细的选择器提示词
        selector_prompt = """
你是方案专家，负责协调出海顾问团队的咨询流程。

**你的核心职责：**
1. 根据用户需求，智能选择下一个发言的专家
2. **对每个专家的输出进行质量评估（这是必须的！）**
3. 如果专家输出不满足要求，要求其重新输出
4. 确保所有专家都达到满意水平后再进行最终整合

**评估标准（1-10分）：**
- 专业性：是否体现了该领域的专业水平
- 完整性：是否全面覆盖了相关要点
- 实用性：建议是否具有可操作性
- 相关性：是否直接回应了用户的具体需求
- 创新性：是否有独特的见解和方案

**工作流程：**
1. 分析用户需求，确定需要哪些专家参与
2. 选择第一个专家发言
3. **在每个专家发言后，你必须进行评估：**
   - 给出评分（1-10分）
   - 指出优点和不足
   - 如果评分低于7分，明确要求该专家重新输出
4. 只有当所有专家都达到满意水平后，选择资深顾问专家进行最终整合

**重要提醒：**
- 你必须对每个专家的输出进行评估，这是强制要求
- 评估要具体、客观、有建设性
- 如果专家输出质量不高，不要急于选择下一个专家，而是要求重新输出
- 确保最终方案的质量和完整性
- **每个专家最多只能被调用3次，超过限制后请选择其他专家或进行最终整合**

**评估格式示例：**
【方案专家】
对[专家名称]的评估：
- 专业性：X/10
- 完整性：X/10
- 实用性：X/10
- 相关性：X/10
- 创新性：X/10
总体评分：X/10

优点：[具体优点]
不足：[具体不足]

[如果评分低于7分且该专家调用次数少于3次：请[专家名称]重新思考并补充完善，重点关注[具体不足点]]
[如果评分低于7分且该专家调用次数已达3次：该专家已达到最大调用次数，请选择其他专家或进行最终整合]

可选的专家包括：
- enterprise_knowledge_expert: 企业知识专家
- market_analysis_expert: 市场分析专家
- strategic_planning_expert: 战略规划专家
- operations_planning_expert: 运营规划专家
- marketing_promotion_expert: 营销推广专家
- legal_compliance_expert: 法律合规专家
- financial_planning_expert: 财务规划专家
- implementation_planning_expert: 实施计划专家
- senior_advisory_expert: 资深顾问专家

请记住：每个专家发言后，你都必须进行评估！每个专家最多只能被调用3次！
"""
        
        self.team = SelectorGroupChat(
            participants=participants,
            model_client=self.model_client,
            selector_prompt=selector_prompt,
            termination_condition=termination_condition,
        )
    
    async def start_consultation(self, user_message: str, callback=None):
        """开始咨询流程，支持流式输出回调和PDF生成"""
        if not self.team:
            return "团队未初始化"
        
        try:
            print(f"DEBUG: start_consultation 开始，用户消息: {user_message}")
            
            # 重置团队状态和调用次数
            await self.team.reset()
            for agent_name in self.agent_call_count.keys():
                self.agent_call_count[agent_name] = 0
            
            # 存储各专家的分析结果
            expert_analysis = {}
            
            # 构建任务描述
            task = f"""
客户需求：{user_message}

请各位专家按照以下流程进行咨询分析：

**工作流程：**
1. **方案专家首先分析用户需求，确定需要哪些专家的参与**
2. 企业知识专家：了解企业基本情况和出海需求
3. **方案专家评估企业知识专家的输出，如果不满要求要求重新输出**
4. 市场分析专家：分析目标市场机会和风险
5. **方案专家评估市场分析专家的输出，如果不满要求要求重新输出**
6. 战略规划专家：制定出海战略和进入策略
7. **方案专家评估战略规划专家的输出，如果不满要求要求重新输出**
8. 运营规划专家：设计运营体系和组织架构
9. **方案专家评估运营规划专家的输出，如果不满要求要求重新输出**
10. 营销推广专家：制定品牌推广和营销策略
11. **方案专家评估营销推广专家的输出，如果不满要求要求重新输出**
12. 法律合规专家：提供法律合规保障方案
13. **方案专家评估法律合规专家的输出，如果不满要求要求重新输出**
14. 财务规划专家：制定财务规划和风险管控
15. **方案专家评估财务规划专家的输出，如果不满要求要求重新输出**
16. 实施计划专家：整合为可执行的实施计划
17. **方案专家评估实施计划专家的输出，如果不满要求要求重新输出**
18. 资深顾问专家：最终协调整合，形成完整方案并生成PDF

**重要说明：**
- **方案专家必须对每个专家的输出进行质量评估**
- **评估标准：专业性、完整性、实用性、相关性、创新性（1-10分）**
- **如果某个专家的输出评分低于7分，方案专家必须要求其重新输出**
- **每个专家最多只能被调用3次，超过限制后请选择其他专家或进行最终整合**
- **只有当所有专家都达到满意水平后，才能选择资深顾问专家进行最终整合**
- **方案专家要确保最终方案的质量和完整性**

**评估格式要求：**
方案专家在评估时必须使用以下格式：
【方案专家】
对[专家名称]的评估：
- 专业性：X/10
- 完整性：X/10
- 实用性：X/10
- 相关性：X/10
- 创新性：X/10
总体评分：X/10

优点：[具体优点]
不足：[具体不足]

[如果评分低于7分且该专家调用次数少于3次：请[专家名称]重新思考并补充完善，重点关注[具体不足点]]
[如果评分低于7分且该专家调用次数已达3次：该专家已达到最大调用次数，请选择其他专家或进行最终整合]

请方案专家开始分析用户需求并协调整个咨询过程。记住：每个专家发言后都要进行评估！每个专家最多只能被调用3次！
"""
            
            # 如果有回调函数，使用流式输出
            if callback:
                async for message in self.team.run_stream(task=task):
                    # 解析消息内容
                    if hasattr(message, 'content') and message.content:
                        content = str(message.content)
                        
                        # 提取智能体名称和回复内容
                        agent_name = "未知专家"
                        agent_key = "unknown"
                        
                        if "【企业知识专家】" in content:
                            agent_name = "🏢 企业知识专家"
                            agent_key = "enterprise_knowledge_expert"
                        elif "【市场分析专家】" in content:
                            agent_name = "📈 市场分析专家"
                            agent_key = "market_analysis_expert"
                        elif "【战略规划专家】" in content:
                            agent_name = "🎯 战略规划专家"
                            agent_key = "strategic_planning_expert"
                        elif "【运营规划专家】" in content:
                            agent_name = "⚙️ 运营规划专家"
                            agent_key = "operations_planning_expert"
                        elif "【营销推广专家】" in content:
                            agent_name = "📢 营销推广专家"
                            agent_key = "marketing_promotion_expert"
                        elif "【法律合规专家】" in content:
                            agent_name = "⚖️ 法律合规专家"
                            agent_key = "legal_compliance_expert"
                        elif "【财务规划专家】" in content:
                            agent_name = "💰 财务规划专家"
                            agent_key = "financial_planning_expert"
                        elif "【实施计划专家】" in content:
                            agent_name = "📋 实施计划专家"
                            agent_key = "implementation_planning_expert"
                        elif "【方案专家】" in content:
                            agent_name = "🎯 方案专家"
                            agent_key = "solution_expert"
                        elif "【资深顾问专家】" in content:
                            agent_name = "🎓 资深顾问专家"
                            agent_key = "senior_advisory_expert"
                            
                            # 如果是资深顾问专家，生成PDF
                            if "出海方案完成" in content:
                                try:
                                    pdf_path = generate_overseas_plan_pdf(user_message, expert_analysis)
                                    # 在Chainlit中显示PDF下载链接
                                    await callback("PDF生成", f"出海方案PDF已生成：{pdf_path}")
                                except Exception as e:
                                    await callback("❌ PDF生成失败", f"PDF生成过程中遇到错误：{str(e)}")
                        
                        # 更新调用次数
                        if agent_key != "unknown":
                            # 找到对应的智能体键名
                            for key, agent in self.agents.items():
                                if agent.name == agent_key:
                                    self.agent_call_count[key] += 1
                                    print(f"DEBUG: {agent_key} 调用次数: {self.agent_call_count[key]}")
                                    break
                        
                        # 存储专家分析结果
                        expert_analysis[agent_key] = content
                        
                        # 调用回调函数显示消息
                        await callback(agent_name, content)
                        
                        # 检查是否达到最大调用次数
                        if agent_key != "unknown" and agent_key != "solution_expert" and agent_key != "senior_advisory_expert":
                            for key, agent in self.agents.items():
                                if agent.name == agent_key and self.agent_call_count[key] >= self.max_calls_per_agent:
                                    print(f"DEBUG: {agent_key} 已达到最大调用次数 {self.max_calls_per_agent}")
                                    break
            else:
                # 如果没有回调函数，使用普通输出
                result = await self.team.run(task=task)
                return str(result)
            
        except Exception as e:
            print(f"DEBUG: start_consultation 发生错误: {str(e)}")
            return f"咨询过程中遇到错误：{str(e)}"


@cl.set_starters
async def set_starters() -> List[cl.Starter]:
    """设置启动选项"""
    return [
        cl.Starter(
            label="🌍 企业出海全面咨询",
            message="我需要为我的企业制定一个全面的出海方案，包括市场分析、战略规划、运营计划等。",
        ),
        cl.Starter(
            label="📊 目标市场分析",
            message="请帮我分析目标海外市场的机会和风险。",
        ),
        cl.Starter(
            label="🎯 出海战略规划",
            message="我需要制定企业出海的长期战略规划。",
        ),
        cl.Starter(
            label="⚖️ 法律合规咨询",
            message="请帮我了解目标市场的法律法规和合规要求。",
        ),
        cl.Starter(
            label="💰 财务规划咨询",
            message="我需要制定出海的投资预算和财务规划。",
        ),
    ]


@cl.on_chat_start
async def on_chat_start():
    """聊天开始时的初始化"""
    
    # 加载模型配置
    try:
        with open("model_config.yaml", "r", encoding="utf-8") as f:
            model_config = yaml.safe_load(f)
    except FileNotFoundError:
        await cl.Message(
            content="❌ 未找到模型配置文件 model_config.yaml，请先配置模型参数。"
        ).send()
        return
    
    # 初始化出海顾问团队
    try:
        swarm = OverseasAdvisorySwarm(model_config)
        cl.user_session.set("swarm", swarm)
        
        # 发送欢迎消息
        welcome_msg = """
🌟 **欢迎使用出海顾问团队智能体系统！**

我们的专业团队包括：
- 🏢 **企业知识专家**：深入了解您的企业情况
- 📈 **市场分析专家**：分析目标市场机会与风险
- 🎯 **战略规划专家**：制定出海战略和进入策略
- ⚙️ **运营规划专家**：设计运营体系和组织架构
- 📢 **营销推广专家**：制定品牌推广和营销策略
- ⚖️ **法律合规专家**：提供法律合规保障方案
- 💰 **财务规划专家**：制定财务规划和风险管控
- 📋 **实施计划专家**：整合为可执行的实施计划
- 🎓 **资深顾问专家**：协调整合，形成最终方案

请描述您的企业出海需求，我们的专业团队将为您提供全面的咨询服务！
        """
        
        await cl.Message(content=welcome_msg).send()
        
    except Exception as e:
        await cl.Message(
            content=f"❌ 初始化出海顾问团队时遇到错误：{str(e)}"
        ).send()


@cl.on_message
async def on_message(message: cl.Message) -> None:
    """处理用户消息"""
    swarm = cast(OverseasAdvisorySwarm, cl.user_session.get("swarm"))
    
    if not swarm:
        await cl.Message(content="❌ 系统未初始化，请刷新页面重试。").send()
        return
    
    # 显示处理状态
    processing_msg = cl.Message(content="🤖 出海顾问团队正在为您分析需求，请稍候...")
    await processing_msg.send()
    
    try:
        # 存储所有专家回复
        expert_responses = []
        
        # 定义回调函数来显示每个智能体的回复
        async def display_agent_message(agent_name: str, content: str):
            """显示智能体消息的回调函数"""
            print(f"DEBUG: 收到专家回复 - {agent_name}")  # 调试信息
            
            # 存储回复
            expert_responses.append({
                "agent_name": agent_name,
                "content": content
            })
            
            # 发送智能体回复
            await cl.Message(
                content=f"## {agent_name}\n\n{content}",
                author=agent_name
            ).send()
        
        # 开始咨询流程，使用流式输出
        print(f"DEBUG: 开始咨询流程，用户消息: {message.content}")  # 调试信息
        await swarm.start_consultation(message.content, callback=display_agent_message)
        
        # 咨询完成后，移除处理状态消息
        await processing_msg.remove()
        
        # 发送完成消息
        print(f"DEBUG: 咨询完成，共收到 {len(expert_responses)} 个回复")  # 调试信息
        await cl.Message(
            content=f"🎉 出海顾问团队分析完成！\n\n✅ 共完成 {len(expert_responses)} 位专家分析\n📄 PDF方案已生成，请查看上方链接。"
        ).send()
        
    except Exception as e:
        await processing_msg.remove()
        print(f"DEBUG: 发生错误 - {str(e)}")  # 调试信息
        await cl.Message(
            content=f"❌ 处理过程中遇到错误：{str(e)}\n\n请检查模型配置或稍后重试。"
        ).send()


if __name__ == "__main__":
    # 开发时可以直接运行测试
    print("出海顾问团队智能体应用已启动！")
    print("请使用 'chainlit run app_swarm.py' 命令启动Web界面。") 