"""
通知模块 - 支持青龙面板内置 QLAPI 通知 + Qmsg酱

优先级:
1. 青龙面板内置 QLAPI.systemNotify()（自动注入，无需任何配置）
2. Qmsg酱推送（设置环境变量 QMSG_KEY）
3. 仅控制台输出

注意: 本文件命名为 skland_notify.py 而非 notify.py，
     是为了避免与青龙面板自身的 /ql/scripts/notify.py 产生命名冲突。
"""

import logging
import os

logger = logging.getLogger("skland_notify")


async def send_notification(title: str, message: str, qmsg_key: str = ""):
    """
    发送通知

    :param title: 通知标题
    :param message: 通知内容
    :param qmsg_key: Qmsg酱 Key（可选，也可通过环境变量 QMSG_KEY 配置）
    """
    sent = False

    # 1. 青龙面板内置 QLAPI（运行时自动注入，使用系统通知设置，无需任何额外配置）
    try:
        result = QLAPI.systemNotify({"title": title, "content": message})  # noqa: F821
        if result and result.get("code") == 200:
            logger.info("青龙面板通知发送成功")
            sent = True
        else:
            logger.warning(f"青龙面板通知失败: {result}")
    except NameError:
        # 非青龙环境，QLAPI 不存在，属于正常情况
        logger.debug("非青龙环境，跳过 QLAPI 通知")
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



