from telegraph.aio import Telegraph


class TelegraphAPI:
    def __init__(self):
        self.telegraph = Telegraph()

    async def create_account(self):
        await self.telegraph.create_account(short_name="GUSS35")

    async def create_page(self, title: str, html_content: str, author_name: str = 'ГУСС',
                          author_url: str = 'https://vk.com/guss35') -> str:
        await self.create_account()
        response = await self.telegraph.create_page(title=title, html_content=html_content, author_name=author_name,
                                                    author_url=author_url)

        return response['url']
