"""
通知模块 - 支持青龙面板内置通知 + Qmsg酱

优先级:
1. 青龙面板内置 send_notify（自动检测 /ql/scripts/notify.py）
2. Qmsg酱推送
3. 仅控制台输出

注意: 本文件命名为 skland_notify.py 而非 notify.py，
     是为了避免与青龙面板自身的 /ql/scripts/notify.py 产生命名冲突。
"""

import logging
import os

logger = logging.getLogger("skland_notify")


def _ql_cli_available() -> bool:
    """检测 ql notify CLI 命令是否可用（青龙 v2.17+）"""
    import shutil
    return shutil.which("ql") is not None


_QL_CLI = _ql_cli_available()
if _QL_CLI:
    logger.info("检测到青龙面板 ql CLI，将使用 `ql notify` 发送通知")


async def send_notification(title: str, message: str, qmsg_key: str = ""):
    """
    发送通知

    :param title: 通知标题
    :param message: 通知内容
    :param qmsg_key: Qmsg酱 Key（可选，也可通过环境变量 QMSG_KEY 配置）
    """
    sent = False

    # 1. 青龙面板 CLI：ql notify "title" "content"
    #    这是最可靠的方式，直接读取青龙数据库中的通知配置（v2.17+）
    if _QL_CLI:
        try:
            import subprocess
            result = subprocess.run(
                ["ql", "notify", title, message],
                capture_output=True,
                text=True,
                timeout=30,
            )
            stdout = result.stdout.strip()
            stderr = result.stderr.strip()
            logger.info(f"ql notify 输出: {stdout or '(无)'}")
            if stderr:
                logger.warning(f"ql notify stderr: {stderr}")
            if result.returncode == 0:
                logger.info("青龙面板通知发送成功")
                sent = True
            else:
                logger.warning(f"青龙面板通知发送失败 (exit {result.returncode})")
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
