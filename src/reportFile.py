import os

def reportFile(filename: str) -> str:
    """
    生成文件报告，包括文件大小、行数和内容摘要
    
    Parameters:
    filename (str): 要报告的文件路径
    
    Returns:
    str: 包含文件信息的字符串
    
    内容摘要规则：
    - 如果文件行数 ≤ 11：输出全部内容
    - 如果文件行数 > 11：输出前8行和最后3行，中间用'...'省略
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(filename):
            return f"Error: File '{filename}' not found."
        
        # 获取文件大小
        file_size = os.path.getsize(filename)
        
        # 读取文件内容
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        total_lines = len(lines)
        
        # 构建结果字符串
        result = f"File report for: {filename}\n"
        result += "=" * 50 + "\n"
        result += f"File size: {file_size} bytes\n"
        result += f"Total lines: {total_lines}\n"
        result += "-" * 50 + "\n"
        result += "Content summary:\n"
        
        if total_lines == 0:
            result += "(Empty file)\n"
        elif total_lines <= 11:
            # 输出全部内容
            for i, line in enumerate(lines, 1):
                result += f"Line {i:3d}: {line.rstrip()}\n"
        else:
            # 输出前8行
            for i in range(min(8, total_lines)):
                result += f"Line {i+1:3d}: {lines[i].rstrip()}\n"
            result += "...\n"
            # 输出最后3行
            for i in range(-3, 0):
                result += f"Line {total_lines + i + 1:3d}: {lines[i].rstrip()}\n"
        
        result += "=" * 50 + "\n"
        return result
        
    except PermissionError:
        return f"Error: Permission denied when reading file '{filename}'."
    except UnicodeDecodeError:
        return f"Error: Cannot decode file '{filename}' as UTF-8 text."
    except Exception as e:
        return f"Error reading file: {str(e)}"


if __name__ == "__main__":
    # 测试主程序
    import sys
    
    if len(sys.argv) > 1:
        # 使用命令行参数作为文件名
        filename = sys.argv[1]
    else:
        # 如果没有提供参数，使用当前目录下的一个测试文件
        filename = "test_report.txt"
        # 创建一个测试文件
        with open(filename, 'w', encoding='utf-8') as f:
            for i in range(1, 21):
                f.write(f"This is line {i} of the test file.\n")
    
    print("Testing reportFile function:")
    print(reportFile(filename))
