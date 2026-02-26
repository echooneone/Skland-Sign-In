# Skland-Sign-In

森空岛自动签到脚本，用于实现森空岛平台下《明日方舟》与《终末地》的每日自动签到。  
支持多账号管理、青龙面板一键部署、Qmsg酱消息推送。

## 部署方式

### 方式一：青龙面板部署（推荐）

#### 1. 拉取仓库

在青龙面板「订阅管理」中添加订阅，各字段填写如下：

| 字段 | 填写内容 |
|------|----------|
| 名称 | 森空岛签到 |
| 类型 | 公开仓库 |
| 链接 | `https://github.com/echooneone/Skland-Sign-In.git` |
| 定时规则 | `2 10 * * *` |
| 白名单 | `main\.py` |
| 黑名单 | *(留空)* |
| 依赖文件 | `skland_api\|qmsg\|skland_notify` |
| 仓库分支 | `main` |

> ⚠️ **必须正确填写「白名单」和「依赖文件」**，否则青龙面板会对仓库中 **每个 `.py` 文件** 都创建定时任务。  
> - 白名单限定只有 `main.py` 作为任务入口  
> - 依赖文件让 `skland_api.py` / `qmsg.py` / `skland_notify.py` 作为库文件被引用，而不是独立任务



#### 2. 安装依赖

在青龙面板「依赖管理」中添加 **Python3** 依赖：

```
httpx
pycryptodome
```

> `pyyaml` 在使用环境变量配置时不需要安装。

#### 3. 添加环境变量

在青龙面板「环境变量」中添加：

| 变量名 | 必填 | 说明 |
|--------|------|------|
| `SKLAND_TOKEN` | ✅ | 用户Token，多账号用 `&` 分隔 |
| `SKLAND_NICKNAME` | ❌ | 用户昵称，与Token顺序对应，用 `&` 分隔 |
| `QMSG_KEY` | ❌ | Qmsg酱推送Key |
| `LOG_LEVEL` | ❌ | 日志等级：`debug` / `info`（默认 `info`） |

**环境变量示例：**

```
# 单账号
SKLAND_TOKEN=你的Token字符串

# 多账号（用 & 分隔）
SKLAND_TOKEN=Token1&Token2&Token3
SKLAND_NICKNAME=大号&小号&仓鼠号
```

#### 4. 添加定时任务

在青龙面板「定时任务」中添加：

```
名称：森空岛签到
命令：task main.py
定时规则：2 10 * * *
```

#### 5. 通知推送

脚本自动适配青龙面板内置通知系统。如果你在青龙面板中配置了推送渠道（如 Server酱、Bark、Telegram 等），签到结果会自动推送。  
同时也支持 Qmsg酱 作为额外推送渠道。

---

### 方式二：本地 / 服务器部署

#### 环境要求

* Python 3.8 或更高版本

#### 安装步骤

1. 克隆或下载本项目到本地。
```bash
git clone https://github.com/kafuneri/Skland-Sign-In.git && cd Skland-Sign-In
```
2. 在项目根目录下，安装所需依赖：

```bash
pip install -r requirements.txt
```

#### 配置方式

**方式 A：使用环境变量（推荐）**

```bash
# Linux / macOS
export SKLAND_TOKEN="你的Token"
export QMSG_KEY="你的QmsgKey"    # 可选
python3 main.py

# Windows
set SKLAND_TOKEN=你的Token
set QMSG_KEY=你的QmsgKey
python main.py
```

**方式 B：使用配置文件**

将 `config.example.yaml` 复制为 `config.yaml` 并编辑：
```bash
cp config.example.yaml config.yaml
```

> 环境变量优先级高于配置文件。当设置了 `SKLAND_TOKEN` 环境变量时，`config.yaml` 会被忽略。

#### 定时执行

配合 cron（Linux）或计划任务（Windows）实现每日自动运行：

```bash
# crontab 示例：每天 10:02 执行
2 10 * * * cd /path/to/Skland-Sign-In && python3 main.py
```

---

## 如何获取 Token

1. 登录 [森空岛官网](https://www.skland.com/)。
2. 登录成功后，访问此链接：[https://web-api.skland.com/account/info/hg](https://web-api.skland.com/account/info/hg)
3. 页面将返回一段 JSON 数据。请复制 `content` 字段中的长字符串。
   * 数据示例：`{"code":0,"data":{"content":"请复制这一长串字符"}}`
4. 将复制的字符串作为 Token 使用。

> ⚠️ Token 等同于账号凭证，请勿泄露给他人。

## 配置消息推送（可选）

### Qmsg酱

1. 注册并登录 [Qmsg酱](https://qmsg.zendee.cn/)。
2. 在管理台获取你的 KEY。
3. 设置环境变量 `QMSG_KEY` 或填入 `config.yaml` 的 `qmsg_key` 字段。

### 青龙面板内置通知

在青龙面板「系统设置 → 通知设置」中配置推送渠道即可，脚本会自动调用。
