pip install ollama pandas matplotlib psutil pynvml

# 创建提示词文件
echo "解释量子计算的基本原理" >> prompts.txt
echo "用Python实现快速排序算法" >> prompts.txt
echo "写一篇关于人工智能未来发展的短文" >> prompts.txt
echo "如何优化深度学习模型的训练速度?" >> prompts.txt
echo "比较RESTful API和GraphQL的优缺点" >> prompts.txt

# 确保Ollama服务运行
ollama serve