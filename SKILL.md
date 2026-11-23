---
name: single-exam-analysis
version: "1.1.1"
display_name: "单场考试成绩分析"
display_name_en: "Single-Exam Performance Analysis"
description: "分析单场考试的班级和学科成绩，或制作全科及单科学生个人学情报告。结合试卷、评分依据和小题分生成带手绘封面的中文 PDF。老师版有讲评建议，学生单科版逐题讲解失分题和知识点。"
description_zh: "结合本场考试的成绩、小题分、试卷和评分依据，生成班级学科分析或学生个人 PDF。支持单科逐题讲解、知识点分析和订正建议。"
description_en: "Turn scores, question-level marks, exam papers, and marking guides into PDF reports for teachers or students, with detailed review for a single subject."
author: "单场考试成绩分析项目"
---

# 单场考试成绩分析

只分析本场考试。先确认用户要哪个班、哪些产物。用户已经指定班级或学生时直接做，该学生班级可由成绩表唯一确认时直接沿用。年级数据用于提供参照。默认按指定班级输出有有效成绩的学科 PDF，打包交付。按需为指定学生生成个人 PDF，也可按班为每名学生分别生成、逐份检查后打包。班级总报告、年级总报告、考点工作簿仅在用户明确要求时交付，个人分析表格不作为附带产物。

用户指定某个学生和一门科目时，读 @references/student-subject.md。只读取该科试卷、评分依据和所需成绩。对全卷建立考点映射，再逐条讲解该生所有有效的非满分评分项，包括零分与部分得分。只交付该生该科的 PDF。

1. 盘点本场的总成绩与名次、小题分、试卷及答案或评分细则。按考试、科目和学生 ID 核对来源，区分零分、缺考、未选科与缺记录。没有 ID 时用班级和考号核对，姓名重名或匹配冲突时先核实。
2. 先读齐本次分析范围内的试卷，建立「小题分列 → 原题号 → 满分 → 题型 → 知识点或能力 → 可用评分依据」映射。数学公式、图表和扫描件的关键位置要看原页。按小题分的实际评分粒度标出合计计分，并列出各题考点。没有证据的题目标为待核实。映射按考试和科目复用，换班或换学生时沿用。
3. 用程序汇总分数、得分率、样本人数和可核对的名次。读 @references/data.md 获取统计口径及 `scripts/metrics.py` 的调用命令。以本场实考数据、同一份卷和同一分值为比较基础。考点来自试卷、答案和细则，作答错误来自答卷或批注。
4. 按 @references/reports.md 撰写。老师版的对应页标题是「讲评建议」，按这次答题情况选材料和说法。学生版给学生看，逐科列出可定位的失分题及考点，把练习顺序和动作统一放在最后「本场订正」。
5. 按 @references/reports.md 的命令运行 `scripts/render.py` 导出 A4 PDF。重新打开核对有效科目、样本、题号、得分及满分、中文、页序和裁切。仅把本次所需的 PDF 放入交付包。学生报告的内容限本人和汇总统计。分析中间文件留在当次任务目录。

## PDF 模板文件

以下路径从 `SKILL.md` 所在目录开始。`scripts/render.py` 按报告类型和学科读取相应的封面图，并应用 `templates/report.css`。

- 学生个人报告与汇总封面使用 `templates/student.jpg`。
- 语文使用 `templates/chinese.jpg`，数学使用 `templates/math.jpg`，英语使用 `templates/english.jpg`。
- 物理使用 `templates/physics.jpg`，化学使用 `templates/chemistry.jpg`，生物使用 `templates/biology.jpg`。
- 历史使用 `templates/history.jpg`，地理使用 `templates/geography.jpg`，思想政治使用 `templates/politics.jpg`。
