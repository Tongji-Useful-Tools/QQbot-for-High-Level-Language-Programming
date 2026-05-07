# 技术类问题

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

## Q15：自定义零判断函数 {#q15}

*来自群：高程[05-丁]  用户：2550299-电信-张瑞祥  提问时间：2026-04-25 17:13:26 问题类别：technology*

::: info 问题状态：已关闭
:::

**问题描述**：

![图片](/root/git_project/Tongji-Useful-Tools/QQbot-for-High-Level-Language-Programming/website/pics/9B2BCBE7FD7B8E234B0470202815207A.png) 

判断某一个数字是否等于0，能否能自行编写相应功能的函数按需调用，而不使用演示代码？

**追问追答**：

::: tip ***追答于：2026-04-25 16:45:52***
可以

:::

---

## Q17：main函数递归调用 {#q17}

*来自群：高程[05-丁]  用户：2552661-汽车-王子豪  提问时间：2026-04-25 23:47:18 问题类别：technology*

::: info 问题状态：已关闭
:::

**问题描述**：

我可以在main函数中调用main函数吗？

**追问追答**：

::: tip ***追答于：2026-04-25 22:24:57***
不可以，这是未定义行为

:::

---

***追问于：2026-04-25 22:36:38***

那4-b18和4-b19对main函数的功能是不是没什么特定要求？还有我可以定义除了要求的三个重载函数以外的我需要的函数吗？

::: tip ***追答于：2026-04-25 22:40:59***
是，可以

:::

---

## Q20：cin.ignore用法 {#q20}

*来自群：高程[05-丁]  用户：2551541-汽车-侯韩煜  提问时间：2026-04-29 19:24:02 问题类别：technology*

::: info 问题状态：已关闭
:::

**问题描述**：

cin.ignore(numeric_limits&lt;streamsize>::max(), '\n');

**追问追答**：

***追问于：2026-04-29 18:15:29***

cin.ignore(numeric_limits&lt;streamsize>::max(), '\n');
非法吗？

::: tip ***追答于：2026-04-29 18:39:21***
在题目没有特殊要求下，合法

:::

---

::: tip ***追答于：2026-05-04 19:45:44***
不用

:::

---

## Q35：格式化后{}光标下移 {#q35}

*来自群：高程[05-丁]  用户：2552246-图灵-董杰  提问时间：2026-05-05 22:44:16 问题类别：technology*

::: info 问题状态：已关闭
:::

**问题描述**：

为什么启用clang-format后{}换行的光标位置会从中间变成下面

![图片](/root/git_project/Tongji-Useful-Tools/QQbot-for-High-Level-Language-Programming/website/pics/CCA5B485F83F5859148EFC12C4845E26.png) 

![图片](/root/git_project/Tongji-Useful-Tools/QQbot-for-High-Level-Language-Programming/website/pics/E1972BFBE13316FB1056D55E119080F6.png) 

，

![图片](/root/git_project/Tongji-Useful-Tools/QQbot-for-High-Level-Language-Programming/website/pics/A2723DE485C3637BFE63C5D05B513F23.png) 

更改相关设置似乎不能解决

**追问追答**：

::: tip ***追答于：2026-05-05 21:41:53***
因为在有启用clang-format的情况下打出左大括号会自动换行并打出右大括号，这时候你再按回车就是第二张图。如果没有启用clang-format就少了这个换行，你回车之后就是第一张图。

:::

---

***追问于：2026-05-05 21:46:50***

如何设置输入{}时不自动格式化呢

::: tip ***追答于：2026-05-05 21:58:09***
暂时没找到设置入口，可以适应一下新的工具逻辑——少按个回车，或者直接就在光标位置写完一行之后按Ctrl+S让它自然保存+格式化；如果实在用不惯，可以把有关配置关掉，写完代码后手动调用工具格式化

:::

---

