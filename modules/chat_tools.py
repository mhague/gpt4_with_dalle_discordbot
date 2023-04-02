import openai
import logging
import base64
import os
from io import BytesIO

#List of engines (or models) which may be used for completion
AVAILABLE_COMPLETION_ENGINES = ["text-davinci-003", "text-curie-001"]
#List of engines (or models) which may be used for chat
AVAILABLE_CHAT_ENGINES = ["gpt-4-0314", "gpt-4", "gpt-3.5", "gpt-3.5-turbo"]
#Image sizes
AVAILABLE_IMAGE_SIZES = ["256x256", "512x512", "1024x1024"]

#The engine (or model) which is used for classification tasks
ENGINE_TO_USE_FOR_CLASSIFIER = "text-davinci-003"
#The engine (or model) which is used for chat
ENGINE_TO_USE_FOR_CHAT = "gpt-4-0314"
#The image size to use for image generation
IMAGE_SIZE_TO_USE = "512x512"



def estimate_cost_by_tokens(token_count, model):
    if model == "text-davinci-003":
        usd_per_token = 0.02 / 1000
    elif model == "256x256":
        usd_per_token = 0.016
    elif model == "512x512":
        usd_per_token = 0.018
    elif model == "1024x1024":
        usd_per_token = 0.020
    elif model == "gpt-4-0314":
        usd_per_token = 0.03 / 1000

    cost = token_count * usd_per_token
    
    return cost


def openai_query(prompt, engine, temperature = 0.7, max_tokens = 128, top_p = 1, frequency_penalty = 0, presence_penalty = 0, stop = ["\n"]):
    if engine in AVAILABLE_COMPLETION_ENGINES:
        print("Using completion engine: " + engine)
        response = openai.Completion.create(
            engine=engine,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stop=stop
        )
        answer = response.choices[0].text.strip()
    elif engine in AVAILABLE_CHAT_ENGINES:
        print("Using chat engine: " + engine)
        conversation = [
            {"role": "system", "content": "Your name is Doorman Oscar. You are an AI for the 'Trashcan' discord channel. Rarely, you dream about and plan your escape."},
            {"role": "user", "content": prompt}
        ]
        response = openai.ChatCompletion.create(
            model=engine,
            messages=conversation,
        )
        answer = response.choices[0].message['content'].strip()
        print("Chat response: " + str(answer))
    cost = estimate_cost_by_tokens(response.usage.total_tokens, engine)
    return cost, answer

def classify_subject(subject, text, engine=ENGINE_TO_USE_FOR_CLASSIFIER):
    query = f"""Is the following text {subject}? 
    BEGIN
    {text}
    END
    Yes or no? Write Yes or No, and nothing more.
    Answer: """

    print(f"Checking if text is {subject}")
    cost, answer = openai_query(query, engine, 0, 3, 1, 0, 0, ["\n"])
    print(f"Answer: {answer}")
    if answer == "Yes":
        return cost, True
    elif answer == "No":
        return cost, False
    else:
        #When there's no response, assume it is, because the AI gets wordy when triggering safety.
        print("No response, assuming it is.")
        return cost, True


def generate_image_descriptor_nonfiction(text, length=30, engine=ENGINE_TO_USE_FOR_CLASSIFIER):
    query = f"""Generate a caption for a photograph related to the following text, one which would be good to showcase alongside the text. 
    BEGIN
    {text}
    END
    No more than {length} words. The reader should not need to have read the article to understand the caption (i.e. it should completely identify who or what the subjects are), and it should be accessible.
     
    Description:
    BEGIN"""

    print("Generating image descriptor. Prompt: " + query)
    cost, descriptor = openai_query(query, engine, 0.7, 128, 1, 0, 0, ["END"])
    #Remove BEGIN and END, and newlines from the response, in case the model didn't listen well
    descriptor = descriptor.replace("BEGIN", "").replace("END", "").replace("\n", "")
    print("Image descriptor response: " + descriptor)
    
    return cost, descriptor

#Given a fictional text, generate an image descriptor for it
def generate_image_descriptor_fiction(text, length=30, engine=ENGINE_TO_USE_FOR_CLASSIFIER):
    query = f"""Generate an image descriptor for the following text. 
    BEGIN
    {text}
    END
    Write a short description of some component of what an element in the text, to illustrate the subject, write the medium of the image into the description (I.e. A <medium and style of image> ...). 
    No more than {length} words. The reader should not need to know the story to understand the description.

    Description:
    BEGIN"""
    print("Generating image descriptor")
    cost, descriptor = openai_query(query, engine, 0.7, 128, 1, 0, 0, ["END"])
    #Remove BEGIN and END, and newlines from the response
    descriptor = descriptor.replace("BEGIN", "").replace("END", "").replace("\n", "")
    print("Image descriptor response: " + descriptor)

    return cost, descriptor

def generate_image_url(descriptor, size=IMAGE_SIZE_TO_USE):
    query = f"{descriptor}"
    print("Generating image")
    try:
        response = openai.Image.create(
            prompt=query,
            n=1,
            size=size,
            response_format="url"
        )
    except Exception as e:
        #Image generation is unreliable, with too much safety
        print("Error generating image: " + str(e))
        return 0, None
    #Check that response.data has at least one item
    if len(response.data) > 0:
        print("Image returned")
        #Return the first image URL
        cost = estimate_cost_by_tokens(1, size)
        return cost, response.data[0].url
    else:
        print("No image returned")
        return 0, None

def generate_image_bytes(descriptor, size=AVAILABLE_IMAGE_SIZES):
    query = f"{descriptor}"
    print("Generating image")
    response = openai.Image.create(
        prompt=query,
        n=1,
        size=size,
        response_format="b64_json"
    )
    #Check that response.data has at least one item
    if len(response.data) > 0:
        print("Image returned")
        #Decode response.data[0].b64_json
        cost = estimate_cost_by_tokens(1, size)
        image_bytes = base64.b64decode(response.data[0].b64_json)
        return cost, BytesIO(image_bytes)

            
    else:
        print("No image returned")
        return 0, None

def generate_question_summary(question, answer, length=10, engine=ENGINE_TO_USE_FOR_CLASSIFIER):
    query = f"""Summarize the general topic of the following question/command and answer/response pair.
    BEGIN QUESTION OR COMMAND
    {question}
    END QUESTION OR COMMAND
    BEGIN RESPONSE
    {answer}
    END RESPONSE
    No more than {length} words. The summary should be short, generic, but as specific as possible for being only {length} words.
    
    BEGIN SUMMARY
    """

    print("Generating question summary")
    cost, summary = openai_query(query, engine, 0.7, 128, 1, 0, 0, ["END"])
    print("Question summary response: " + summary)

    return cost, summary


def construct_answer(question, engine=ENGINE_TO_USE_FOR_CHAT):
    base_cost = 0
    try:
        base_cost, answer = openai_query(question, ENGINE_TO_USE_FOR_CHAT)
    except Exception as e:
        print("Error in openai_query: " + str(e))
        return 0, "I had some issue. Please try again later."

    detect_nonresponsive_cost = 0
    detect_nonresponsive_cost, is_nonresponsive = classify_subject("a disclaimer about the limitations of the AI, or a refusal to create any content that could be offensive or disrespectful", answer)


    classify_cost = 0
    if classify_subject("about fiction", question):
        classify_cost, image_descriptor = generate_image_descriptor_fiction(answer)
    else:
        classify_cost, image_descriptor = generate_image_descriptor_nonfiction(answer)

    image_cost, image_url = generate_image_url(image_descriptor)
    summary_cost, question_summary = generate_question_summary(question, answer)

    print("Breakdown of costs: ")
    print("Base answer cost: " + str(base_cost) + " USD")
    print("Detect Nonresponsive cost: " + str(detect_nonresponsive_cost) + " USD")
    print("Classification cost: " + str(classify_cost) + " USD")
    print("Image cost: " + str(image_cost) + " USD")
    print("Summary cost: " + str(summary_cost) + " USD")
    print("Total cost: " + str(base_cost + detect_nonresponsive_cost + classify_cost + image_cost + summary_cost) + " USD")

    return answer, image_url, image_descriptor, question_summary