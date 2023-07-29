import random
import json
import torch
from app.chatbot_code.model import NeuralNet
from app.chatbot_code.nltk_utils import bag_of_words, tokenize
import numpy as np
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def get_chatbot_response(user_input):
    with open('app/chatbot_code/intents.json', 'r') as json_data:
        intents = json.load(json_data)

    FILE = "app/chatbot_code/data.pth"
    data = torch.load(FILE)

    input_size = data["input_size"]
    hidden_size = data["hidden_size"]
    output_size = data["output_size"]
    all_words = data['all_words']
    tags = data['tags']
    model_state = data["model_state"]

    model = NeuralNet(input_size, hidden_size, output_size).to(device)
    # model = NeuralNet(input_size, hidden_size, output_size).unsqueeze(0)
    model.load_state_dict(model_state)
    model.eval()


    sentence = tokenize(user_input)
    X = bag_of_words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)
    # X = torch.from_numpy(X).unsqueeze(0)


    output = model(X)
    _, predicted = torch.max(output, dim=1)

    tag = tags[predicted.item()]

    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]
    if prob.item() > 0.80:
        for intent in intents['intents']:
            if tag == intent["tag"]:
                return random.choice(intent['responses'])
    else:
        return "I do not understand..."

# Example usage
# print("Let's chat! (type 'quit' to exit)")
# while True:
#     user_input = input("You: ")
#     if user_input == "quit":
#         break
#     response = get_chatbot_response(user_input)
#     print(f"Sam: {response}")
