# 典型问题

## Q9：代码格式化问题 {#q9}

*来自群：高程[05-丁]  用户：2551521-微应物-姜浙誉  提问时间：2026-04-25 09:19:15 问题类别：technology*

::: info 问题状态：已关闭
:::

::: details
这是一个典型问题，因此在你提问之前，请确保浏览过这些问题.
:::

**问题描述**：

为什么我在vs里面配置了clang-format之后，在while(getchar()!='\n')后面打；，‘；’会自动换行？这是正常现象吗？

![图片](/root/git_project/Tongji-Useful-Tools/QQbot-for-High-Level-Language-Programming/website/pics/4D0911D5697B96ABE34FC1298CB90F51.png)

**追问追答**：

::: tip ***追答于：2026-04-24 16:24:34***
![图片](/root/git_project/Tongji-Useful-Tools/QQbot-for-High-Level-Language-Programming/website/pics/5483D09003BE979BDE74C143C46ECA36.png) 

1. 你可以把这里的空语句理解成 continue;
while (condition)
    [单语句] continue;
规定是要换行的；记得认真阅读一下之前的格式要求相关的文档
2. 看，配好 clang-format 的好处就在这儿，避免因失误丢分

:::

---

::: tip ***追答于：2026-04-24 16:28:31***
我想试试这个：
```
while (condition)
    [单语句] continue;
```

:::

---

## Q34：cfg乱码配置咨询 {#q34}

*来自群：高程[05-丁]  用户：2552084-经管-李光楷  提问时间：2026-05-06 09:44:23 问题类别：programming*

::: info 问题状态：已关闭
:::

::: details
这是一个典型问题，因此在你提问之前，请确保浏览过这些问题.
:::

**问题描述**：

请问.cfg文件双击打开以后出现如图所示的乱码是什么情况，以及图中三项信息应该如何配置，pdf文件规则没有读懂

![图片](/root/git_project/Tongji-Useful-Tools/QQbot-for-High-Level-Language-Programming/website/pics/2D6F76668F24C500E0BA258E36D9BBED.png)

**追问追答**：

::: tip ***追答于：2026-05-05 14:20:05***
1.如图，选择 gbk

![图片](/root/git_project/Tongji-Useful-Tools/QQbot-for-High-Level-Language-Programming/website/pics/7048679E8921A8AF91D5963AF65ABF69.png) 

2.VSCode 整不明白就别用了，右键记事本打开吧

:::

---

