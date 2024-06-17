import numpy as np
import cv2

# 计算 LBP 码
def calculate_lbp_pixel(img, x, y):
    center = img[x, y]
    code = 0
    # 顺时针遍历8个像素点
    for i, (dx, dy) in enumerate([(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]):
        new_x, new_y = x + dx, y + dy
        # 如果周围的像素值大于中心像素值，则为1，否则为0
        if img[new_x, new_y] >= center:
            code |= 1 << i
    return code

# 计算 LBP 图像
def calculate_lbp_image(img):
    height, width = img.shape
    lbp_img = np.zeros((height, width), dtype=np.uint8)
    for i in range(1, height-1):
        for j in range(1, width-1):
            lbp_img[i, j] = calculate_lbp_pixel(img, i, j)
    return lbp_img[:height-2, :width-2]  # 裁剪LBP图像的边界，使其尺寸与原始图像相同


# 计算 LBP 图像差异度
def calculate_lbp_diff(lbp_img1, lbp_img2):
    return np.sum(lbp_img1 != lbp_img2)

# 主函数
def main():
    # 读取两个图像
    img1 = cv2.imread('test.png', cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread('image.png', cv2.IMREAD_GRAYSCALE)

    # 计算两个图像的 LBP 图像
    lbp_img1 = calculate_lbp_image(img1)
    lbp_img2 = calculate_lbp_image(img2)

    # 计算 LBP 图像的差异度
    diff = calculate_lbp_diff(lbp_img1, lbp_img2)

    # 显示原始图像和 LBP 图像
    cv2.imshow('Original Image 1', img1)
    cv2.imshow('LBP Image 1', lbp_img1)
    cv2.imshow('Original Image 2', img2)
    cv2.imshow('LBP Image 2', lbp_img2)
    print('LBP Image Difference:', diff)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
