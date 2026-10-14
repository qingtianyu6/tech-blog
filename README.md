# 技术札记

简洁中文技术博客，支持文章搜索、分类筛选、归档、文章目录、代码复制和深色模式。使用 Markdown 写作，GitHub Actions 自动构建并部署到 GitHub Pages。

## 写文章（无需在电脑上安装工具）

1. 在 GitHub 打开本仓库的 `content` 文件夹。
2. 点击 **Add file → Create new file**，输入英文文件名，例如 `my-first-note.md`。
3. 按照下面格式写作，点击 **Commit changes** 提交到 `main` 分支。
4. 等待 **Actions** 中的发布任务变绿，再刷新博客。

```markdown
---
title: 我的第一篇笔记
date: 2026-10-14
category: 学习笔记
tags: 编程, 学习
summary: 一句话介绍文章内容。
---

## 正文标题

从这里开始写文章。
```

文件名仅使用小写英文字母、数字和连字符。日期格式为 `YYYY-MM-DD`。分类和标签会自动显示。两篇初始文章为示例，可以直接编辑或删除；自己的文章不需要填写“示例文章”标签。

## 修改个人信息

- 编辑 `site.json`：博客名称、作者、简介、GitHub 链接和站点地址。
- 编辑 `scripts/build.py` 中的 `about`：关于我页面。
- 编辑 `assets/style.css`：配色、字体和布局。
- 首页介绍文字与侧栏介绍位于 `scripts/build.py` 的 `hero` 与 `sidebar`。

## 本地预览

需要 Python 3.11 或更新版本。在仓库目录打开终端：

```powershell
python -m pip install -r requirements.txt
python scripts/build.py
python -m http.server 8000 --directory dist
```

在浏览器访问 `http://localhost:8000`。修改文章后重新运行构建脚本，再刷新页面。

## 部署

在仓库 **Settings → Pages → Build and deployment → Source** 选择 **GitHub Actions**。以后推送到 `main` 会自动更新。

初始地址：https://qingtianyu6.github.io/tech-blog/

源码在仓库中，`dist/` 是自动生成的页面，不要直接修改它。代码复制功能需要浏览器的剪贴板权限，在 HTTPS 或 localhost 中可用。
