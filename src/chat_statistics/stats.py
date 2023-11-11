import json
import pathlib as Path
import matplotlib.pyplot as plt
from collections import Counter
from loguru import logger

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
        logger.info('Chat statistics created!')
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

        # calculate users values
        self.__calculate_Q_and_msg()
        self.__calculate_A_and_reply()
        self.__calculate_QandA()

    
    def __calculate_Q_and_msg(self):
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

    def __calculate_A_and_reply(self):
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

    def __calculate_QandA(self):
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

    def __write_file(self, q_a, output_dir, file_name):
        """ writing in a file
        Args:
            q_a (dict): Q&A dictionary of chat
            output_dir (Path): Path of the file to save Q&A
            file_name (string): name of the file
        """
        write_q = False
        with open(str(output_dir / file_name), 'w') as f:
            for q in q_a:
                if len(q_a[q]) != 0: 
                    f.write('Question:\n'+ q + '\n')
                    write_q = True
                for i, a in enumerate(q_a[q]):
                    f.write(f'Answer {i+1}:\n' + a + '\n')
                if write_q:
                    f.write('-'*50 + '\n')
                    write_q = False


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
        """
        Args:
            output_dir (Path): Path to store the file
        """
        self.__write_file(self.q_a ,output_dir, 'Q&A.txt')
            
    def specific_QandA_file(self, output_dir,*args):
        """ generate a Q&A file with specific words in questions
        Args:
            output_dir (Path): Path to store the file
            args (string): specific words
        """
        new_q_a = {}
        for q, a in self.q_a.items():
            if len(self.q_a[q]) == 0:
                continue
            for key_word in args:
                if key_word.lower() not in q.lower():
                    continue
                new_q_a[q] = a
        self.__write_file(new_q_a, output_dir, 'specific_Q&A.txt')


    def generate_word_cloud(self, output_dir):
        """generates a word cloud from a chat data

        Args:
            output_dir : path tp output directory for word cloud image
        """
        logger.info('generating word cloud...')
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

    # generating word cloud
    chat_stats.generate_word_cloud(DATA_DIR)

    # write top 10 in a file
    m_r = chat_stats.most_replier(10)
    m_t = chat_stats.most_talkative(10)
    with open(str(DATA_DIR / 'Top 10.txt'), 'w') as f:
        f.write('Top 10 repliers in chat:\n')
        for user in m_r:
            f.write(str(user) + '\n')
        f.write("-"*50 + '\n')
        f.write('Top 10 talkative people in chat:\n')
        for user in m_t:
            f.write(str(user) + '\n')

    # generating Q&A files
    logger.info('writing Q&As in file...')
    chat_stats.generate_QandA_file(DATA_DIR)
    chat_stats.specific_QandA_file(DATA_DIR, 'there')
    logger.info('Done!')
        
