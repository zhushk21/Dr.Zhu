import pandas as pd
from datetime import datetime

def calculate_time_differences(input_excel_path, output_excel_path, sheet_name='raw'):
    # 读取Excel文件中的指定工作表
    df = pd.read_excel(input_excel_path, sheet_name=sheet_name)
    
    # 确保 'Time(Sec)' 列存在
    if 'Time(Sec)' not in df.columns:
        raise ValueError("工作表中不存在 'Time(Sec)' 列")
    
    # 初始化一个空列表来存储时间差
    time_differences = []
    base_time = None
    
    # 遍历每一行，计算时间差
    for _, row in df.iterrows():
        # 解析当前时间
        current_time_str = row['Time(Sec)']
        try:
            # 尝试解析为 "HH:MM:SS fff" 格式
            current_time = datetime.strptime(current_time_str, '%H:%M:%S %f')
        except ValueError:
            try:
                # 尝试解析为 "HH:MM:SS" 格式
                current_time = datetime.strptime(current_time_str, '%H:%M:%S')
            except ValueError:
                # 如果解析失败，跳过这一行
                time_differences.append(None)
                continue
        
        # 如果是第一行，设置为基准时间
        if base_time is None:
            base_time = current_time
            time_diff = 0.0
        else:
            # 计算与基准时间的时间差（以秒为单位）
            time_diff = (current_time - base_time).total_seconds()
        
        time_differences.append(time_diff)
    
    # 创建一个新的DataFrame，只包含时间和时间差两列
    result_df = pd.DataFrame({
        'Time(Sec)': df['Time(Sec)'],
        'Time Difference (s)': time_differences
    })
    
    # 将结果保存到新的Excel文件
    result_df.to_excel(output_excel_path, index=False)
    print(f"时间差计算完成，结果已保存到: {output_excel_path}")

if __name__ == "__main__":
    # 输入和输出文件路径
    input_excel_path = r'E:\\Dr\\728-aluminum-alloy\\In-situ mechanics\\TEM\\20250309-Al-2.6Mg\\20250309_input_data.xlsx'
    output_excel_path = r'E:\\Dr\\728-aluminum-alloy\\In-situ mechanics\\TEM\\20250309-Al-2.6Mg\\20250309_time_differences.xlsx'
    
    # 计算时间差并保存结果
    calculate_time_differences(input_excel_path, output_excel_path)