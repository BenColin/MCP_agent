import requests
# SiliconFlow 平台的调用示例

# Rerank
url = "https://api.siliconflow.cn/v1/rerank"

payload = {
    "model": "Qwen/Qwen3-Reranker-8B",
    "query": "Apple",
    "documents": ["apple", "banana", "fruit", "vegetable"]
}
headers = {
    "Authorization": "YOUR_SILICONFLOW_API_KEY",
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

print(response.json())



# Embedding
url = "https://api.siliconflow.cn/v1/embeddings"

payload = {
    "model": "Qwen/Qwen3-Embedding-8B",
    "input": "Silicon flow embedding online: fast, affordable, and high-quality embedding services. come try it out!"
}
headers = {
    "Authorization": "YOUR_SILICONFLOW_API_KEY",
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

print(response.json())