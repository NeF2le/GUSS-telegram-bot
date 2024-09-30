from pprint import pprint

import requests
from src.logging_ import logger


class VkAPI:
    def __init__(self, token: str, version: str = '5.199'):
        """
        Initializes VkAPI instance with access token and API version.
        :param token: VK access token.
        :param version: VK API version. Default is '5.199'.
        """
        self.token = token
        self.version = version

    def check_vk_user(self, vk_url: str) -> bool:
        """
        Checks if a VK profile URL is valid and corresponds to a user.
        :param vk_url: VK profile URL.
        :return: True if the URL is valid and corresponds to a user, False otherwise.
        """
        screen_name = vk_url.split('/')[-1]
        params = {
            'access_token': self.token,
            'v': self.version,
            'screen_name': screen_name
        }

        try:
            response = requests.get("https://api.vk.com/method/utils.resolveScreenName", params=params)
            response.raise_for_status()

            data = response.json()
            return 'response' in data and data['response']['type'] == 'user'

        except requests.exceptions.RequestException as req_err:
            logger.error(f"Network error while checking user {vk_url}: {req_err}")
        except ValueError as json_err:
            logger.error(f"JSON parsing error while checking user {vk_url}: {json_err}")
        except Exception as err:
            logger.error(f"Unexpected error while checking user {vk_url}: {err}")

        return False

    def convert_vk_url_to_id(self, vk_url: str) -> int | None:
        """
        Converts VK profile URL to user ID.
        :param vk_url: VK profile URL.
        :return: User ID corresponding to the given VK profile URL.
        """
        screen_name = vk_url.split('/')[-1]
        if screen_name.isdigit():
            return int(screen_name)
        params = {
            'access_token': self.token,
            'v': self.version,
            'screen_name': screen_name
        }
        try:
            response = requests.get("https://api.vk.com/method/utils.resolveScreenName", params=params)
            response.raise_for_status()

            data = response.json()
            return data['response']['object_id'] if 'response' in data else None

        except requests.exceptions.RequestException as req_err:
            logger.error(f"Network error while converting URL {vk_url} to ID: {req_err}")
        except ValueError as json_err:
            logger.error(f"JSON parsing error while converting URL {vk_url} to ID: {json_err}")
        except Exception as err:
            logger.error(f"Unexpected error while converting URL {vk_url} to ID: {err}")

        return None

    def get_group_id(self, domain: str | int) -> int | None:
        """
        Gets group ID by domain.
        :param domain: VK group domain.
        :return: Group ID corresponding to the given domain.
        """
        params = {
            'access_token': self.token,
            'v': self.version,
            'group_id': domain
        }
        try:
            response = requests.get('https://api.vk.com/method/groups.getById', params=params)
            response.raise_for_status()

            data = response.json()
            return data['response']['groups'][0]['id'] if 'response' in data else None

        except requests.exceptions.RequestException as req_err:
            logger.error(f"Network error while getting group ID for {domain}: {req_err}")
        except ValueError as json_err:
            logger.error(f"JSON parsing error while getting group ID for {domain}: {json_err}")
        except Exception as err:
            logger.error(f"Unexpected error while getting group ID for {domain}: {err}")

        return None

    def get_group_screen_name(self, domain: str | int) -> str | None:
        """
        Gets group ID by domain.
        :param domain: VK group domain.
        :return: Group screen name corresponding to the given domain.
        """
        params = {
            'access_token': self.token,
            'v': self.version,
            'group_id': domain
        }
        try:
            response = requests.get('https://api.vk.com/method/groups.getById', params=params)
            response.raise_for_status()

            data = response.json()
            return data['response']['groups'][0]['screen_name'] if 'response' in data else None

        except requests.exceptions.RequestException as req_err:
            logger.error(f"Network error while getting group screen name for {domain}: {req_err}")
        except ValueError as json_err:
            logger.error(f"JSON parsing error while getting group screen name for {domain}: {json_err}")
        except Exception as err:
            logger.error(f"Unexpected error while getting group screen name for {domain}: {err}")

        return None

    def get_group_posts_ids(self, domain: str, count: int) -> list[int]:
        """
        Gets IDs of the latest posts in a group.
        :param domain: VK group domain.
        :param count: Number of posts ro retrieve. Default is 10.
        :return: List of post IDs.
        """
        params = {
            'access_token': self.token,
            'v': self.version,
            'domain': domain,
            'count': count
        }
        try:
            response = requests.get('https://api.vk.com/method/wall.get', params=params)
            response.raise_for_status()

            data = response.json()
            result = []
            for obj in data.get('response').get('items'):
                if obj.get('type') == 'post':
                    result.append(obj.get('id'))
            return result

        except requests.exceptions.RequestException as req_err:
            logger.error(f"Network error while getting posts for group {domain}: {req_err}")
        except ValueError as json_err:
            logger.error(f"JSON parsing error while getting posts for group {domain}: {json_err}")
        except Exception as err:
            logger.error(f"Unexpected error while getting posts for group {domain}: {err}")

        return []

    def get_post_liked_ids(self, owner_id: int, item_id: int) -> list[int]:
        """
        Gets IDs of users who liked a post.
        :param owner_id: Owner ID of the post.
        :param item_id: Post ID.
        :return: List of user IDs who liked the post.
        """
        params = {
            'access_token': self.token,
            'v': self.version,
            'type': 'post',
            'owner_id': owner_id,
            'item_id': item_id,
            'filter': 'likes'
        }
        try:
            response = requests.get('https://api.vk.com/method/likes.getList', params=params)
            response.raise_for_status()

            data = response.json()
            return data['response']['items'] if 'response' in data else []

        except requests.exceptions.RequestException as req_err:
            logger.error(f"Network error while getting likes for post {item_id}: {req_err}")
        except ValueError as json_err:
            logger.error(f"JSON parsing error while getting likes for post {item_id}: {json_err}")
        except Exception as err:
            logger.error(f"Unexpected error while getting likes for post {item_id}: {err}")

        return []

    def get_post_commented_ids(self, owner_id: int, post_id: int, comment_id: int | None = None) -> list[int]:
        """
        Gets IDs of users who commented a post.
        :param owner_id: Owner ID of the post.
        :param post_id: Post ID.
        :param comment_id: Comment ID to start retrieving comments from. Default is None.
        :return: List of user IDs who commented on the post.
        """
        params = {
            'access_token': self.token,
            'v': self.version,
            'owner_id': owner_id,
            'count': 100,
            'post_id': post_id,
            'comment_id': comment_id
        }
        try:
            response = requests.get('https://api.vk.com/method/wall.getComments', params=params)
            response.raise_for_status()

            data = response.json()
            commented_ids = []

            if 'response' in data:
                for post in data['response']['items']:
                    try:
                        if post['thread']['count'] == 1:
                            commented_ids.append(*self.get_post_commented_ids(owner_id, post_id, post['id']))
                        elif post['thread']['count'] > 1:
                            commented_ids.extend(self.get_post_commented_ids(owner_id, post_id, post['id']))
                        else:
                            commented_ids.append(post['from_id'])
                    except KeyError:
                        commented_ids.append(post['from_id'])
            return commented_ids

        except requests.exceptions.RequestException as req_err:
            logger.error(f"Network error while getting comments for post {post_id}: {req_err}")
        except ValueError as json_err:
            logger.error(f"JSON parsing error while getting comments for post {post_id}: {json_err}")
        except Exception as err:
            logger.error(f"Unexpected error while getting comments for post {post_id}: {err}")

        return []

    @staticmethod
    def get_post_url(owner_id: int, post_id: int) -> str:
        """
        Gets VK post URL.
        :param owner_id: Owner ID of the post.
        :param post_id: Post ID.
        :return: VK post URL.
        """
        return f"https://vk.com/wall{owner_id}_{post_id}"
