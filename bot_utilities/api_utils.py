import google.generativeai as gemini
from openai import OpenAI
from bot_utilities.api_prompt import prompt

gemini.configure(api_key="AIzaSyBiXYuuTUgD5m42TF49_7AmDqCF6QxU2zk")

model = gemini.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=prompt)

openai_client = OpenAI(
    api_key="ng-wvwyhdHCzRCBdlaO7umV2fskewKhB",
    base_url="https://api.naga.ac/v1"
)

def sdxl(prompt):
    response = openai_client.images.generate(
        model="playground-v2.5",
        prompt=prompt,
        n=1,  # images count
        size="4096x4096"
    )
    return response.data[0].url

def gen_text(prompt):
    response = model.generate_content(
        contents=prompt
    )
    return {"generated_text": response.text}