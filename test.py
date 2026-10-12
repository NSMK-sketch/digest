from gigachat import GigaChat

giga = GigaChat(
   base_url="https://api.giga.chat/v1",
   credentials="Токен",
   model="GigaChat-2",
   verify_ssl_certs=False
)

response = giga.chat("Привет! Как дела?")

print(response.choices[0].message.content)