import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from numpy.polynomial import Polynomial

# 定义多项式阶数
degree = 9  # 可以根据需要调整阶数

# 读取 Excel 文件
input_file = r'e:\\Dr\\728-aluminum-alloy\\In-situ mechanics\\TEM\\20250309-Al-2.6Mg\\fitting_calculation.xlsx'  # 请替换为你的 Excel 文件名

# 加载数据
df = pd.read_excel(input_file, sheet_name=None)

# 提取 fitting data
fitting_data = df['fitting data']
x_fit = fitting_data['x'].values
y_fit = fitting_data['y'].values

# 多项式拟合
p = Polynomial.fit(x_fit, y_fit, degree)

# 提取 calculation data
calculation_data = df['calculation data']
x_calc = calculation_data['x'].values

# 计算拟合结果
y_calc = p(x_calc)

# 将结果添加到数据框的 y 列
calculation_data['y'] = y_calc

# 保存结果到原始 Excel 文件
with pd.ExcelWriter(input_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    calculation_data.to_excel(writer, sheet_name='calculation data', index=False)

# 可视化结果
plt.figure(figsize=(10, 6))
# 绘制原始数据点
plt.scatter(x_fit, y_fit, color='red', label='Fitting Data', s=50)
# 绘制拟合曲线
x_fit_line = np.linspace(min(x_fit), max(x_fit), 100)
y_fit_line = p(x_fit_line)
plt.plot(x_fit_line, y_fit_line, color='blue', label='Polynomial Fit', linewidth=2)
# 绘制计算结果
plt.scatter(x_calc, y_calc, color='green', label='Calculated Data', s=50)
plt.title('Polynomial Fit and Calculation Results')
plt.xlabel('x')
plt.ylabel('y')
plt.legend()
plt.grid()
plt.savefig('fitting_results.png')  # 保存图像
plt.show()  # 显示图像

print(f"Results saved to {input_file} in 'calculation data' sheet.")

