# HENAU 实验室安全准入考试自动化辅助项目

[![Python](https://img.shields.io/badge/Python-3.8+-blue)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/Playwright-Latest-green)](https://playwright.dev/python/)
[![DeepSeek](https://img.shields.io/badge/LLM-DeepSeek-orange)](https://platform.deepseek.com/)

**一个基于 Playwright + Python + DeepSeek LLM 的全自动实验室安全准入考试辅助工具**

本项目实现了从登录、提取题目、调用大模型推理答案、自动答题、保存多选题、提交试卷到打开证书页面的完整闭环自动化流程，已在河南农业大学实验室安全准入考试（2025年版本）中验证通过。

> ⚠️ **重要声明**  
> 本项目仅供学习和研究使用，旨在练习 Playwright 自动化测试、DOM 结构解析、LLM 提示工程、反防作弊机制等技术。  
> 请严格遵守学校相关规定，**严禁用于任何违规或作弊行为**。作者不对任何不当使用承担责任。

## 项目功能

- 自动处理全屏确认、防切屏警告、考试中断恢复等弹窗
- 保存并复用登录状态（免重复登录）
- 精准提取全部 90 道题（单选 40 + 多选 10 + 判断 40），并正确划分题型标题
- 调用 DeepSeek 大模型获取完整答案（支持单选、多选、判断）
- 智能解析 LLM 输出（鲁棒支持多种格式）
- 直接操作 `<input>` 元素，稳定选中选项
- 多选题自动点击多个选项 + 点击“保存”按钮
- 模拟人类答题节奏（随机停顿 + 滚动），有效规避防作弊检测
- 答题完成后自动打开证书页面并截图留证
- 全程日志输出，操作友好

## 环境准备

### 1. 安装 Python（推荐 3.8 ~ 3.12）

下载地址：https://www.python.org/downloads/

安装时请务必勾选 **Add Python to PATH**

### 2. 安装 Playwright

打开终端（Windows：cmd 或 PowerShell），执行以下命令：

```bash
pip install playwright
```

然后安装浏览器驱动（必须执行这一步）：

```bash
playwright install
```

这一步会自动下载 Chromium、Firefox 和 WebKit 浏览器（约 200~300MB），请保持网络畅通。

> 官方文档：https://playwright.dev/python/docs/intro

### 3. 安装项目依赖（如果有其他第三方库）

本项目主要依赖 Playwright，通常无需额外安装。若提示缺少模块，可执行：

```bash
pip install requests  # 如有需要
```

## 使用方法

### 步骤 1：首次登录获取登录态

1. 将项目文件夹中的 `login2getcookie.py` 运行：

```bash
python login2getcookie.py
```

2. 浏览器会自动打开登录页面，按正常流程输入学号、密码完成登录（包括验证码、短信验证等）。
3. 登录成功后，终端会提示 **“按 Enter 保存登录状态...”**，此时按下回车键。
4. 程序会自动生成 `storage_state.json` 文件保存登录态，后续运行无需再次登录。

### 步骤 2：配置 DeepSeek API Key

1. 打开项目中的 `deepseek.py` 文件
2. 找到以下位置：

```python
API_KEY = "sk-your-api-key-here"
```

3. 替换为你的 DeepSeek API Key（从 https://platform.deepseek.com/api-keys 获取）

### 步骤 3：运行主程序

```bash
python LabSafetyExam.py
```

程序将自动：

- 复用登录态进入考试页面
- 等待题目加载并处理所有弹窗
- 提取全部题目并保存为 `实验室安全考试题目.txt`
- 调用 DeepSeek 获取答案并保存为 `GetAnswer.txt`
- 自动答题（单选、多选、判断）
- 答题完成后提示你手动提交（遵守五分钟内不得交卷规则）
- 你手动提交后，按任意键自动打开证书页面并截图保存为 `证书截图.png`

## 文件说明

- `LabSafetyExam.py`：主程序，完整自动化流程
- `login2getcookie.py`：用于首次登录并保存 `storage_state.json`
- `deepseek.py`：DeepSeek API 调用封装（需填入 API Key）
- `storage_state.json`：登录状态文件（自动生成）
- `实验室安全考试题目.txt`：提取的原始题目（用于调试）
- `GetAnswer.txt`：大模型返回的答案原文
- `证书截图.png`：最终证书页面截图

## 注意事项

- 请确保网络通畅，尤其是首次运行 Playwright 下载浏览器时
- 考试期间请勿频繁切换窗口或最小化浏览器，以免触发防切屏检测
- 提交前务必检查是否有未保存的多选题
- 遵守学校规定，五分钟内请勿点击提交
- 如遇题目结构变化，可手动调整题号范围（目前固定：1-40 单选，41-50 多选，51-90 判断）

## 致谢

- Playwright 团队
- DeepSeek 提供强大 LLM 支持
- 所有为自动化测试技术做出贡献的开发者

---

**学习技术，合理使用，诚信为本。**

祝你顺利通过实验室安全准入考试，开启科研之路！

Made with ❤️ by 一位热爱自动化的学生

2025年12月