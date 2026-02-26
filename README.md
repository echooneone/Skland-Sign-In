# Skland-Sign-In

森空岛自动签到脚本，支持《明日方舟》与《终末地》每日自动签到，适配青龙面板部署。

本项目基于 [kafuneri/Skland-Sign-In](https://github.com/kafuneri/Skland-Sign-In) 改造，增加了青龙面板环境变量配置与内置通知支持。非青龙面板部署请参考原项目文档。

---

## 青龙面板部署（测试版本 v2.19.2）

### 1. 添加订阅

在青龙面板「订阅管理」中新建订阅，各字段填写如下：

| 字段 | 填写内容 |
|------|----------|
| 名称 | 森空岛签到 |
| 类型 | 公开仓库 |
| 链接 | `https://github.com/echooneone/Skland-Sign-In.git` |
| 定时规则 | `5 4 * * *` |
| 白名单 | `main.py` |
| 依赖文件 | `skland_api\|qmsg\|skland_notify` |
| 仓库分支 | `main` |

**白名单与依赖文件的区别：**
- **白名单**：控制哪些文件会被创建为定时任务。填 `main.py` 后只有 `main.py` 会生成任务，否则仓库中每个 `.py` 文件都会创建一个任务。
- **依赖文件**：控制哪些文件作为库被一并复制到脚本目录供 `import` 使用。两者都需要填写。

**关于订阅的定时规则：**

订阅和任务是两套独立的定时机制：
- **订阅定时**：控制青龙何时从仓库拉取更新代码
- **任务定时**：控制何时执行签到脚本

任务创建时会复制订阅中填写的定时规则作为初始值，之后两者互不影响。

订阅运行后会自动创建签到任务，无需手动添加。如果不需要自动跟进脚本更新，可以在「订阅管理」中**禁用该订阅**，签到任务会照常每天执行。

### 2. 安装依赖

在青龙面板「依赖管理 - Python3」中添加：

```
httpx
pycryptodome
```

### 3. 添加环境变量

在青龙面板「环境变量」中添加：

| 变量名 | 必填 | 说明 |
|--------|------|------|
| `SKLAND_TOKEN` | 是 | 用户 Token，多账号用 `&` 分隔 |
| `SKLAND_NICKNAME` | 否 | 账号昵称，与 Token 顺序对应，用 `&` 分隔 |
| `QMSG_KEY` | 否 | Qmsg 酱推送 Key（可选备用推送渠道） |

多账号示例：
```
SKLAND_TOKEN=Token1&Token2
SKLAND_NICKNAME=大号&小号
```

### 4. 通知推送

脚本自动调用青龙内置 `QLAPI.systemNotify()`，无需任何额外配置，直接使用「系统设置 - 通知设置」中配置的推送渠道即可。

---

## 如何获取 Token

1. 登录 [森空岛官网](https://www.skland.com/)
2. 登录后访问：[https://web-api.skland.com/account/info/hg](https://web-api.skland.com/account/info/hg)
3. 页面返回 JSON 数据，复制 `content` 字段中的字符串
   - 示例：`{"code":0,"data":{"content":"复制这里的内容"}}`

> Token 等同于账号凭证，请勿泄露。
