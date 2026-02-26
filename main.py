#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
森空岛自动签到脚本 - 支持青龙面板 / 本地部署

环境变量配置（青龙面板推荐）:
    SKLAND_TOKEN   - 用户Token，多账号用 & 或换行分隔
    SKLAND_NICKNAME - 用户昵称（可选），与Token顺序对应，用 & 分隔
    QMSG_KEY       - Qmsg酱推送Key（可选）
    LOG_LEVEL      - 日志等级: debug / info（默认 info）

也兼容 config.yaml 配置文件，环境变量优先级更高。
"""

import asyncio
import os
import logging
from skland_api import SklandAPI
from skland_notify import send_notification

# 初始化基础日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SklandSign")


def load_config_from_env():
    """从环境变量加载配置（青龙面板标准方式）"""
    token_str = os.environ.get("SKLAND_TOKEN", "").strip()
    if not token_str:
        return None

    # 支持 & 或换行分隔多个Token
    tokens = [t.strip() for t in token_str.replace("&", "\n").split("\n") if t.strip()]

    nickname_str = os.environ.get("SKLAND_NICKNAME", "").strip()
    nicknames = [n.strip() for n in nickname_str.replace("&", "\n").split("\n") if n.strip()] if nickname_str else []

    users = []
    for i, token in enumerate(tokens):
        nickname = nicknames[i] if i < len(nicknames) else f"账号{i + 1}"
        users.append({"nickname": nickname, "token": token})

    config = {
        "users": users,
        "qmsg_key": os.environ.get("QMSG_KEY", ""),
        "log_level": os.environ.get("LOG_LEVEL", "info"),
    }

    logger.info(f"从环境变量加载配置，共 {len(users)} 个账号")
    # 启动时打印读取到的账号信息，方便排查环境变量是否配置正确
    for i, u in enumerate(users, 1):
        token_preview = u['token'][:6] + "..." if u['token'] else "(空)"
        logger.info(f"  账号{i}: 昵称={u['nickname']}, Token={token_preview}")
    return config


def load_config_from_file():
    """从 config.yaml 文件加载配置（向后兼容）"""
    try:
        import yaml
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        logger.info("从 config.yaml 加载配置")
        return config
    except FileNotFoundError:
        return None
    except ImportError:
        logger.warning("未安装 pyyaml，无法读取 config.yaml")
        return None


def load_config():
    """加载配置，环境变量优先"""
    config = load_config_from_env()
    if config:
        return config

    config = load_config_from_file()
    if config:
        return config

    logger.error(
        "未找到任何配置！请设置环境变量 SKLAND_TOKEN 或创建 config.yaml 文件。\n"
        "青龙面板: 在环境变量中添加 SKLAND_TOKEN\n"
        "本地部署: 复制 config.example.yaml 为 config.yaml"
    )
    return None


async def run_sign_in():
    # 1. 加载配置
    config = load_config()
    if not config:
        return

    # 2. 日志等级控制
    user_log_level = config.get("log_level", "info").lower()
    log_level = logging.DEBUG if user_log_level == "debug" else logging.WARNING
    for lib in ["httpx", "httpcore", "skland_api", "Qmsg"]:
        logging.getLogger(lib).setLevel(log_level)

    users = config.get("users", [])
    qmsg_key = config.get("qmsg_key", "")

    if not users:
        logger.warning("配置中没有发现用户信息")
        return

    api = SklandAPI(max_retries=3)

    # 3. 准备消息头部
    notify_lines = ["森空岛签到报告", ""]

    logger.info(f"开始执行签到任务，共 {len(users)} 个账号")

    for index, user in enumerate(users, 1):
        nickname_cfg = user.get("nickname", f"账号{index}")
        token = user.get("token", "")

        user_header = f"[{index}] {nickname_cfg}"
        notify_lines.append(user_header)
        logger.info(f"正在处理: {nickname_cfg}")

        if not token:
            logger.error(f"  [{nickname_cfg}] 未配置 Token")
            notify_lines.append("  错误: 缺少Token")
            notify_lines.append("")
            continue

        try:
            results, official_nickname = await api.do_full_sign_in(token)

            if not results:
                notify_lines.append("  未找到绑定角色")
                logger.warning(f"  [{nickname_cfg}] 未找到角色")

            for r in results:
                is_signed_already = not r.success and any(
                    k in r.error for k in ["已签到", "重复", "already"]
                )

                if r.success:
                    status_text = "成功"
                    detail = f" ({', '.join(r.awards)})" if r.awards else ""
                elif is_signed_already:
                    status_text = "已签"
                    detail = ""
                else:
                    status_text = "失败"
                    detail = f" ({r.error})"

                line = f"  {r.game}: {status_text}{detail}"
                notify_lines.append(line)
                logger.info(f"  - {line.strip()}")

        except Exception as e:
            error_msg = str(e)
            logger.error(f"  [{nickname_cfg}] 异常: {error_msg}")
            notify_lines.append(f"  错误: {error_msg}")

        notify_lines.append("")

    await api.close()

    # 4. 发送推送（自动适配青龙面板通知 / Qmsg酱）
    while notify_lines and notify_lines[-1] == "":
        notify_lines.pop()

    final_message = "\n".join(notify_lines)

    # 打印完整结果到控制台（青龙面板会捕获标准输出作为日志）
    print("\n" + "=" * 40)
    print(final_message)
    print("=" * 40 + "\n")

    await send_notification("森空岛签到", final_message, qmsg_key)

    logger.info("所有任务已完成")


if __name__ == "__main__":
    asyncio.run(run_sign_in())