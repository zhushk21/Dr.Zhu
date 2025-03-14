import cv2
import os
import numpy as np
from moviepy.editor import VideoFileClip, clips_array, CompositeVideoClip


def get_frame_count(video_path):
    cap = cv2.VideoCapture(video_path)
    count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    return count

def get_frame_at_image(image_name, image_folder):
    images = [img for img in os.listdir(image_folder) if img.endswith(".jpg")]
    images.sort()
    if image_name in images:
        return images.index(image_name)
    return -1

def get_video_fps(video_path):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)  # 获取帧率
    cap.release()
    return fps

def adjust_video_speed(input_video_path, output_video_path, new_fps):
    cap = cv2.VideoCapture(input_video_path)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # 创建输出视频对象，使用新的帧率
    out = cv2.VideoWriter(output_video_path, fourcc, new_fps, (frame_width, frame_height))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        out.write(frame)  # 写入当前帧

    cap.release()
    out.release()

def split_video_at_frame(video_path, start_frame, output_path1, output_path2):
    cap = cv2.VideoCapture(video_path)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    fps = get_video_fps(video_path)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    out1 = cv2.VideoWriter(output_path1, fourcc, fps, (frame_width, frame_height))
    out2 = cv2.VideoWriter(output_path2, fourcc, fps, (frame_width, frame_height))

    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_count < start_frame:
            out1.write(frame)
        else:
            out2.write(frame)

        frame_count += 1

    cap.release()
    out1.release()
    out2.release()

def concatenate_videos_with_overlay(video1_path, video2_path, merged_video_path):
    # video1 是背景视频（output_video_part2），video2 是叠加视频（adjusted_stress_video）
    video1 = VideoFileClip(video1_path)  # output_video_part2
    video2 = VideoFileClip(video2_path)  # adjusted_stress_video

    # 确保 video1 的高度
    target_height = video1.size[1]

    # 调整 video2 的高度，并保持宽高比，同时缩小到1/4的大小
    video2_resized = video2.resize(height=target_height / 4)

    # 计算位置，右下角
    x_position = video1.size[0] - video2_resized.size[0] - 10  # 10像素的边距
    y_position = video1.size[1] - video2_resized.size[1] - 10  # 10像素的边距

    # 计算时间差
    time_difference = video2.duration - video1.duration

    # 如果 video2 较长，增加 video1 的持续时间
    if time_difference > 0:
        video1 = video1.set_duration(video1.duration + time_difference)

    # 创建带有叠加的视频
    final_video = CompositeVideoClip([video1.set_duration(video1.duration), 
                                       video2_resized.set_position((x_position, y_position))])

    # 写入输出视频
    final_video.write_videofile(
        merged_video_path,
        codec='libx264',  # 使用更高质量的编码器
        bitrate='5000k',   # 设置比特率，视需要可调整
        fps=video1.fps,    # 保持原始帧速率
        audio=False        # 不处理音轨
    )


def concatenate_videos_with_padding(video1_path, video2_path, merged_video_path):
    video1 = VideoFileClip(video1_path)
    video2 = VideoFileClip(video2_path)

    # 确保 video2 的高度
    target_height = video2.size[1]

    # 调整 video1 的高度，并保持宽高比
    video1_resized = video1.resize(height=target_height)

    # 计算填充的宽度
    width_diff = video2.size[0] - video1_resized.size[0]
    if width_diff > 0:
        # 填充白色背景
        video1_padded = video1_resized.on_color(size=(video2.size[0], target_height), color=(255, 255, 255))
    else:
        video1_padded = video1_resized

    # 创建顺序拼接
    final_video = CompositeVideoClip([video1_padded.set_duration(video1.duration), video2.set_duration(video2.duration)])

    # 写入输出视频，设置更高的比特率和编码器，不处理音轨
    final_video.write_videofile(
        merged_video_path,
        codec='libx264',  # 使用更高质量的编码器
        bitrate='5000k',   # 设置比特率，视需要可调整
        fps=video1.fps,    # 保持原始帧速率
        audio=False        # 不处理音轨
    )


if __name__ == "__main__":
    # 路径设置
    image_folder = r"E:\\Dr\\728-aluminum-alloy\\In-situ mechanics\\TEM\\20250309-Al-2.6Mg\\video\\2025_03-09 161526"
    output_video_path = r"E:\\Dr\\728-aluminum-alloy\\In-situ mechanics\\TEM\\20250309-Al-2.6Mg\\video\\output_video_cropped_with_name.avi"
    stress_video_path = r"E:\\Dr\\728-aluminum-alloy\\In-situ mechanics\\TEM\\20250309-Al-2.6Mg\\stress_strain_video.avi"
    merged_video_path = r"E:\\Dr\\728-aluminum-alloy\\In-situ mechanics\\TEM\\20250309-Al-2.6Mg\\merged_video.avi"

    # 查找帧位置
    start_frame = get_frame_at_image("image-161547_677.jpg", image_folder)
    end_frame = get_frame_at_image("image-161815_682.jpg", image_folder)
    
    if start_frame == -1 or end_frame == -1:
        print("无法找到指定的图像文件。")
        exit()

    # 通过OpenCV读取帧率
    output_fps = get_video_fps(output_video_path) 
    # 获取output_video的帧数 
    output_frame_count = get_frame_count(output_video_path)
    
    # 拆分output_video
    output_video_part1 = r"E:\\Dr\\728-aluminum-alloy\\In-situ mechanics\\TEM\\20250309-Al-2.6Mg\\video\\output_video_part1.avi"
    output_video_part2 = r"E:\\Dr\\728-aluminum-alloy\\In-situ mechanics\\TEM\\20250309-Al-2.6Mg\\video\\output_video_part2.avi"
    split_video_at_frame(output_video_path, start_frame, output_video_part1, output_video_part2)

    # 获取stress视频的帧数
    stress_frame_count = get_frame_count(stress_video_path)

    # 计算需要的速度
    total_frames = end_frame - start_frame + 1
    new_fps = (stress_frame_count/ total_frames) * output_fps

    # 调整stress视频的速度
    adjusted_stress_video_path = r"E:\\Dr\\728-aluminum-alloy\\In-situ mechanics\\TEM\\20250309-Al-2.6Mg\\adjusted_stress_video.avi"
    adjust_video_speed(stress_video_path, adjusted_stress_video_path, new_fps)

    # 左右拼合output_video_part2和adjusted_stress_video
    merged_video_part = r"E:\\Dr\\728-aluminum-alloy\\In-situ mechanics\\TEM\\20250309-Al-2.6Mg\\video\\merged_video_part.avi"
    concatenate_videos_with_overlay(output_video_part2, adjusted_stress_video_path, merged_video_part)

    # 顺序拼合output_video_part1和merged_video_part
    final_merged_video_path = r"E:\\Dr\\728-aluminum-alloy\\In-situ mechanics\\TEM\\20250309-Al-2.6Mg\\final_merged_video.avi"
    concatenate_videos_with_padding(output_video_part1, merged_video_part, final_merged_video_path)

    print(f"合并视频已保存至 {final_merged_video_path}")