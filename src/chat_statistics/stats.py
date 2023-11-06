import json
import pathlib as Path
import matplotlib.pyplot as plt
from collections import Counter

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

        # generate users profile
        names = set()
        for msg in self.chat_data['messages']:
            if msg['type'] != 'message':
                continue
            names.add((msg['from_id'], msg['from']))
        self.users = dict()
        for id_, name in names:
            self.users[id_] = {
                'name':name,
                'Q':0,
                'A':0,
                'msg':0,
                'reply':0,
            }

        # generate Question & Answer dict
        self.q_a = {}

    
    def calculate_Q_and_msg(self):
        """
        calculate the value of Q and msg in users profile
        """
        for user in self.users.keys():
            for msg in self.chat_data['messages']:
                if msg['type'] != 'message':
                    continue
                if msg['from_id'] == user:
                    self.users[user]['msg'] += 1
                if '?' in msg['text'] or '؟' in msg['text']:
                    self.users[user]['Q'] += 1
                    self.q_a[msg['text']] = []

    
    def calculate_A_and_reply(self):
        """
        calculate the value of A and reply in users profile
        """
        for i, msg in enumerate(self.chat_data['messages']):
            if msg['type'] != 'message':
                continue
            try:
                msg_id = msg['id']
                reply_msg_id = msg["reply_to_message_id"]
                diff = msg_id - reply_msg_id
                text = self.chat_data['messages'][i-diff]['text']
                if '?' in text or '؟' in text:
                    self.users[msg['from_id']]['A'] += 1
            except KeyError as ke:
                continue
            except IndexError as ie:
                continue


    def most_talkative(self, n=10):
        """ calculate the most n talkative users in chat
        must first run 2 define methods

        Args:
            n (int): top {n} 

        Returns:
            list: list of top n talkative users with their id and name and number of their messages
        """
        msgs_from = [] 
        for msg in self.chat_data['messages']:
            if msg['type'] != 'message':
                continue
            msgs_from.append(msg['from_id'])
        top_n = Counter(msgs_from).most_common(n)
        new_top_n = []
        for id_, num in top_n:
            new_top_n.append((id_, self.users[id_]['name'], num))
        return new_top_n


    def most_replier(self, n=10):
        """calculate the most n replier users in chat
        must first run 2 define methods

        Args:
            n (int): top {n} 

        Returns:
            list: list of top n replier users with their id and name and number of their messages
        """
        msgs_reply = []
        for msg in self.chat_data['messages']:
            if msg['type'] != 'message':
                continue
            try:
                _ = msg["reply_to_message_id"]
                msgs_reply.append(msg['from_id'])
            except KeyError as ke:
                continue
        top_n = Counter(msgs_reply).most_common(n)
        new_top_n = []
        for id_, num in top_n:
            new_top_n.append((id_, self.users[id_]['name'], num))
        return new_top_n


    def generate_QandA_file(self, output_dir):
        """ write all of questions and their answers in a text file

        Args:
            output_dir (Path): path of text file 
        """
        for i, msg in enumerate(self.chat_data['messages']):
            if msg['type'] != 'message':
                continue
            try:
                msg_id = msg['id']
                reply_msg_id = msg["reply_to_message_id"]
                diff = msg_id - reply_msg_id
                A = self.chat_data['messages'][i]['text']
                Q = self.chat_data['messages'][i-diff]['text']
                if isinstance(A, str) and isinstance(Q, str) and Q in self.q_a:
                    self.q_a[Q].append(A)
            except KeyError as ke:
                continue
            except IndexError as ie:
                continue

        # write Q&As in a file 
        with open(str(output_dir / 'Q&A.txt'), 'w') as f:
            for q in self.q_a:
                f.write('Question:\n'+ q + '\n')
                for i, a in enumerate(self.q_a[q]):
                    f.write(f'Answer {i+1}:\n' + a + '\n')
                f.write('-'*50 + '\n')
            

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
    # example to check code
    chat_stats = ChatStatistics(Chat_json=DATA_DIR / "groupChat.json")
    chat_stats.generate_word_cloud(DATA_DIR)
    chat_stats.calculate_Q_and_msg()
    chat_stats.calculate_A_and_reply()
    m_r = chat_stats.most_replier()
    print(m_r)  
    print('-'*50)
    m_t = chat_stats.most_talkative()
    print(m_t)
    print('-'*50)
    chat_stats.generate_QandA_file(DATA_DIR)
    print("Done!")
        
