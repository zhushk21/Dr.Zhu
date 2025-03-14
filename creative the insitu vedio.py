import cv2
import os

def create_video_from_images(image_folder, output_video_path_cropped_with_name, output_video_path_cropped_without_name, frame_rate, codec, crop_area=None):
    images = [img for img in os.listdir(image_folder) if img.endswith(".jpg")]
    print(f"Found {len(images)} images in the folder.")
    images.sort()

    if not images:
        print("No JPG images found in the specified folder.")
        return

    first_image_path = os.path.join(image_folder, images[0])
    first_image = cv2.imread(first_image_path)

    if first_image is None:
        print(f"Error: Unable to read the first image at {first_image_path}")
        return
    
    height, width = first_image.shape[:2]
    fourcc = cv2.VideoWriter_fourcc(*codec)
    
    # Create two video writers: one with names and one without
    video_with_name = cv2.VideoWriter(output_video_path_cropped_with_name, fourcc, frame_rate, (width, height))
    video_without_name = cv2.VideoWriter(output_video_path_cropped_without_name, fourcc, frame_rate, (width, height))

    for image in images:
        img_path = os.path.join(image_folder, image)
        img = cv2.imread(img_path)

        if img is None:
            print(f"Warning: Unable to read image at {img_path}. Skipping...")
            continue

        if crop_area:
            x, y, w, h = crop_area
            cropped_img = img[y:y+h, x:x+w]
            cropped_img = cv2.resize(cropped_img, (width, height))

            # Write cropped image to video with name
            img_with_name = cropped_img.copy()  # 创建一个副本用于添加名称
            cv2.putText(img_with_name, image, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            video_with_name.write(img_with_name)
            print(f"Wrote cropped image with name to video: {img_path}")

            # Write cropped image to video without name
            video_without_name.write(cropped_img)
            print(f"Wrote cropped image without name to video: {img_path}")

    video_with_name.release()
    video_without_name.release()
    print(f"Cropped video with names saved to {output_video_path_cropped_with_name}")
    print(f"Cropped video without names saved to {output_video_path_cropped_without_name}")
    cv2.destroyAllWindows()

if __name__ == "__main__":
    image_folder = r"E:\\Dr\\728-aluminum-alloy\\In-situ mechanics\\TEM\\20250309-Al-2.6Mg\\video\\2025_03-09 161526"
    output_video_path_cropped_with_name = r"E:\\Dr\\728-aluminum-alloy\\In-situ mechanics\\TEM\\20250309-Al-2.6Mg\\output_video_cropped_with_name.avi"
    output_video_path_cropped_without_name = r"E:\\Dr\\728-aluminum-alloy\\In-situ mechanics\\TEM\\20250309-Al-2.6Mg\\output_video_cropped_without_name.avi"
    frame_rate = 24
    codec = 'XVID'
    crop_area = (15, 92, 935, 935)  # 裁剪区域 (x起始像素, y起始像素, x像素宽度, y像素高度)

    create_video_from_images(image_folder, output_video_path_cropped_with_name, output_video_path_cropped_without_name, frame_rate, codec, crop_area)