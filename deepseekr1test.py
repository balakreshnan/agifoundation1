# pip install azure-ai-inference
import os
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

# Load .env file
load_dotenv()

api_key = os.getenv("AZURE_INFERENCE_CREDENTIAL", '')
if not api_key:
  raise Exception("A key should be provided to invoke the endpoint")

client = ChatCompletionsClient(
    endpoint='https://DeepSeek-R1-ep.eastus2.models.ai.azure.com',
    credential=AzureKeyCredential(api_key)
)

model_info = client.get_model_info()
print("Model name:", model_info.model_name)
print("Model type:", model_info.model_type)
print("Model provider name:", model_info.model_provider_name)

payload = {
  "messages": [
    {
      "role": "user",
      "content": "what to know more about scientific theory, can you explain it?"
    },
    {
      "role": "assistant",
      "content": "A scientific theory is a well-substantiated explanation of a natural phenomenon, based on a body of empirical evidence that has been repeatedly confirmed through observation and experimentation. Unlike a hypothesis or a guess, a theory provides a comprehensive framework that explains and predicts phenomena in a reliable way. It must be testable, falsifiable, and subject to revision if new evidence contradicts it. A strong theory has broad explanatory scope and predictive power, making accurate forecasts about future observations. Examples include the Theory of Evolution, which explains species changes over time through natural selection; General Relativity, which describes how gravity affects space and time; and Quantum Mechanics, which governs atomic and subatomic behavior. Unlike scientific laws, which describe relationships (e.g., Newton’s Laws of Motion), theories explain why and how those laws work, often incorporating them as special cases."
    },
    {
      "role": "user",
      "content": "Invent a new scientific theory that explains both dark matter and consciousness.?"
    }
  ],
  "max_tokens": 2048
}
response = client.complete(payload)

print("Response:", response.choices[0].message.content)
print("Model:", response.model)
print("Usage:")
print("	Prompt tokens:", response.usage.prompt_tokens)
print("	Total tokens:", response.usage.total_tokens)
print("	Completion tokens:", response.usage.completion_tokens)