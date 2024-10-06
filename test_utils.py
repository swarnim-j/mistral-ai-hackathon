from mistralai import Mistral
from mistralai.models.sdkerror import SDKError
import os
import sys
import base64
import re 
import json
from typing import List, Dict
import traceback

api_key = os.getenv("MISTRAL_API_KEY")
client = Mistral(api_key=api_key)

MODELS = {
    "text": "mistral-large-latest",
    "image": "pixtral-12b-2409",
    "code": "codestral-mamba-latest",
}

def init_mistral_client():
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError("MISTRAL_API_KEY environment variable is not set")
    return Mistral(api_key=api_key)

def generate_event_details(user_input: str) -> str:
    client = init_mistral_client()
    
    prompt = f"""
    You are an AI assistant helping to create a website for an event based on a user's input. The input might be vague or minimal. Your task is to expand on this input and provide rich context for website generation.

    Given the user input: "{user_input}"

    1. Interpret the core idea of the event.
    2. Imagine and describe key aspects that would be relevant for creating a website.
    3. Suggest a theme, style, or mood that would suit this event.
    4. If any specific details are mentioned (like date, location, etc.), include them. If not, do not mention them, or add TBD.
    5. If no specific design details are given, feel free to creatively fill in gaps that would help in website design.

    Provide your response as a concise paragraph or two, focusing on elements that would inspire and guide the creation of a spectacular, modern website. Your output will be used directly in further prompts for website generation, so make it rich and descriptive.
    """

    messages = [
        {"role": "system", "content": "You are a creative event planner and web designer, skilled at interpreting client needs and expanding on minimal information."},
        {"role": "user", "content": prompt}
    ]

    try:
        response = client.chat.complete(
            model=MODELS["text"],
            messages=messages
        )
        return response.choices[0].message.content
    except SDKError as e:
        raise RuntimeError(f"Mistral API error: {str(e)}")

def _list_file_names(directory: str) -> List[str]:
    return os.listdir(directory)

def _encode_image(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def generate_website_theme(event_details: str, image_dir: str = "./images", html_structure: List[str] = ["index.html","contact.html","register.html","about.html"]) -> Dict[str, str]:
    reference_images = _list_file_names(image_dir)[:7]
    image_paths = [f"{image_dir}/{image_name}" for image_name in reference_images]
    images = [{"type": "image_url", "image_url": f"data:image/jpeg;base64,{_encode_image(path)}"} for path in image_paths]

    messages = [
        {
            "role": "system",
            "content": "You are an exceptionally skilled web designer. Create a modern, spectacular website theme based on requirements and loosely based on the provided images."
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"""Generate a website theme based on these images and the following requirements: {event_details}

                    Please provide:
                    1. A CSS file with very modern, responsive design and cool web design features
                    2. A basic HTML structure for the home page as well as a navbar which links to all of the other pages in {html_structure}
                    3. DO not add ```css or ```html, format only as below

                    Ensure that the navbar actually links to the other pages, i.e. it has page_name.html as its href.
                    Use relative paths for all links (e.g., './page_name.html').
                    Ensure spectacular and modern design using latest web technologies and trends.

                    Format your response as follows:

                    [CSS]
                    (Your CSS code here)
                    [/CSS]

                    [HTML]
                    (Your HTML structure here)
                    [/HTML]
                    """
                },
                *images
            ]
        }
    ]

    response = client.chat.complete(
        model=MODELS["image"],
        messages=messages
    )
    response_content = response.choices[0].message.content

    response_content = response.choices[0].message.content.replace("```html","").replace("```","").replace("```css","")

    # Extract CSS and HTML
    css = re.search(r'\[CSS\](.*?)\[/CSS\]', response_content, re.DOTALL)
    html = re.search(r'\[HTML\](.*?)\[/HTML\]', response_content, re.DOTALL)
    
    css = css.group(1).strip() if css else ""
    html = html.group(1).strip() if html else ""
    
    return {
        "css": css,
        "html": html,
    }

def generate_pages(website_theme: Dict[str, str], event_details: str, asset_images: List[str], html_structure: List[str] = ["index.html","contact.html","register.html","about.html"]) -> List[Dict[str, str]]:
    pages = []
    for page in html_structure:
        content = generate_page_content(website_theme, page, event_details, asset_images)
        pages.append({"name": page, "content": content})
    return pages

def generate_page_content(website_theme: Dict[str, str], page: str, event_details: str, asset_images: List[str]) -> str:
    prompt = f"""
    Create a single-page '{page}' for a website using HTML and CSS.

    - If the page is 'index.html', include a brief summary of the event. For 'contact.html', generate contact information, and so on, depending on the page type.
    - The event details are as follows: '{event_details}'.
    - The website's theme is: '{json.dumps(website_theme)}'.
    - You may use the following images: {' '.join(asset_images)}. Include at least one image on the page, ensuring that images are relevant to the content when possible. Use the format 'images/imagename.png' to reference images.
    - Ensure the page is responsive and follows modern web design principles.
    - Use the provided CSS to style the page consistently with the overall theme.
    - Make sure all internal links use relative paths (e.g., './page_name.html').

    Provide your response as a complete HTML file, including the DOCTYPE, html, head, and body tags. Embed the CSS directly in a style tag within the head. Do not include any other text, such as comments or additional tags.
    """

    messages = [
        {"role": "system", "content": "You are a skilled web developer creating a modern, responsive website. Your response should only be the HTML code, with no other text or markup."},
        {"role": "user", "content": prompt}
    ]

    response = client.chat.complete(
        model=MODELS["text"],
        messages=messages
    )

    return response.choices[0].message.content


def generate_website(user_input: str) -> dict:
    try:
        event_details = generate_event_details(user_input)
        website_theme = generate_website_theme(event_details)
        pages = generate_pages(website_theme, event_details, [])
        
        return {
            "theme": website_theme,
            "pages": pages
        }
    except Exception as e:
        return {
            "error": str(e),
            "traceback": traceback.format_exc()
        }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        json.dump({"error": "No input provided"}, sys.stderr)
        sys.exit(1)

    user_input = sys.argv[1]
    result = generate_website(user_input)
    
    try:
        json_result = json.dumps(result)
        print(json_result)
    except Exception as e:
        json.dump({
            "error": f"Failed to serialize result: {str(e)}",
            "traceback": traceback.format_exc()
        }, sys.stderr)
        sys.exit(1)