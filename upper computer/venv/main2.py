from PIL import Image


def crop_image(image_path, target_width, target_height):
    # 打开图像文件
    img = Image.open(image_path)

    # 获取图像的原始大小
    width, height = img.size

    # 计算裁剪的左上角和右下角坐标
    left = (width - target_width) / 2
    top = (height - target_height) / 2
    right = (width + target_width) / 2
    bottom = (height + target_height) / 2

    # 裁剪图像
    cropped_img = img.crop((left, top, right, bottom))

    return cropped_img


# 调用函数裁剪图片
image_path = "img.png"  # 图片路径
target_width = 598
target_height = 660
cropped_image = crop_image(image_path, target_width, target_height)

# 保存裁剪后的图片
cropped_image.save("image.png")
