from mimetypes import guess_type
import os
from dotenv import load_dotenv
import requests
import base64
from openai import AzureOpenAI
import base64
from dotenv import load_dotenv

load_dotenv()


imageAzureOpenAI = AzureOpenAI( 
    azure_endpoint=os.getenv("AZURE_OPENAI_IMAGE_ENDPOINT"),
    api_version=os.getenv("AZUER_OPENAI_IMAGE_VERSION"),
    azure_deployment=os.getenv("AZURE_OPENAI_IMAGE_DEPLOYMENT"),
    api_key=os.getenv("AZURE_OPENAI_IMAGE_KEY"))


from mimetypes import guess_type
import os
from dotenv import load_dotenv
import requests
import base64
from openai import AzureOpenAI,AsyncAzureOpenAI
import base64
import uuid
from datetime import datetime
from azure.storage.blob import BlobServiceClient, ContentSettings

from dotenv import load_dotenv

load_dotenv()

# Setup Azure Blob Storage client
STORAGE_ACCOUNT_NAME = os.getenv("STORAGE_ACCOUNT_NAME")
STORAGE_ACCOUNT_KEY = os.getenv("STORAGE_ACCOUNT_KEY")
CONTAINER_NAME = "$web"

# Get the full URL for the blob storage website
BLOB_SERVICE_URL = f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net"
WEBSITE_URL = f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net"

def upload_image_to_blob_storage(image_bytes, file_name=None):
    """
    Upload an image to Azure Blob Storage with static website hosting and return the URL
    
    Args:
        image_bytes: The image binary data
        file_name: Optional file name, if not provided a UUID will be generated
        
    Returns:
        The URL to access the uploaded image
    """
    try:
        # Create a unique filename if one is not provided
        if not file_name:
            # Create a timestamp-based unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            file_name = f"images/{timestamp}_{unique_id}.png"
        
        # Initialize the BlobServiceClient
        blob_service_client = BlobServiceClient(
            account_url=f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net", 
            credential=STORAGE_ACCOUNT_KEY
        )
        
        # Get container client
        container_client = blob_service_client.get_container_client(CONTAINER_NAME)
        
        # Set content settings for image
        content_settings = ContentSettings(content_type='image/png')
        
        # Upload the image
        blob_client = container_client.upload_blob(
            name=file_name,
            data=image_bytes,
            overwrite=True,
            content_settings=content_settings
        )
        
        # Return the public URL for the image
        # Using the website URL for static website hosting
        return f"{WEBSITE_URL}/{CONTAINER_NAME}/{file_name}"
    
    except Exception as e:
        print(f"Error uploading image to Azure Blob Storage: {str(e)}")
        return None

# 定义生成图像的工具函数
async def generate_image(prompt):
    """
    Generate an image using Azure OpenAI and upload it to Blob Storage
    
    Args:
        prompt: The text prompt for image generation
        
    Returns:
        The URL of the uploaded image
    """
    imageAzureOpenAI = AsyncAzureOpenAI( 
        azure_endpoint=os.getenv("AZURE_OPENAI_IMAGE_ENDPOINT"),
        api_version=os.getenv("AZUER_OPENAI_IMAGE_VERSION"),
        azure_deployment=os.getenv("AZURE_OPENAI_IMAGE_DEPLOYMENT"),
        api_key=os.getenv("AZURE_OPENAI_IMAGE_KEY")
    )

    try:
        # Generate the image
        result = await imageAzureOpenAI.images.generate(
            model="gpt-image-1",
            prompt=prompt
        )
        
        # Get the image data
        image_base64 = result.data[0].b64_json
        image_bytes = base64.b64decode(image_base64)
        
        # Upload to Azure Blob Storage
        image_url = upload_image_to_blob_storage(image_bytes)
        
        return image_url
    
    except Exception as e:
        print(f"Error generating or uploading image: {str(e)}")
        return None

# 定义获取图像并反馈的工具函数
def fetch_image_base64(url:str)->str:
    """
    Fetch an image from a URL and convert it to base64 format.
    Args:
        url: URL of the image to fetch
    Returns:
        str: Base64 encoded string of the image
    """
    response = requests.get(url)
    if response.status_code == 200:
        image_data = response.content
        base64_image = base64.b64encode(image_data).decode('utf-8')
        return base64_image
    else:
        return None

def get_feedback(image_url:str, description:str)->str:
    """"
    Get feedback on the generated image from the model.
    Args:
        image_url: URL of the generated image
        description: Description of the image for evaluation
    Returns:
        str: Feedback from the model
    """
    base64_image = fetch_image_base64(image_url)
    if not base64_image:
        return "无法获取图像。"

    # Guess the MIME type of the image based on the file extension
    mime_type, _ = guess_type(image_url)
    if mime_type is None:
        mime_type = 'application/octet-stream'  # Default MIME type if none is found


    messages = [
        {"role": "user", "content": [
            {"type": "image_url","image_url":{"url": f"data:{mime_type};base64,{base64_image}"}},
            {"type": "text", "text": f"评估此图像是否符合描述：{description}。提供反馈，说明优点和改进建议。"}
        ]}
    ]

    try:
        response = chat_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            messages=messages
        )
        feedback = response.choices[0].message.content
        return feedback
    except Exception as e:
        return f"获取反馈错误：{str(e)}"