import ollama
import threading
import time
import json
import csv
import matplotlib.pyplot as plt
import pandas as pd
import psutil
import pynvml
from datetime import datetime
plt.rcParams['font.sans-serif'] = ['SimHei']  # 或 ['Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号 '-' 显示为方块的问题

# 测试配置
MODEL_NAME = "deepseek-r1:32b"  # 要测试的模型
TEST_DURATION = 600                # 测试时长(秒)
CONCURRENT_THREADS = 8             # 并发线程数
PROMPT_FILE = "D:\\hework\\debug\\prompts.txt"        # 提示词文件
OUTPUT_PREFIX = f"ollama_stress_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
TEMPERATURE = 0.7
MAX_TOKENS = 512

# 全局统计
stats = {
    "start_time": time.time(),
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0,
    "total_tokens": 0,
    "total_latency": 0.0,
    "request_history": [],
    "system_stats": []
}

# 初始化GPU监控
pynvml.nvmlInit()
gpu_handle = pynvml.nvmlDeviceGetHandleByIndex(0)

def get_system_stats():
    """获取系统资源使用情况"""
    # CPU使用率
    cpu_percent = psutil.cpu_percent()
    
    # 内存使用
    mem = psutil.virtual_memory()
    
    # GPU使用
    gpu_util = pynvml.nvmlDeviceGetUtilizationRates(gpu_handle).gpu
    gpu_mem_info = pynvml.nvmlDeviceGetMemoryInfo(gpu_handle)
    gpu_mem_percent = (gpu_mem_info.used / gpu_mem_info.total) * 100
    gpu_temp = pynvml.nvmlDeviceGetTemperature(gpu_handle, pynvml.NVML_TEMPERATURE_GPU)
    
    return {
        "timestamp": datetime.now().isoformat(),
        "cpu_percent": cpu_percent,
        "mem_percent": mem.percent,
        "mem_used_gb": mem.used / (1024 ** 3),
        "gpu_util": gpu_util,
        "gpu_mem_percent": gpu_mem_percent,
        "gpu_temp": gpu_temp
    }

def load_prompts():
    """加载提示词文件"""
    try:
        with open(PROMPT_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        print(f"提示词文件 {PROMPT_FILE} 未找到，使用默认提示")
        return [
            "解释量子计算的基本原理",
            "用Python实现快速排序算法",
            "写一篇关于人工智能未来发展的短文",
            "如何优化深度学习模型的训练速度?",
            "比较RESTful API和GraphQL的优缺点"
        ]

def worker(worker_id, prompts):
    """压力测试工作线程"""
    prompt_index = 0
    while time.time() - stats["start_time"] < TEST_DURATION:
        prompt = prompts[prompt_index % len(prompts)]
        prompt_index += 1
        
        try:
            start_time = time.time()
            
            # 发送模型请求
            response = ollama.generate(
                model=MODEL_NAME,
                prompt=prompt,
                options={
                    "temperature": TEMPERATURE,
                    "num_predict": MAX_TOKENS
                }
            )
            
            latency = time.time() - start_time
            tokens_generated = len(response["response"].split())
            
            # 更新统计
            with threading.Lock():
                stats["total_requests"] += 1
                stats["successful_requests"] += 1
                stats["total_tokens"] += tokens_generated
                stats["total_latency"] += latency
                
                stats["request_history"].append({
                    "timestamp": datetime.now().isoformat(),
                    "worker_id": worker_id,
                    "prompt": prompt[:50] + "..." if len(prompt) > 50 else prompt,
                    "latency": latency,
                    "tokens": tokens_generated,
                    "success": True
                })
                
        except Exception as e:
            with threading.Lock():
                stats["total_requests"] += 1
                stats["failed_requests"] += 1
                stats["request_history"].append({
                    "timestamp": datetime.now().isoformat(),
                    "worker_id": worker_id,
                    "prompt": prompt[:50] + "..." if len(prompt) > 50 else prompt,
                    "error": str(e),
                    "success": False
                })

def monitor():
    """系统监控线程"""
    while time.time() - stats["start_time"] < TEST_DURATION:
        time.sleep(5)
        with threading.Lock():
            stats["system_stats"].append(get_system_stats())

def reporter():
    """实时报告线程"""
    start_time = stats["start_time"]
    last_tokens = 0
    last_requests = 0
    
    while time.time() - start_time < TEST_DURATION:
        time.sleep(10)
        elapsed = time.time() - start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        
        with threading.Lock():
            current_tokens = stats["total_tokens"]
            current_requests = stats["successful_requests"]
            
            # 计算当前区间TPS和RPS
            interval_tokens = current_tokens - last_tokens
            interval_requests = current_requests - last_requests
            tps = interval_tokens / 10
            rps = interval_requests / 10
            
            last_tokens = current_tokens
            last_requests = current_requests
            
            # 获取最新的系统状态
            if stats["system_stats"]:
                sys_stat = stats["system_stats"][-1]
                gpu_temp = sys_stat["gpu_temp"]
                gpu_util = sys_stat["gpu_util"]
                gpu_mem = sys_stat["gpu_mem_percent"]
            else:
                gpu_temp = gpu_util = gpu_mem = 0
            
            print(
                f"[{minutes:02d}:{seconds:02d}] "
                f"Req: {stats['successful_requests']}/{stats['total_requests']} "
                f"(失败: {stats['failed_requests']}) | "
                f"TPS: {tps:.1f} | "
                f"RPS: {rps:.1f} | "
                f"延迟: { 0 if stats['successful_requests'] == 0 else (stats['total_latency']/stats['successful_requests'])*1000:.1f}ms |"
                f"GPU: {gpu_util}%/{gpu_temp}°C | "
                f"显存: {gpu_mem:.1f}%"
            )

def save_results():
    """保存测试结果"""
    # 保存请求历史
    with open(f"{OUTPUT_PREFIX}_requests.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "worker_id", "prompt", "latency", "tokens", "success", "error"])
        writer.writeheader()
        writer.writerows(stats["request_history"])
    
    # 保存系统状态
    with open(f"{OUTPUT_PREFIX}_system.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=stats["system_stats"][0].keys())
        writer.writeheader()
        writer.writerows(stats["system_stats"])
    
    # 保存汇总报告
    total_time = TEST_DURATION
    avg_tps = stats["total_tokens"] / total_time
    avg_rps = stats["successful_requests"] / total_time
    avg_latency = (stats["total_latency"] / stats["successful_requests"]) * 1000 if stats["successful_requests"] > 0 else 0
    success_rate = (stats["successful_requests"] / stats["total_requests"]) * 100 if stats["total_requests"] > 0 else 0
    
    report = {
        "model": MODEL_NAME,
        "test_duration": TEST_DURATION,
        "concurrent_threads": CONCURRENT_THREADS,
        "start_time": datetime.fromtimestamp(stats["start_time"]).isoformat(),
        "end_time": datetime.now().isoformat(),
        "total_requests": stats["total_requests"],
        "successful_requests": stats["successful_requests"],
        "failed_requests": stats["failed_requests"],
        "success_rate": f"{success_rate:.2f}%",
        "total_tokens": stats["total_tokens"],
        "avg_tps": f"{avg_tps:.2f}",
        "avg_rps": f"{avg_rps:.2f}",
        "avg_latency_ms": f"{avg_latency:.1f}",
        "max_gpu_temp": max(s["gpu_temp"] for s in stats["system_stats"]),
        "max_gpu_util": max(s["gpu_util"] for s in stats["system_stats"]),
        "max_gpu_mem": max(s["gpu_mem_percent"] for s in stats["system_stats"])
    }
    
    with open(f"{OUTPUT_PREFIX}_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    return report

def generate_visual_report(report):
    """生成可视化报告"""
    # 读取数据
    requests_df = pd.read_csv(f"{OUTPUT_PREFIX}_requests.csv")
    system_df = pd.read_csv(f"{OUTPUT_PREFIX}_system.csv")
    
    # 转换时间戳
    requests_df["timestamp"] = pd.to_datetime(requests_df["timestamp"])
    system_df["timestamp"] = pd.to_datetime(system_df["timestamp"])
    
    # 设置时间索引
    requests_df.set_index("timestamp", inplace=True)
    system_df.set_index("timestamp", inplace=True)
    
    # 创建图表
    plt.figure(figsize=(15, 12))
    
    # TPS 图表
    plt.subplot(3, 1, 1)
    requests_df["tokens"].resample("10S").sum().plot(label="Tokens/10s")
    plt.ylabel("Tokens")
    plt.title(f"Ollama 压力测试报告 - {MODEL_NAME}\n平均TPS: {report['avg_tps']} | 平均延迟: {report['avg_latency_ms']}ms")
    plt.legend()
    plt.grid(True)
    
    # 请求成功率图表
    plt.subplot(3, 1, 2)
    requests_df["success"].resample("10S").mean().plot(label="成功率", color="green")
    plt.axhline(y=0.95, color="r", linestyle="--", label="95%警戒线")
    plt.ylabel("成功率")
    plt.ylim(0.7, 1.05)
    plt.legend()
    plt.grid(True)
    
    # 系统资源图表
    plt.subplot(3, 1, 3)
    system_df["gpu_util"].plot(label="GPU利用率", color="blue")
    system_df["gpu_temp"].plot(label="GPU温度", secondary_y=True, color="red")
    plt.axhline(y=85, color="r", linestyle="--", label="温度警戒线")
    plt.ylabel("利用率 (%)")
    plt.xlabel("时间")
    plt.legend(loc="upper left")
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_PREFIX}_report.png", dpi=150)

def main():
    # 加载提示词
    prompts = load_prompts()
    print(f"✅ 已加载 {len(prompts)} 条提示词")
    
    # 启动工作线程
    threads = []
    for i in range(CONCURRENT_THREADS):
        t = threading.Thread(target=worker, args=(i, prompts))
        t.start()
        threads.append(t)
    
    # 启动监控和报告线程
    threading.Thread(target=monitor, daemon=True).start()
    threading.Thread(target=reporter, daemon=True).start()
    
    # 显示测试信息
    print(f"🚀 开始压力测试: {CONCURRENT_THREADS}线程, 持续{TEST_DURATION//60}分钟")
    print(f"模型: {MODEL_NAME}")
    print("-" * 80)
    
    # 等待测试结束
    time.sleep(TEST_DURATION)
    
    # 保存结果
    print("\n📊 测试完成，保存结果...")
    report = save_results()
    
    # 生成可视化报告
    generate_visual_report(report)
    print(f"📈 报告已生成: {OUTPUT_PREFIX}_report.png")
    
    # 打印摘要
    print("\n" + "=" * 80)
    print(f"模型: {report['model']}")
    print(f"持续时间: {report['test_duration']}秒")
    print(f"并发数: {report['concurrent_threads']}")
    print(f"总请求数: {report['total_requests']} (成功: {report['successful_requests']}, 失败: {report['failed_requests']})")
    print(f"成功率: {report['success_rate']}")
    print(f"总Token数: {report['total_tokens']}")
    print(f"平均TPS: {report['avg_tps']}")
    print(f"平均RPS: {report['avg_rps']}")
    print(f"平均延迟: {report['avg_latency_ms']}ms")
    print(f"最大GPU温度: {report['max_gpu_temp']}°C")
    print(f"最大GPU利用率: {report['max_gpu_util']}%")
    print(f"最大显存使用率: {report['max_gpu_mem']}%")
    print("=" * 80)

if __name__ == "__main__":
    main()