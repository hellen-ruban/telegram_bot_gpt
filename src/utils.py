from src.settings.config import PATH_TO_RESOURCES

def load_messages_for_bot(name:str) -> str:
    with open(PATH_TO_RESOURCES/ "messages" / f"{name}.txt", encoding="utf-8") as file:
        return file.read()
