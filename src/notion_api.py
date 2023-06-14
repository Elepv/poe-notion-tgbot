import config
import asyncio

from notion_client import AsyncClient
from notion_client.errors import APIErrorCode

import utils

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# database_id = "f05180116fa54b009643148abc23ed97"
# notion_token = config.notion_token
# notion_page_id = ""

class NotionClient:

    # def __init__(self, notion_token, database_id) -> None:
    def __init__(self) -> None:
        notion_token = config.notion_token
        database_id = "f05180116fa54b009643148abc23ed97"
        cris_user_id = "28236a9a-da36-4486-8a7f-535350791102"
        suuu_user_id = "3404ad57-e612-4391-ad36-0f0a6681d660"

        self.client = AsyncClient(auth=notion_token)
        self.database_id = database_id
        self.cris_user_id = cris_user_id
        self.suuu_user_id = suuu_user_id

    
    # 新建数据库条目
    async def write_row(self, speak_time, abstract=None, topic=None, user_name=None, file_unique_id=None, block_title_h2=None, block_content=None):
        
        # response_data = await self.client.pages.create(
        #     **{
        #         "parent": {
        #             "database_id": database_id
        #         },
        #         "properties": {
        #             "Abstract": {"title": [{"text": {"content": abstract}}]},
        #             "Topic": {"rich_text": [{"text": {"content": topic}}]},
        #             "Speaker": {"people": [{"id": user_id}]},
        #             "Speak_Time": {"date": {"start": speak_time}}
        #             "file_unique_id": {"rich_text": [{"text": {"content": file_unique_id}}]},
        #         }
        #     }
        # )

        logging.info("write_row is running")

        # cris = "Lynn Tee"
        tg_username_cris = "courage2continue"
        # suuu = "刘大"
        tg_username_suuu = ""
        if user_name is None or user_name in tg_username_cris:
            # user_id = self.bot_user_id
            user_id = self.cris_user_id 
        elif user_name in tg_username_suuu:
            user_id = self.suuu_user_id
        
        properties = {
            "Speak_Time": {"date": {"start": speak_time}},
            "Abstract": {"title": [{"text": {"content": abstract}}]} if abstract else {},
            "Topic": {"rich_text": [{"text": {"content": topic}}]} if topic else {},
            "Speaker": {"people": [{"id": user_id}]} if user_id else {},
            "file_unique_id": {"rich_text": [{"text": {"content": file_unique_id}}]} if file_unique_id else {},
        }

        response_data = await self.client.pages.create(
            **{
                "parent": {
                    "database_id": self.database_id
                },
                "properties": {k:v for k,v in properties.items() if v}
            }
        )

        if block_title_h2:
            logging.info("write_to_block is running")

            await self.client.blocks.children.append(
                block_id = response_data['id'],
                children = [
                    {
                        "object": "block",
                        "type": "heading_2",
                        "heading_2": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": block_title_h2
                                    },
                                    "annotations": {
                                        "color": "green"
                                    }
                                }
                            ]
                        }
                    }
                ] 
            )

        if block_content:
            await self.client.blocks.children.append(
                block_id = response_data['id'],
                children = [
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": block_content
                                    }
                                }
                            ]
                        }
                    }
                ] 
            )
        

        return response_data

    # 加入文本块
    async def write_text_block(self, page_id, text_block):
        await self.client.blocks.children.append(
            block_id = page_id,
            children = [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": text_block
                                }
                            }
                        ]
                    }
                }
            ]
        )

    async def search_database(self, file_unique_id):

        # try:
            # Search for records with matching Name and Date properties
            results = self.client.databases.query(
                database_id=self.database_id,
                filter={
                    "and": [
                        {
                            "property": "file_unique_id",
                            "title": {
                                "equals": file_unique_id
                            }
                        },
                        # {
                        #     "property": "Date",
                        #     "date": {
                        #         "equals": datetime.now().strftime("%Y-%m-%d")
                        #     }
                        # }
                    ]
                }
            )

            return results

        # except APIErrorCode as e:
        #     error_text = f"在完成的过程中出了点问题。 Reason: {e}"
        #     logger.error(error_text)


async def test():
    client = NotionClient()

    abstract = "abstract test3"
    topic = "topic test 3"
    speak_time = utils.get_time_now()
    user_id = "28236a9a-da36-4486-8a7f-535350791102"  # Crie Elep

    response_data = await client.write_row(speak_time=speak_time, abstract=abstract, user_id=user_id)

    added_db_id = response_data['id']

    await client.write_text_block(page_id=added_db_id, text_block="hellow world!")

if __name__ == '__main__':
    # 测试用例
    asyncio.run(test())