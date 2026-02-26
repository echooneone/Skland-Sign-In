"""
通知模块 - 支持青龙面板内置通知 + Qmsg酱

优先级:
1. 青龙面板内置 send_notify（自动检测 /ql/scripts/notify.py）
2. Qmsg酱推送
3. 仅控制台输出

注意: 本文件命名为 skland_notify.py 而非 notify.py，
     是为了避免与青龙面板自身的 /ql/scripts/notify.py 产生命名冲突。
"""

import importlib
import logging
import os
import sys

logger = logging.getLogger("skland_notify")

# 青龙面板自身通知模块所在路径
_QL_NOTIFY_PATHS = [
    "/ql/scripts",
    "/ql/data/scripts",
]

_ql_send = None


def _try_import_ql_notify():
    """动态查找并导入青龙面板 notify.py 中的 send_notify 函数"""
    for path in _QL_NOTIFY_PATHS:
        notify_file = os.path.join(path, "notify.py")
        if not os.path.isfile(notify_file):
            continue

        if path not in sys.path:
            sys.path.insert(0, path)

        try:
            mod = importlib.import_module("notify")
            fn = getattr(mod, "send_notify", None)
            if callable(fn):
                logger.info(f"检测到青龙面板通知模块: {notify_file}")
                return fn
        except Exception as e:
            logger.debug(f"加载青龙通知模块失败 ({path}): {e}")
            if path in sys.path:
                sys.path.remove(path)

    return None


_ql_send = _try_import_ql_notify()
if not _ql_send:
    logger.debug("未检测到青龙面板通知模块，将尝试其他推送渠道")


async def send_notification(title: str, message: str, qmsg_key: str = ""):
    """
    发送通知

    :param title: 通知标题
    :param message: 通知内容
    :param qmsg_key: Qmsg酱 Key（可选，也可通过环境变量 QMSG_KEY 配置）
    """
    sent = False

    # 1. 青龙面板内置通知（send_notify 是同步函数）
    if _ql_send:
        try:
            _ql_send(title, message)
            logger.info("青龙面板通知发送成功")
            sent = True
        except Exception as e:
            logger.warning(f"青龙面板通知发送失败: {e}")

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
