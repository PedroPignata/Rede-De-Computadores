# Usa uma imagem leve do Python
FROM python:3.9-slim

# Define a pasta de trabalho dentro do container
WORKDIR /app

# Instala ferramentas básicas de rede (ping e curl) para debug
RUN apt-get update && apt-get install -y iputils-ping curl

# Copia a lista de ferramentas e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o seu código para dentro do container
COPY . .

# Comando para rodar o aplicativo quando o container ligar
CMD ["python", "app.py"]