# FitCheck

Fitness coach in your hand.

## UAT Deployment

### Server for deployment

ถ้า RAM ไม่พอบอกให้ขยายขนาดได้นะครับ

```
ssh azureuser@104.43.90.55
```

### API Deployment

Go to the backend branch and pull the latest changes.

```bash
cd ~/fitcheck
git checkout llm-service
git pull
```

Edit API configuration and AZURE API KEY in .env file.

```ENV
GPT35_AZURE_OPEN_AI_URL= # GPT-3.5 API URL
AZURE_OPEN_AI_URL= # GPT-4o or GPT-4o mini API URL
AZURE_OPEN_AI_API_KEY= # Azure AI portal key

## Text to Speech
AZURE_SERVICE_REGION= # Azure service region
AZURE_TEXT_TO_SPEECH= # Azure text to speech endpoint URL
VOICE_STREAM_SIZE= # default size of voice streaming chunk, default is 9600.
```

Deploy backend API in docker-compose.dev.yml

```bash
docker-compose -f docker-compose.dev.yml pull && \
    docker-compose -f docker-compose.dev.yml up -d
```

In case of docker pull failed by authentication, login to [Azure Container Registry](#Secrets) first.

```bash
docker login [login-server]
```

## Try the API

Go to web browser http://104.43.90.55/docs

## Build and push docker image

Build docker image

```bash
docker compose -f docker-compose.dev.yml build
```

Push docker image. Please make sure you login to [Azure Container Registry by `docker login`](https://portal.azure.com/#@dhanabhonoutlook.onmicrosoft.com/resource/subscriptions/e97812df-de44-479e-96e4-e6e88bb8e046/resourcegroups/FitCheck/providers/Microsoft.ContainerRegistry/registries/fitcheckapi/accessKey) or [Azure CLI](https://learn.microsoft.com/en-us/azure/container-registry/container-registry-authentication?tabs=azure-cli) first.

```bash
docker compose -f docker-compose.dev.yml push
```

## Local Development

### Clone repository

```bash
git clone https://github.com/innobyte-ai-dream/fitcheck.git
cd fitcheck

## Checkout to llm-service in remote branch
git switch llm-service
```

### (Optional) Create Python Virtual Environment

```bash
python -m venv venv

# Activate virtual environment
## Windows CMD
venv\Scripts\activate.bat
## Windows PowerShell
venv\Scripts\Activate.ps1
## Linux
source venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run FastAPI server

For development

```bash
fastapi dev backend/app.py
```

For production

```bash
fastapi run backend/app.py
```

## License

[MIT](https://choosealicense.com/licenses/mit/)
