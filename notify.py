"""
通知模块 - 支持青龙面板内置通知 + Qmsg酱

优先级:
1. 青龙面板内置 sendNotify（自动检测）
2. Qmsg酱推送
3. 仅控制台输出
"""

import logging
import os

logger = logging.getLogger("notify")

# 尝试导入青龙面板内置通知模块
_ql_notify = None
try:
    # 青龙面板会在 /ql/scripts/ 或 /ql/repo/ 下提供 sendNotify
    import sendNotify
    _ql_notify = sendNotify
    logger.info("检测到青龙面板通知模块")
except ImportError:
    pass


async def send_notification(title: str, message: str, qmsg_key: str = ""):
    """
    发送通知

    :param title: 通知标题
    :param message: 通知内容
    :param qmsg_key: Qmsg酱 Key（可选）
    """
    sent = False

    # 1. 尝试青龙面板内置通知
    if _ql_notify:
        try:
            # sendNotify.send 是同步函数
            _ql_notify.send(title, message)
            logger.info("青龙面板通知发送成功")
            sent = True
        except Exception as e:
            logger.warning(f"青龙面板通知发送失败: {e}")

    # 2. 尝试 Qmsg酱
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
