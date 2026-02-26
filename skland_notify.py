"""
通知模块 - 支持青龙面板 Open API 通知 + Qmsg酱

优先级:
1. 青龙面板 Open API（PUT /open/system/notify），需配置 QL_NOTIFY_TOKEN
2. Qmsg酱推送
3. 仅控制台输出

注意: 本文件命名为 skland_notify.py 而非 notify.py，
     是为了避免与青龙面板自身的 /ql/scripts/notify.py 产生命名冲突。

青龙 Token 获取方式:
  青龙面板 → 系统设置 → 应用管理 → 新建应用 → 复制生成的 Token
  将 Token 添加为青龙环境变量 QL_NOTIFY_TOKEN
"""

import logging
import os

logger = logging.getLogger("skland_notify")

# 青龙 Open API 地址（容器内固定为 localhost:5600）
_QL_API_BASE = os.environ.get("QL_API_BASE", "http://localhost:5600")


async def _send_ql_notify(title: str, content: str, token: str) -> bool:
    """调用青龙 Open API 发送通知"""
    try:
        import httpx
        url = f"{_QL_API_BASE}/open/system/notify"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.put(url, headers=headers, json={"title": title, "content": content})
            data = resp.json()
            if data.get("code") == 200:
                logger.info("青龙面板通知发送成功")
                return True
            else:
                logger.warning(f"青龙面板通知失败: {data}")
                return False
    except Exception as e:
        logger.warning(f"青龙面板通知发送失败: {e}")
        return False


async def send_notification(title: str, message: str, qmsg_key: str = ""):
    """
    发送通知

    :param title: 通知标题
    :param message: 通知内容
    :param qmsg_key: Qmsg酱 Key（可选，也可通过环境变量 QMSG_KEY 配置）
    """
    sent = False

    # 1. 青龙面板 Open API（需要 QL_NOTIFY_TOKEN 环境变量）
    ql_token = os.environ.get("QL_NOTIFY_TOKEN", "")
    if ql_token:
        sent = await _send_ql_notify(title, message, ql_token)
    else:
        logger.debug("未配置 QL_NOTIFY_TOKEN，跳过青龙面板通知")

    # 2. Qmsg酱
    qmsg_key = qmsg_key or os.environ.get("QMSG_KEY", "")
    if qmsg_key:
        from qmsg import QmsgNotifier
        notifier = QmsgNotifier(qmsg_key)
        try:
            result = await notifier.send(message)
            if result:
                sent = True
        except Exception as e:
            logger.warning(f"Qmsg推送失败: {e}")

    if not sent:
        logger.info("未配置推送渠道，仅输出到控制台")

    return sent

