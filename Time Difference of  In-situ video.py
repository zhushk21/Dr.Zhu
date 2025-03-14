import os
import re
import glob
import pandas as pd

def parse_filename(filename):
    """解析文件名并返回时间信息和总秒数"""
    pattern = r'^image-(\d{2})(\d{2})(\d{2})_(\d{3})\.jpg$'
    match = re.match(pattern, filename)
    if not match:
        return None, None
    
    hh, mm, ss, ms = map(int, match.groups())
    time_str = f"{hh:02}{mm:02}{ss:02}_{ms:03}"
    total_seconds = hh * 3600 + mm * 60 + ss + ms / 1000.0
    return time_str, total_seconds

def main():
    # 用户输入路径
    input_folder = r'E:\\Dr\\728-aluminum-alloy\\In-situ mechanics\\TEM\\20250309-Al-2.6Mg\\video\\2025_03-09 161526'
    output_path = r'E:\\Dr\\728-aluminum-alloy\\In-situ mechanics\\TEM\\20250309-Al-2.6Mg\\video_timestamps.xlsx'

    # 收集有效文件数据
    files_data = []
    for filepath in glob.glob(os.path.join(input_folder, 'image-*.jpg')):
        filename = os.path.basename(filepath)
        time_str, total_seconds = parse_filename(filename)
        if time_str:
            files_data.append((filename, time_str, total_seconds))

    if not files_data:
        print("未找到符合格式的文件")
        return

    # 按时间排序
    files_data.sort(key=lambda x: x[1])
    
    # 计算时间差
    base_time = files_data[0][2]
    results = []
    for filename, time_str, seconds in files_data:
        time_diff = round(seconds - base_time, 3)
        # 格式化时间字符串为 "HHhMMmSS.sssS"
        formatted_time = f"{time_str[:2]}h{time_str[2:4]}m{time_str[4:6]}.{time_str[7:]}s"
        results.append({
            "文件名": filename,
            "时间差(s)": time_diff
        })

    # 创建并保存DataFrame
    df = pd.DataFrame(results)
    df.to_excel(output_path, index=False)
    print(f"文件已成功生成：{output_path}")

if __name__ == "__main__":
    main()