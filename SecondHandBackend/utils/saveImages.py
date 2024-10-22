import re
from SecondHandBackend import settings


def ger_image_save_path(url):
    match = re.search(r'media/(.+)', url)
    key = match.group(1)
    return settings.MEDIA_ROOT + "/" + key


def get_image_url(save_path):
    print("Save Path:", save_path)
    base_url = "http://127.0.0.1:8000/"

    # 将反斜杠转换为斜杠，以便与正则表达式匹配
    save_path = save_path.replace("\\", "/")

    # 匹配 media 后面的路径
    match = re.search(r'media/(.+)', save_path)

    # 如果匹配成功，生成 URL
    if match:
        key = match.group(1)
        return base_url + "media/" + key
    else:
        print("No match found in the path.")
        return None  # 或者返回其他错误提示


s = r"D:\pyhonProject\Django\SecondHandBackend\SecondHandBackend/media/68d77288-f812-4734-a684-c8a7b5f4202f.png"
