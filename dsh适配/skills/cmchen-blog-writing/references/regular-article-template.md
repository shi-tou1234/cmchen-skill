# 普通文章模板

> 普通文章类文章的完整模板，包含四种子类型的格式规范。

---

## 子类型一：随笔（category: 随笔）

适用于：个人经历、游记、情感记录、Q&A 自问自答、生活感悟。

```markdown
---
title: 文章标题
pubDate: 2026-06-03T12:00:00.000Z
updatedDate: 2026-06-03T12:00:00.000Z
draft: false
description: 
image: ./assets/封面图.jpg
category: 随笔
slugId: 文章标识
---

> 简短的情感导入或引子...

正文内容，自由分段。

![图片描述](./assets/图片.jpg)

可以有感触、有描写、有对话。

---

另一个段落...

:::quote
名人名言或自创引用。

<br><right>—— 作者</right>
:::
```

### Q&A 自问自答格式

```markdown
### Q1：如果完全没有限制，你心目中「最完美的一天」是什么样的？

**Q：** 完整的问题描述...

**A：** 回答内容...

---

### Q2：下一个问题？

**Q：** ...

**A：** ...
```

### 格式检查清单

- [ ] Frontmatter 完整
- [ ] `category: 随笔`
- [ ] 图片使用正确（`![alt](./assets/图片.jpg)`）
- [ ] 如需引用，使用 `:::quote`
- [ ] 语气口语化、有个人风格

---

## 子类型二：工具使用（category: 工具使用）

适用于：工具/网站推荐、软件教程、资源整理。

```markdown
---
title: 一些好用的网站和工具（一）
pubDate: 2026-02-17T09:57:00.000Z
updatedDate: 2026-02-17T09:57:00.000Z
draft: false
description: 
image: ./assets/无标题.png
category: 工具使用
slugId: 一些好用的网站和工具
---

* 1. [github](https://github.com/)，毫无疑问，非常好用的代码托管仓库，开源社区，里面有非常多的免费软件。网络不是很稳定，有时候需要梯子或者加速器。国内平替[gitee](https://gitee.com/)。

![无标题.png](./assets/无标题.png)

* 2.[朱雀ai检测助手](https://matrix.tencent.com/ai-detect/ai_gen_txt)，免费的ai查重网站

* 3.[CDSN](https://www.csdn.net/)，电子人的百科全书，但是这个网站的广告实在是太多了，建议转到知乎。

* 4.[git](https://git-scm.com/),非常好用的代码伴侣，可以远程拉取提交克隆代码，搭配github和trae十分好用。

:::tip[小提示]
推荐搭配加速器使用。
:::
```

### 格式检查清单

- [ ] Frontmatter 完整
- [ ] `category: 工具使用`
- [ ] 列表格式（`*` 无序列表）
- [ ] 图片展示工具截图
- [ ] 口语化、推荐语气

---

## 子类型三：创意写作（category: 写在这里）

适用于：故事、小说、日记、散文、创作实验。

```markdown
---
title: 1978的故事（一）
pubDate: 2026-06-26T08:11:00.000Z
updatedDate: 2026-06-26T08:11:00.000Z
draft: false
description: 
category: 写在这里
slugId: 1978的故事（一）
---

写于1978年

故事从春天开始…

:::quote
草在结它的种子，风在摇它的叶子。我们站着，不说话，就十分美好。

<br><right>—— 顾城《门前》</right>
:::

## 三月

##### 3月23日

今天第一次看到你发那条手链的照片...

:::quote
黑夜给了我黑色的眼睛，我却用它寻找光明。

<br><right>—— 顾城</right>
:::

你就是我在这黑夜里，不小心寻找到的一束光。

##### 3月30日

十一点半，问你睡了吗，你说刚下课。

正文继续...
```

### 日期标题格式

```markdown
## 月份

##### 日期

正文...

:::quote
引用。

<br><right>—— 作者</right>
:::

##### 下一个日期

正文...
```

### 格式检查清单

- [ ] Frontmatter 完整
- [ ] `category: 写在这里`
- [ ] 日期标题使用 `#####`
- [ ] `:::quote` 用于文学引用
- [ ] 语气文学性、叙事性

---

## 子类型四：开发记录（category: 自定义）

适用于：项目开发过程、技术博客、网站搭建记录。

```markdown
---
title: 网站开发记录
pubDate: 2026-02-18T10:00:00.000Z
updatedDate: 2026-02-18T10:00:00.000Z
draft: false
description: 
image: ./assets/开发截图.png
category: 开发记录
slugId: 网站开发记录
---

## 第一阶段：需求分析和设计

项目背景...

```bash
npm create astro@latest
```

:::tip
这是一个开发小技巧。
:::

## 第二阶段：核心功能实现

...

```javascript
// 核心代码
function init() {
  console.log('initialized');
}
```

:::note[注意事项]
部署时需要注意...
:::
```

### 格式检查清单

- [ ] Frontmatter 完整
- [ ] category 自定义（如 `开发记录`）
- [ ] 代码块使用正确
- [ ] 图片展示界面截图
- [ ] 语气技术性、记录性

---

## 普通文章通用检查清单

- [ ] Frontmatter 完整
- [ ] category 正确
- [ ] 如需图片，使用 `![alt](./assets/图片.jpg)`
- [ ] 如需引用，使用 `:::quote`
- [ ] 如需列表，使用 `*` 或 `-` 无序列表
- [ ] 如需代码块，使用 ` ```lang ` 语法
- [ ] 如需提示，使用 `:::note/tip/important/warning/caution`
