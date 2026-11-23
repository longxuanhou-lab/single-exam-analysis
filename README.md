# 单场考试成绩分析

一套面向老师和学生的 Agent 技能，提供 WorkBuddy 版和通用版。它结合单场考试的成绩表、小题分、试卷和评分依据，生成带手绘封面的 A4 报告。

- **老师用**：按班级和科目分析得分，整理讲评建议和逐题明细。
- **学生用**：可生成全科个人报告，也可对一门科目逐题讲解，列出涉及的知识点和订正步骤。

## 在 WorkBuddy 使用

1. 在 WorkBuddy 技能市场搜索「单场考试成绩分析」。也可以[下载 v1.1.1 技能 ZIP](downloads/single-exam-analysis-workbuddy-v1.1.1.zip)，通过「技能 → 添加技能 → 上传技能」导入。
2. 提供同一场考试的成绩表、小题分、试卷。可一并提供答案、评分细则或学生答卷，帮助定位具体失分步骤。
3. 说明要做哪个班、哪一科，或哪位学生。例如「请分析示例1班这场考试的数学成绩，并出一份 PDF」或「请给学生甲做这场考试的数学个人报告，逐题讲解失分题」。

## 在其他 Agent 使用

[下载通用 Agent Skills 安装包](downloads/single-exam-analysis-agent-skills.zip)。安装包包含统计脚本、报告样式、九科封面和学生个人报告封面。

- **豆包工作**：如果客户端提供「导入本地技能」，选择这个 ZIP。豆包内的实际导入和运行尚未验证。
- **Codex、Claude Code、OpenClaw**：将 ZIP 解压到名为 `single-exam-analysis` 的文件夹，然后把整个文件夹放进该 Agent 的技能目录。在项目内，Codex 使用 `.agents/skills/`，Claude Code 使用 `.claude/skills/`，OpenClaw 可使用工作区的 `skills/`。

## 源码与运行条件

- [SKILL.md](SKILL.md) 包含技能说明。
- [数据和计算](references/data.md)、[报告写法和版式](references/reports.md) 说明统计口径和导出方式。
- 统计与排版脚本使用 Python 3.8 或以上版本。脚本直接导出 PDF 时需要 Chrome、Edge 或 Chromium，也可先导出 HTML，再用浏览器打印成 A4 PDF。
- 仓库提供技能规则、脚本和通用封面。使用时请提供自己的考试材料。

## 许可证

仓库中的代码、样式表和文档按 [MIT 许可证](LICENSE) 提供。`templates/` 目录下的封面插画及安装包中的同款插画不在该许可范围内。
