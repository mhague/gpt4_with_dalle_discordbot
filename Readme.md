# GPT-4 with DALL-E Discord Bot

This is a Discord chat bot that utilizes OpenAI's GPT-4 and DALL-E APIs to answer questions and generate related images. The bot can be used in Discord servers to make conversations more interactive and engaging.

## Features

- Answer questions using OpenAI's GPT-4 API.
- Generate related images using DALL-E API, crafting the prompt with some simple fine-tuning using zero shot classifiers.
- Provide a summary of the question and answer.
- Provide a caption for the image.
- Estimate the cost of each API call.

## Requirements

- Python 3.9
- Docker and Docker Compose
- An OpenAI API key
- A Discord bot token

## Installation

1. Clone the repository:

```
git clone https://github.com/mhague/gpt4_with_dalle_discordbot.git
```

2. Change directory to the project folder:

```
cd gpt4_with_dalle_discordbot
```

3. Create a `.env` file in the project folder and add the following environment variables:

```
DISCORD_TOKEN=your_discord_bot_token
OPENAI_API_KEY=your_openai_api_key
VERSION=1.0.0
NAME=Oscar
```

Replace `your_discord_bot_token` and `your_openai_api_key` with your Discord bot token and OpenAI API key, respectively. You can also update the `VERSION` and `NAME` variables if needed.

4. Build and run the bot using Docker:

```
docker-compose up --build -d
```

## Usage

Once the bot is running and connected to your Discord server, you can interact with it using the `ask` command followed by your question:

```
/ask question: write a 2 paragraph story about a hero named Oscar

```
![image](https://user-images.githubusercontent.com/5944910/229381358-0a5d6c71-6a3d-4ae3-ac63-5ab249ab53ff.png)

The bot will respond with an answer, a related image (if possible), an image descriptor, and a summary of the question.

## Customization

You can customize the bot's behavior by modifying the settings in the `modules/chat_tools.py` file, such as the engines used for classification and chat, the image size, and other parameters.
