from openai import AzureOpenAI

client = AzureOpenAI(
    azure_endpoint="https://muvan-o1-mini.openai.azure.com/",
    api_version="2024-12-01-preview",
    api_key="50bU6AQnSEuu3mA4kEYLb9neDods1UmAzK3zwYPCp8SR7RNTQlbyJQQJ99ALACHYHv6XJ3w3AAABACOGnNKS"
)


response = client.chat.completions.create(
    model="gpt-4.1-2",
    messages=[{"role": "user", "content": "tell me what is an allergen"}],
    temperature=0.1,
    max_tokens=20
)
print(response.choices[0].message.content)
