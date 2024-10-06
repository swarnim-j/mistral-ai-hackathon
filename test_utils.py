from mistralai import Mistral
from mistralai.models.sdkerror import SDKError
import os
import sys
import base64
import re 
import json
from typing import List, Dict
import traceback
import asyncio
from jinja2 import Environment, FileSystemLoader
from tools import SearchTooling, _encode_image
import shutil
from jinja2 import Environment, FileSystemLoader
api_key = os.environ.get("MISTRAL_API_KEY")
if not api_key:
    raise ValueError("MISTRAL_API_KEY environment variable is not set")
client = 
MODELS = {
    "text": "mistral-large-latest",
    "image": "pixtral-12b-2409",
    "code": "codestral-mamba-latest",
}

def clear_directory(directory_path):
    try:
        if os.path.exists(directory_path):
            for item in os.listdir(directory_path):
                item_path = os.path.join(directory_path, item)
                if os.path.isfile(item_path):
                    os.unlink(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            print(f"Directory '{directory_path}' has been cleared.")
        else:
            print(f"Directory '{directory_path}' does not exist.")
    except Exception as e:
        print(f"An error occurred while clearing the directory: {e}")

def generate_event_details(user_input: str) -> str:
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
        response = client.chat.complete(model=MODELS["text"], messages=messages)
        return response.choices[0].message.content
    except SDKError as e:
        raise RuntimeError(f"Mistral API error: {str(e)}")

def _list_file_names(directory: str) -> List[str]:
    return os.listdir(directory)
def get_reference_images(event_details):
    template_dir = os.path.join(os.path.dirname(__file__), "prompts")
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("get_reference_images.xml.jinja")

    rendered_content = template.render(event_details=event_details)

    query_messages = [
        {"role": "system", "content": "You are a creative web designer assistant."},
        {"role": "user", "content": rendered_content},
    ]
    searchTooling = SearchTooling(prompt=event_details)
    query_response = client.chat.complete(
        model=MODELS["text"],
        messages=query_messages,
        tools=searchTooling.tools,
        tool_choice="required",
    )

    tool_calls = query_response.choices[0].message.tool_calls
    function_name = "screenshot_web"
    image_queries = []
    for call in tool_calls:
        function_params = json.loads(call.function.arguments)
        print(function_params)
        image_queries.append(function_params["query"])

    image_queries = image_queries[:min(len(image_queries), 5)]
    for query in image_queries:
        searchTooling.function_names[function_name](query)

    screenshot_dir = os.path.join(os.getcwd(), "screenshots")
    screenshot_files = [
        f for f in os.listdir(screenshot_dir)
        if os.path.isfile(os.path.join(screenshot_dir, f))
    ]

    return screenshot_files


def generate_website_theme(event_details: str, reference_images: List[str], image_dir: str = "screenshots") -> Dict[str, str]:
    image_paths = [os.path.join(os.getcwd(), image_dir, image_name) for image_name in reference_images]
    images = [{"type": "image_url", "image_url": f"data:image/jpeg;base64,{_encode_image(path)}"} for path in image_paths]

    base_css = """
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@200;300;400;500;600;700&display=swap');

    :root {
        --primary-color: #4a4af4;
        --secondary-color: #8b8b8b;
        --background-color: #0f172a;
        --text-color: #e2e8f0;
        --accent-color: #22d3ee;
    }

    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    body {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #0f172a, #1a2642);
        color: var(--text-color);
        line-height: 1.6;
        font-weight: 300;
    }

    .container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 2rem;
    }

    header {
        padding: 1.5rem 0;
        background: linear-gradient(180deg, rgba(15,23,42,0.9) 0%, rgba(15,23,42,0) 100%);
        position: fixed;
        width: 100%;
        z-index: 1000;
        backdrop-filter: blur(5px);
    }

    nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .logo {
        font-size: 1.5rem;
        font-weight: 500;
        color: var(--accent-color);
        letter-spacing: 1px;
    }

    .nav-links a {
        color: var(--text-color);
        text-decoration: none;
        margin-left: 1.5rem;
        font-weight: 300;
        transition: all 0.3s ease;
    }

    .nav-links a:hover {
        color: var(--accent-color);
        transform: translateY(-2px);
    }

    .hero {
        text-align: center;
        padding: 10rem 0 6rem;
        background: linear-gradient(135deg, rgba(74,74,244,0.1), rgba(34,211,238,0.1));
    }

    h1 {
        font-size: 4rem;
        margin-bottom: 1rem;
        font-weight: 300;
        background: linear-gradient(45deg, var(--primary-color), var(--accent-color));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -1px;
    }

    .subtitle {
        font-size: 1.25rem;
        color: var(--secondary-color);
        margin-bottom: 2rem;
        font-weight: 200;
    }

    .cta-button {
        display: inline-block;
        background: linear-gradient(45deg, var(--primary-color), var(--accent-color));
        color: white;
        padding: 0.75rem 2rem;
        border-radius: 50px;
        text-decoration: none;
        font-weight: 600;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 0.9rem;
    }

    .cta-button:hover {
        opacity: 0.9;
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(74,74,244,0.3);
    }

    .section {
        padding: 6rem 0;
    }

    h2 {
        font-size: 2.5rem;
        margin-bottom: 2rem;
        text-align: center;
        font-weight: 300;
        color: var(--accent-color);
    }

    .grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 2rem;
    }

    .card {
        background: linear-gradient(135deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02));
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
        border: 1px solid rgba(255,255,255,0.1);
    }

    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }

    .card h3 {
        font-weight: 500;
        margin-bottom: 1rem;
        color: var(--accent-color);
    }

    .card p {
        font-weight: 300;
    }

    footer {
        text-align: center;
        padding: 2rem 0;
        color: var(--secondary-color);
        font-weight: 200;
        background: linear-gradient(0deg, rgba(15,23,42,0.9) 0%, rgba(15,23,42,0) 100%);
    }

    @media (max-width: 768px) {
        h1 {
            font-size: 3rem;
        }
        
        .nav-links {
            display: none;
        }
    }
    """

    base_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Hack Cambridge 2024</title>
        <link rel="stylesheet" href="base_css.css">
    </head>
    <body>
        <header>
            <div class="container">
                <nav>
                    <div class="logo">Hack Cambridge</div>
                    <div class="nav-links">
                        <a href="#about">About</a>
                        <a href="#tracks">Tracks</a>
                        <a href="#sponsors">Sponsors</a>
                        <a href="#faq">FAQ</a>
                        <a href="#apply" class="cta-button">Apply Now</a>
                    </div>
                </nav>
            </div>
        </header>

        <main>
            <section class="hero">
                <div class="container">
                    <h1>Hack Cambridge 2024</h1>
                    <p class="subtitle">Cambridge University's Premier Hackathon</p>
                    <a href="#apply" class="cta-button">Join the Innovation</a>
                </div>
            </section>

            <section id="about" class="section">
                <div class="container">
                    <h2>About the Event</h2>
                    <p>Hack Cambridge brings together the brightest minds in technology to solve real-world problems and push the boundaries of innovation. Join us for 24 hours of coding, creativity, and collaboration.</p>
                </div>
            </section>

            <section id="tracks" class="section">
                <div class="container">
                    <h2>Hackathon Tracks</h2>
                    <div class="grid">
                        <div class="card">
                            <h3>AI & Machine Learning</h3>
                            <p>Develop cutting-edge AI solutions to tackle complex challenges.</p>
                        </div>
                        <div class="card">
                            <h3>FinTech Revolution</h3>
                            <p>Innovate in the world of finance and create the future of banking.</p>
                        </div>
                        <div class="card">
                            <h3>Sustainable Tech</h3>
                            <p>Build technology that addresses environmental and social issues.</p>
                        </div>
                    </div>
                </div>
            </section>

            <section id="sponsors" class="section">
                <div class="container">
                    <h2>Our Sponsors</h2>
                    <!-- Add sponsor logos or names here -->
                </div>
            </section>

            <section id="faq" class="section">
                <div class="container">
                    <h2>Frequently Asked Questions</h2>
                    <!-- Add FAQ items here -->
                </div>
            </section>
        </main>

        <footer>
            <div class="container">
                <p>&copy; 2024 Hack Cambridge. All rights reserved.</p>
            </div>
        </footer>
    </body>
    </html>
    """

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
                    "text": f"""Customize and enhance the following base CSS and HTML for this event: {event_details}

                    Base CSS:
                    {base_css}

                    Base HTML:
                    {base_html}

                    Instructions:
                    1. Modify the color scheme to suit the event theme.
                    2. Add additional CSS for creative layouts and modern design elements.
                    3. Enhance the HTML structure with more sections relevant to the event.
                    4. Incorporate subtle animations or transitions for interactive elements.
                    5. Ensure the design is responsive and works well on all devices.

                    Format your response as follows:

                    [CSS]
                    (Your enhanced CSS code here, including the base CSS with your modifications)
                    [/CSS]

                    [HTML]
                    (Your enhanced HTML structure here, based on the base HTML with your additions)
                    [/HTML]

                    [DESIGN_TOKENS]
                    (Your design tokens here in JSON format, including color schemes, typography, spacing, and breakpoints)
                    [/DESIGN_TOKENS]

                    Ensure the design is visually appealing, modern, and aligns with the event's theme while maintaining usability and accessibility.""",
                },
                *images,
            ],
        },
    ]

    response = client.chat.complete(model=MODELS["image"], messages=messages)
    response_content = response.choices[0].message.content.replace("```html", "").replace("```", "").replace("```css", "")

    css = re.search(r'\[CSS\](.*?)\[/CSS\]', response_content, re.DOTALL)
    html = re.search(r'\[HTML\](.*?)\[/HTML\]', response_content, re.DOTALL)
    design_tokens = re.search(r'\[DESIGN_TOKENS\](.*?)\[/DESIGN_TOKENS\]', response_content, re.DOTALL)
    
    css = css.group(1).strip() if css else ""
    html = html.group(1).strip() if html else ""
    design_tokens = json.loads(design_tokens.group(1).strip()) if design_tokens else {}
    
    return {
        "css": css,
        "html": html,
        "design_tokens": design_tokens
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

    html_content = response.choices[0].message.content.replace("```html", "").replace("```", "")

    return html_content

def refine_pages(pages: List[Dict[str, str]], website_theme: Dict[str, str]):
    template_dir = os.path.join(os.path.dirname(__file__), "prompts")
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("refine_website.xml.jinja")

    rendered_content = template.render(
        pages=pages,
        html_theme=website_theme.get("html", ""),
        css_theme=website_theme.get("css", "")
    )
    messages = [
        {"role": "system", "content": "You are an expert web developer tasked with refining and improving web pages. For each file, provide the filename, content, and any additional notes or explanations. Use [FILE] to start a file section, [CONTENT] for the file content, and [NOTES] for any additional information."},
        {"role": "user", "content": rendered_content}
    ]

    response = client.chat.complete(
        model=MODELS["text"],
        messages=messages
    )

    refined_pages = []
    content = response.choices[0].message.content
    file_sections = re.split(r'\[FILE\]', content)[1:]  # Skip the first empty split
    
    for section in file_sections:
        file_match = re.search(r'(.*?)\[CONTENT\](.*?)\[NOTES\](.*)', section, re.DOTALL)
        if file_match:
            filename = file_match.group(1).strip()
            file_content = file_match.group(2).strip()
            notes = file_match.group(3).strip()
            refined_pages.append({
                "name": filename,
                "content": file_content,
                "notes": notes
            })
    return refined_pages
def generate_images(event_details: str, num_images: int = 5):
    template_dir = os.path.join(os.path.dirname(__file__), "prompts")
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("get_event_images.xml.jinja")

    rendered_content = template.render(event_details=event_details)

    query_messages = [
        {"role": "system", "content": "You are a creative web designer assistant."},
        {"role": "user", "content": rendered_content},
    ]
    searchTooling = SearchTooling(prompt=event_details)
    query_response = client.chat.complete(
        model=MODELS["text"],
        messages=query_messages,
        tools=searchTooling.image_search_tool,
        tool_choice="required",
    )

    tool_calls = query_response.choices[0].message.tool_calls
    function_name = "search_web_pictures"
    saved_images = []
    
    for i, call in enumerate(tool_calls[:num_images]):
        function_params = json.loads(call.function.arguments)
        searchTooling.function_names[function_name](**function_params)


    return saved_images

def generate_website(user_input: str) -> dict:
    try:
        clear_directory('screenshots')
        clear_directory('images')
        event_details = generate_event_details(user_input)
        website_theme = generate_website_theme(event_details)
        pages = generate_pages(website_theme, event_details, [])
        update_refined_pages = refine_pages(pages, website_theme)
        generate_images(event_details=event_details)
        return {
            "theme": website_theme,
            "pages": update_refined_pages
        }
    except Exception as e:
        return {
            "error": str(e),
            "traceback": traceback.format_exc()
        }

def update_pages_with_images(pages: List[Dict[str, str]], images: List[str]) -> List[Dict[str, str]]:
    updated_pages = []
    for page in pages:
        content = page['content']
        for image in images:
            # Replace placeholder images or add new images where appropriate
            content = content.replace('images/placeholder.jpg', f'images/{image}', 1)
        updated_pages.append({
            "name": page['name'],
            "content": content,
            "notes": page.get('notes', '')
        })
    return updated_pages

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