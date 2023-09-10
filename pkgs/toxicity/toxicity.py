from profanity_check import predict


def check_toxicity(text: str) -> bool:
    is_toxic = predict([text])[0] == 1
    return is_toxic