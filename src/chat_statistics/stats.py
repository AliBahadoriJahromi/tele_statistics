import json
import pathlib as Path
import matplotlib.pyplot as plt

from src.data import DATA_DIR
from wordcloud import WordCloud


class ChatStatistics:
    """
    generates chat statistics from a telegram chat json file
    """
    def __init__(self, Chat_json):
        """
        Args:
            Chat_json : path to telegram export json file
        """
        # load chat data
        with open(Chat_json) as f:
            self.chat_data = json.load(f)

    def generate_word_cloud(self, output_dir):
        """generates a word cloud from a chat data

        Args:
            output_dir : path tp output directory for word cloud image
        """
        # getting text messages
        text_content = ''
        for msg in self.chat_data['messages']:
            if isinstance(msg['text'] ,str):
                text_content += f" {msg['text']}"

        # generate wordcloud
        wordcloud = WordCloud(
            width=1200,height=1200,
            background_color='black'
        ).generate(text_content)

        # save wordcloud to a file in data
        wordcloud.to_file(str(output_dir / 'wordcloud.png'))


if __name__ == "__main__":
    chat_stats = ChatStatistics(Chat_json=DATA_DIR / "groupChat.json")
    chat_stats.generate_word_cloud(DATA_DIR)
    print("Done!")
        
