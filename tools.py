import asyncio
import base64
import functools
from jinja2 import Environment, FileSystemLoader
from mistralai import Mistral
from pyppeteer import launch
import requests
import os
from dotenv import load_dotenv
from pprint import pprint
from typing import List, Dict, Any
from urllib.parse import urlparse
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
import time
from multiprocessing import Pool, cpu_count

load_dotenv()

api_key = os.environ["MISTRAL_API_KEY"]
client = Mistral(api_key=api_key)


def _encode_image(image_path: str) -> str:
    # Encode image to base64
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


MODELS = {
    "text": "mistral-large-latest",
    "image": "pixtral-12b-2409",
    "code": "codestral-mamba-latest",
}

brave_api_key = os.getenv("BRAVE_API_KEY")


class VisualTooling:

    def render_website(self, directory: str):
        pass


class SearchTooling:
    def __init__(self, prompt):
        self.prompt = prompt
        self.api_key = os.getenv("BRAVE_API_KEY")
        self.base_url = "https://api.search.brave.com/res/v1/web/search"
        self.image_search_url = "https://api.search.brave.com/res/v1/images/search"
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_web_information",
                    "description": "Search the web for information on a given query",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query.",
                            }
                        },
                        "required": ["query"],
                    },
                },
            },
        ]

        self.image_search_tool = [
            {
                "type": "function",
                "function": {
                    "name": "search_web_pictures",
                    "description": "Search for images on the web based on a query and save them with a specific filename",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query for images.",
                            },
                            "filename": {
                                "type": "string",
                                "description": "The filename to save the image as.",
                            },
                            "save_dir": {
                                "type": "string",
                                "description": "The directory to save the downloaded images. Defaults to 'images'.",
                            },
                        },
                        "required": ["query", "filename"],
                    },
                },
            },
        ]

        self.screenshot_tool = [
            {
                "type": "function",
                "function": {
                    "name": "screenshot_web",
                    "description": "Search the web and take screenshots of resulting websites",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query for websites.",
                            },
                            "save_dir": {
                                "type": "string",
                                "description": "The directory to save the screenshots. Defaults to 'screenshots'.",
                            },
                        },
                        "required": ["query"],
                    },
                },
            },
        ]

        self.function_names = {
            "search_web_information": self.search_web_information,
            "search_web_pictures": self.search_web_pictures,
            "screenshot_web": functools.partial(
                self.screenshot_web, save_dir="screenshots"
            ),
        }

    def search_web_information(self, query: str):  # search the web for information
        """
        Fetches search results from Brave Search API using Python with specific headers.

        Args:
        - api_key (str): Your Brave Search API key.
        - query (str): The search query.

        Returns:
        - dict: Search results as a dictionary.
        """

        # API endpoint
        url = self.base_url

        # Query parameters
        params = {
            "q": query,
            "count": 2,
            "result_filter": "web",
        }  # Number of results to return

        # Headers to match the curl request
        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": self.api_key,  # API Key passed here
        }

        # Make the GET request
        response = requests.get(url, headers=headers, params=params)

        # Check if the request was successful
        if response.status_code == 200:
            return response.json()  # Return the search results as a JSON dictionary
        else:
            # If the request fails, raise an error with the status and error message
            return f"Error: {response.status_code} - {response.text}"

    def filter_images(self, image_path: str, prompt: str) -> bool:
        return True
        template_dir = os.path.join(os.path.dirname(__file__), "prompts")
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template("filter_images_by_condition.xml.jinja")

        rendered_content = template.render(prompt=prompt)

        try:
            with open(image_path, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

            messages = [
                {
                    "role": "system",
                    "content": "You are an AI assistant skilled in image analysis.",
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": rendered_content},
                        {
                            "type": "image_url",
                            "image_url": f"data:image/png;base64,{encoded_image}",
                        },
                    ],
                },
            ]

            response = client.chat.complete(
                model=MODELS["image"], messages=messages, max_tokens=100
            )
            response_content = response.choices[0].message.content
            time.sleep(1)
            return "SUITABLE" in response_content.upper()
            # Sleep for 1 second
        except Exception as e:
            print(f"Error in filter_images: {e}")
            return False

    def search_web_pictures(self, query: str, filename: str, save_dir: str = "images") -> Dict[str, Any]:
        """
        Search for an image using the Brave API's image search endpoint and save it with the specified filename.

        Args:
        - query (str): The search query for images.
        - filename (str): The filename to save the image as.
        - save_dir (str): The directory to save the downloaded image. Defaults to 'images'.

        Returns:
        - Dict[str, Any]: A dictionary with the local file path of the saved image.
        """
        save_dir = os.path.join(os.getcwd(), save_dir.lstrip("/"))
        headers = {"Accept": "application/json", "X-Subscription-Token": self.api_key}
        params = {"q": query, "count": 1}  # We only need one result
        response = requests.get(self.image_search_url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])

            if results:
                image_url = results[0].get("image", {}).get("url")
                if image_url:
                    try:
                        image_response = requests.get(image_url)
                        if image_response.status_code == 200:
                            # Ensure the save directory exists
                            Path(save_dir).mkdir(parents=True, exist_ok=True)
                            
                            # Use the provided filename, but ensure it has an extension
                            file_extension = os.path.splitext(image_url)[1] or '.jpg'
                            safe_filename = f"{filename}{file_extension}"
                            file_path = os.path.join(save_dir, safe_filename)
                            
                            with open(file_path, "wb") as f:
                                f.write(image_response.content)
                            return {"local_path": file_path}
                    except Exception as e:
                        print(f"Error downloading image: {e}")

        print(f"Error: {response.status_code} - {response.text}")
        return {}

    def _capture_screenshot(self, url: str, save_dir: str) -> str:
        try:
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()), options=options
            )
            driver.set_window_size(1280, 800)
            driver.get(url)
            time.sleep(5)  # Wait for page to load

            url_filename = "".join(char for char in url if char.isalnum())[:50]
            screenshot_path = os.path.join(save_dir, f"screenshot_{url_filename}.png")
            driver.save_screenshot(screenshot_path)

            if self.filter_images(screenshot_path, self.prompt):
                return screenshot_path
            else:
                os.remove(screenshot_path)
                return None

        except Exception as e:
            print(f"Error capturing screenshot for {url}: {e}")
            return None
        finally:
            driver.quit()

    def screenshot_web(self, query: str, save_dir: str = "screenshots") -> List[str]:
        search_results = (
            self.search_web_information(query).get("web", {}).get("results", [])
        )
        urls = [result["url"] for result in search_results][
            :3
        ]  # Limit to first 3 results

        save_dir = os.path.join(os.getcwd(), save_dir)
        Path(save_dir).mkdir(parents=True, exist_ok=True)

        with Pool(processes=min(cpu_count(), len(urls))) as pool:
            screenshot_paths = pool.starmap(
                self._capture_screenshot, [(url, save_dir) for url in urls]
            )

        return [path for path in screenshot_paths if path]

    def extract_website_code(self, url: str):  # extract the code from a website
        pass


# Example usage with pretty printing
if __name__ == "__main__":
    query = "cool hackathon websites"
    search_tool = SearchTooling(brave_api_key)
    results = search_tool.search_web_information(query)
    pprint(results, indent=2, width=100)

    # Image search example
    image_results = search_tool.search_web_pictures(query, "/images")
    print("\nImage Search Results:")
    pprint(image_results, indent=2, width=100)

    # Screenshot example
    screenshot_results = search_tool.screenshot_web(query)
    print("\nScreenshot Results:")
    pprint(screenshot_results, indent=2, width=100)