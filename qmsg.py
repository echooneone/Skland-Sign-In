# qmsg.py
import httpx
import logging

logger = logging.getLogger("Qmsg")

class QmsgNotifier:
    def __init__(self, key: str):
        self.key = key
        self.base_url = "https://qmsg.zendee.cn"

    async def send(self, message: str) -> bool:
        """
        发送 Qmsg 推送
        :param message: 推送内容
        :return: 是否成功
        """
        if not self.key:
            logger.warning("未配置 Qmsg Key，跳过推送")
            return False

        # 使用 send 接口 (私聊)，如果你想推送到群，请改用 group 接口
        url = f"{self.base_url}/send/{self.key}"
        
        try:
            async with httpx.AsyncClient() as client:
                # 使用 data 字典发送表单数据，避免 URL 编码过长问题
                resp = await client.post(url, data={"msg": message})
                result = resp.json()
                
                if result.get("success"):
                    logger.info("Qmsg 推送成功")
                    return True
                else:
                    logger.error(f"Qmsg 推送失败: {result.get('reason')}")
                    return False
        except Exception as e:
            logger.error(f"Qmsg 请求发生错误: {e}")
            return False