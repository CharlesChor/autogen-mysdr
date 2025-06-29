# 🌍 出海顾问团队智能体系统 (AutoGen Swarm)

基于 AutoGen v0.4 的多智能体出海顾问团队应用，为企业提供全面的海外市场拓展咨询服务。

## 🚀 系统特点

- **多专业智能体协作**：9个专业领域智能体协同工作
- **AutoGen v0.4架构**：使用最新的AutoGen框架
- **Chainlit Web界面**：友好的用户交互界面
- **全流程咨询**：从企业分析到实施计划的完整服务

## 🤖 专业智能体团队

### 核心专家团队
1. **🏢 企业知识专家** - 深入了解企业情况和出海需求
2. **📈 市场分析专家** - 分析目标市场机会与风险
3. **🎯 战略规划专家** - 制定出海战略和进入策略
4. **⚙️ 运营规划专家** - 设计运营体系和组织架构
5. **📢 营销推广专家** - 制定品牌推广和营销策略
6. **⚖️ 法律合规专家** - 提供法律合规保障方案
7. **💰 财务规划专家** - 制定财务规划和风险管控
8. **📋 实施计划专家** - 整合为可执行的实施计划
9. **🎓 资深顾问专家** - 协调整合，形成最终方案

## 🛠️ 环境要求

### Python 版本
- **Python 3.12+** (AutoGen v0.4 要求)

### 主要依赖
```bash
autogen-agentchat>=0.4
autogen-ext[openai]>=0.4
autogen-core>=0.4
chainlit>=2.5
pyyaml
```

## 📦 安装步骤

### 1. 创建Python 3.12环境
```bash
# 使用conda创建新环境
conda create -n autogen312 python=3.12 -y
conda activate autogen312
```

### 2. 安装依赖包
```bash
# 安装AutoGen v0.4
pip install "autogen-agentchat>=0.4" "autogen-ext[openai]>=0.4" "autogen-core>=0.4"

# 安装Chainlit和其他依赖
pip install chainlit pyyaml
```

### 3. 配置模型
复制并编辑模型配置文件：
```bash
cp model_config_template.yaml model_config.yaml
```

在 `model_config.yaml` 中配置您的模型参数：
```yaml
model: "gpt-4o"  # 或其他支持的模型
api_key: "your-api-key-here"
base_url: "https://api.openai.com/v1"  # 可选，自定义API端点
```

## 🚀 启动应用

### 启动Web界面
```bash
chainlit run app_swarm.py
```

### 访问应用
打开浏览器访问：`http://localhost:8000`

## 💡 使用方法

### 1. 选择咨询类型
应用提供多个预设的咨询场景：
- 🌍 企业出海全面咨询
- 📊 目标市场分析
- 🎯 出海战略规划
- ⚖️ 法律合规咨询
- 💰 财务规划咨询

### 2. 描述需求
详细描述您的企业情况和出海需求，包括：
- 企业基本信息（行业、规模、产品/服务）
- 目标市场（国家/地区）
- 出海目标和时间计划
- 现有资源和能力
- 关注的重点问题

### 3. 获取专业建议
系统将按照以下流程进行分析：
1. **企业知识专家** 了解企业基本情况
2. **市场分析专家** 分析目标市场
3. **战略规划专家** 制定出海战略
4. **运营规划专家** 设计运营方案
5. **营销推广专家** 制定营销策略
6. **法律合规专家** 提供合规建议
7. **财务规划专家** 制定财务计划
8. **实施计划专家** 整合实施方案
9. **资深顾问专家** 形成最终建议

## 🔧 技术架构

### AutoGen v0.4 特性
- **RoundRobinGroupChat**: 轮询式团队协作
- **TextMentionTermination**: 智能对话终止条件
- **OpenAIChatCompletionClient**: 统一的模型客户端

### 系统架构
```
用户请求 → Chainlit界面 → OverseasAdvisorySwarm → 
多智能体团队协作 → 生成综合建议 → 返回结果
```

## 📝 示例对话

**用户输入：**
```
我是一家做智能家居产品的科技公司，现在想要进入欧洲市场，
特别是德国和法国。我们的主要产品是智能音箱和智能照明系统。
希望了解市场机会、进入策略和需要注意的法律问题。
```

**系统输出：**
系统会依次由各专家提供分析，最终形成包含以下内容的综合报告：
- 企业出海准备度评估
- 德法智能家居市场分析
- 进入策略建议
- 运营架构设计
- 营销推广方案
- 法律合规要求
- 财务投资规划
- 详细实施时间表

## 🔍 故障排除

### 常见问题

1. **Python版本问题**
   ```
   Error: AutoGen v0.4 requires Python 3.10+
   ```
   解决：确保使用Python 3.12+

2. **依赖冲突**
   ```
   ERROR: pip's dependency resolver conflicts
   ```
   解决：使用新的conda环境重新安装

3. **模型配置错误**
   ```
   Error: 未找到模型配置文件
   ```
   解决：确保 `model_config.yaml` 文件存在且配置正确

4. **API密钥问题**
   ```
   Error: Invalid API key
   ```
   解决：检查 `model_config.yaml` 中的API密钥是否正确

## 🔄 更新日志

### v1.0.0 (2025-01-XX)
- ✅ 基于AutoGen v0.4的多智能体架构
- ✅ 9个专业领域智能体
- ✅ Chainlit Web界面
- ✅ 完整的出海咨询流程
- ✅ 支持自定义模型配置

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进系统：

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 发起Pull Request

## 📄 许可证

本项目采用 MIT 许可证。

## 📞 技术支持

如有技术问题，请：
1. 查看故障排除部分
2. 提交GitHub Issue
3. 联系技术支持团队

---

**注意**：使用前请确保已正确配置模型API密钥，并遵守相关服务条款。 