"""
通知模块 - 支持青龙面板 Open API 通知 + Qmsg酱

优先级:
1. 青龙面板 Open API（PUT /open/system/notify）
2. Qmsg酱推送
3. 仅控制台输出

青龙通知配置（二选一）:
  方式A（推荐）: 设置 QL_CLIENT_ID 和 QL_CLIENT_SECRET 环境变量
    - 青龙面板 → 系统设置 → 应用管理 → 新建应用（权限勾选"系统管理"）
    - 将显示的 Client ID 填入 QL_CLIENT_ID，Client Secret 填入 QL_CLIENT_SECRET
  方式B: 直接设置 QL_NOTIFY_TOKEN（已通过 /open/auth/token 换取的 JWT）

注意: 本文件命名为 skland_notify.py 而非 notify.py，
     是为了避免与青龙面板自身的 /ql/scripts/notify.py 产生命名冲突。
"""

import logging
import os

logger = logging.getLogger("skland_notify")

_QL_API_BASE = os.environ.get("QL_API_BASE", "http://localhost:5600")


async def _get_ql_token(client_id: str, client_secret: str) -> str | None:
    """用 Client ID + Client Secret 换取 JWT Token"""
    try:
        import httpx
        url = f"{_QL_API_BASE}/open/auth/token"
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url, params={"client_id": client_id, "client_secret": client_secret})
            data = resp.json()
            if data.get("code") == 200:
                return data["data"]["token"]
            else:
                logger.warning(f"获取青龙 Token 失败: {data}")
                return None
    except Exception as e:
        logger.warning(f"获取青龙 Token 异常: {e}")
        return None


async def _send_ql_notify(title: str, content: str) -> bool:
    """调用青龙 Open API 发送通知，自动处理 Token 获取"""
    import httpx

    # 优先用已有 JWT Token，否则用 Client ID/Secret 换取
    token = os.environ.get("QL_NOTIFY_TOKEN", "")
    if not token:
        client_id = os.environ.get("QL_CLIENT_ID", "")
        client_secret = os.environ.get("QL_CLIENT_SECRET", "")
        if client_id and client_secret:
            token = await _get_ql_token(client_id, client_secret)
        
    if not token:
        return False

    try:
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

    # 1. 青龙面板 Open API
    has_ql_config = (
        os.environ.get("QL_NOTIFY_TOKEN")
        or (os.environ.get("QL_CLIENT_ID") and os.environ.get("QL_CLIENT_SECRET"))
    )
    if has_ql_config:
        sent = await _send_ql_notify(title, message)
    else:
        logger.debug("未配置青龙通知变量 (QL_CLIENT_ID/QL_CLIENT_SECRET 或 QL_NOTIFY_TOKEN)，跳过")

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


