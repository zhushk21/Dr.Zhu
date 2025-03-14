import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import cv2
import os
import time
import re
from datetime import datetime, timedelta
from scipy.signal import savgol_filter

def parse_filename(filename):
    """解析文件名并返回时间信息和总秒数"""
    pattern = r'^image-(\d{2})(\d{2})(\d{2})_(\d{3})\.jpg$'
    match = re.match(pattern, filename)
    if not match:
        return None, None
    
    hh, mm, ss, ms = map(int, match.groups())
    total_seconds = hh * 3600 + mm * 60 + ss + ms / 1000.0
    return f"{hh:02}{mm:02}{ss:02}_{ms:03}", total_seconds

def create_stress_strain_video(input_file_path, output_video_path, sheet_name='input_data', speed_factor=50, xlim=None, ylim=None):
    try:
        # 读取Excel文件
        data = pd.read_excel(input_file_path, sheet_name=sheet_name)
        first_column = data.columns[0]

        # 公共数据准备
        epsilon = data['ε (%)']
        sigma = data['σ (MPa)']
        valid_indices = []
        cumulative_time = []

        # 时间处理逻辑
        if first_column == 'Time(Sec)':
            elapsed_time = data[first_column].astype(str)
            time_points = []
            
            for idx, time_str in enumerate(elapsed_time):
                try:
                    parts = time_str.split(':')
                    if len(parts) == 3:
                        hours, minutes, seconds = map(float, parts)
                    elif len(parts) == 2:
                        minutes, seconds = map(float, parts)
                        hours = 0
                    else:
                        raise ValueError("无效时间格式")
                    
                    total_seconds = hours * 3600 + minutes * 60 + seconds
                    time_points.append(total_seconds)
                    valid_indices.append(idx)
                except Exception as e:
                    print(f"跳过无效时间格式: {time_str} - {e}")
                    continue

            # 计算累积时间
            base_time = datetime.strptime("00:00:00.000", "%H:%M:%S.%f")
            cumulative_time = [base_time + timedelta(seconds=(sum(time_points[:i]) / speed_factor)) 
                              for i in range(len(time_points))]

        elif first_column == 'File name':
            filenames = data[first_column].astype(str)
            time_seconds = []
            
            for idx, filename in enumerate(filenames):
                _, total_seconds = parse_filename(filename)
                if total_seconds is not None:
                    time_seconds.append(total_seconds)
                    valid_indices.append(idx)
                else:
                    print(f"跳过无效文件名: {filename}")

            if not time_seconds:
                raise ValueError("没有有效的文件名时间数据")
            
            # 计算时间差并生成时间轴
            base_time = datetime.strptime("00:00:00.000", "%H:%M:%S.%f")
            time_diff = [ts - time_seconds[0] for ts in time_seconds]
            cumulative_time = [base_time + timedelta(seconds=(td / speed_factor)) 
                              for td in time_diff]

        else:
            raise ValueError(f"不支持的首列类型: {first_column}")

        # 过滤有效数据
        valid_data = data.iloc[valid_indices].reset_index(drop=True)
        epsilon = valid_data['ε (%)']
        sigma = valid_data['σ (MPa)']

        # 数据平滑处理
        window_length = min(37, len(epsilon))
        polyorder = 2
        smoothed_epsilon = savgol_filter(epsilon, window_length, polyorder)
        smoothed_sigma = savgol_filter(sigma, window_length, polyorder)

        # 确保输出目录存在
        output_dir = os.path.dirname(output_video_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # 将平滑后的数据添加到新的Excel工作表
        output_file_path = input_file_path.replace('.xlsx', '_smoothed.xlsx')
        output_file_dir = os.path.dirname(output_file_path)
        if not os.path.exists(output_file_dir):
            os.makedirs(output_file_dir)

        with pd.ExcelWriter(output_file_path, engine='openpyxl', mode='w') as writer:
            smoothed_data = pd.DataFrame({'Smoothed ε (%)': smoothed_epsilon, 'Smoothed σ (MPa)': smoothed_sigma})
            smoothed_data.to_excel(writer, sheet_name='Smoothed_Data', index=False)

        # 创建视频文件
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        fps = 24
        frame_width = 640
        frame_height = 480
        out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))

        plt.figure(figsize=(8, 6))

        for i in range(len(smoothed_epsilon)):
            plt.clf()
            plt.scatter(smoothed_epsilon[:i], smoothed_sigma[:i], color='blue', marker='o', label='Previous Points')
            plt.scatter(smoothed_epsilon[i], smoothed_sigma[i], color='red', marker='o', s=100, label='Current Point')

            # 设置坐标轴范围
            if xlim is not None:
                plt.xlim(xlim)
            else:
                plt.xlim(min(smoothed_epsilon), max(smoothed_epsilon))

            if ylim is not None:
                plt.ylim(ylim)
            else:
                plt.ylim(min(smoothed_sigma), max(smoothed_sigma))

            # #输出平滑的load-displacement曲线
            # plt.xlabel('Displacement (nm)')
            # plt.ylabel('Load (uN)')
            # plt.title('load-displacement Curve (Smoothed)')

            plt.xlabel('ε (%)')
            plt.ylabel('σ (MPa)')
            plt.title('Stress-Strain Curve (Smoothed)')
            plt.grid()
            plt.legend()

            # 保存图形为图像
            plt.savefig('temp_frame.png', bbox_inches='tight')
            frame = cv2.imread('temp_frame.png')
            if frame is not None:
                frame = cv2.resize(frame, (frame_width, frame_height))
                out.write(frame)

            # 控制每帧的显示时间，使用加速后的时间
            if i < len(cumulative_time) - 1:
                next_time = cumulative_time[i + 1]
                current_time = cumulative_time[i]
                wait_time = (next_time - current_time).total_seconds()
                time.sleep(max(0, wait_time))

        out.release()
        os.remove('temp_frame.png')
        print(f"视频已保存为 {output_video_path}，平滑数据已保存至 {output_file_path}")

    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    # 设置路径
    input_file_path = r"E:\Dr\\728-aluminum-alloy\\In-situ mechanics\\TEM\\20250309-Al-2.6Mg\\20250309_input_data.xlsx"
    output_stress_strain_video_path = r"E:\Dr\\728-aluminum-alloy\\In-situ mechanics\\TEM\\20250309-Al-2.6Mg\\stress_strain_video.avi"

    # 自定义坐标轴范围
    # xlim = (0, 160)  # 设置横轴范围
    # ylim = (0, 40)  # 设置纵轴范围
    
    xlim = (0, 10)  # 设置横轴范围
    ylim = (0, 300)  # 设置纵轴范围

    # 创建应力-应变视频，speed_factor 可根据需要调整
    create_stress_strain_video(input_file_path, output_stress_strain_video_path, speed_factor=50, xlim=xlim, ylim=ylim)