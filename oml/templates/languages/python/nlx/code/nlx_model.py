"""
DO NOT EDIT UNLESS YOU KNOW WHAT YOU'RE DOING

The class is auto-generated from saved template. Implement your
code in OModel class that extends this base class.

Base abstract class for NLX team. This class provides common
functions across different models within NLX team.
"""

from abc import abstractmethod
from os.path import join
from nltk.tokenize import word_tokenize
import numpy as np

from . import BaseModel
from .settings import SEQ_LEN, UNK_CHAR, VALIDATION_FILE_NAME, VOCAB_FILE_NAME


class NLXModel(BaseModel):

    def __init__(self, data_dirpath):
        super().__init__(data_dirpath)

        self.query_dict = self.generate_vocab_map(join(self.data_dirpath, VOCAB_FILE_NAME))
        self.validation_data = join(self.data_dirpath, VALIDATION_FILE_NAME)
        self.vocab_size = len(self.query_dict)

    def generate_vocab_map(self, vocab_path):
        """
        Simple function to create a python dictionary to map input
        and labels to their corresponding IDs.

        :param vocab_path: Vocab path containing all the words in the input sentences
        :return: Dictionary (Map) from word in input vocabulary to corresponding ID
        """
        query_wl = [line.strip() for line in open(vocab_path, encoding='utf-8', mode='r')]
        query_dict = {query_wl[i]: i for i in range(len(query_wl))}
        print('Common vocab loaded.')
        return query_dict

    def get_ids(self, seq):
        """
        Run a sequence through and get the ids for the sequence

        :param seq: word sequence
        :return: the ids for the sequence
        """
        ids = []
        for tok in seq:
            if tok in self.query_dict.keys():
                ids.append(self.query_dict[tok])
            else:
                ids.append(UNK_CHAR)
        return ids

    def generate_onehot(self, data):
        seq = word_tokenize(data)

        w = self.get_ids(seq)  # convert to word indices
        onehot = np.zeros([len(w), len(self.query_dict)], np.float32)
        for t in range(len(w)):
            onehot[t, w[t]] = 1
        return onehot

    def generate_batches(self):
        x_batch, y_batch, batch_lengths = [], [], []

        for x, y, line_seqlen in self.get_dynamic_line(self.validation_data, SEQ_LEN):
            x_batch.append(x)
            y_batch.append(y)
            batch_lengths.append(line_seqlen)
            yield (np.asarray(x_batch), np.asarray(y_batch), np.asarray(batch_lengths))

    def get_dynamic_line(self, filename, seqlen):
        with open(filename, 'r') as f:
            line_count = 0
            for line in f:
                line_count += 1
                line_split = line.strip().split('\t')
                sentence = line_split[0].strip().split(' ')
                labels = line_split[1].strip().split(' ')
                sentence = [self.get_ids(w) for w in sentence]
                labels = [int(label) for label in labels]
                if len(sentence) > seqlen:
                    sentence = sentence[: seqlen]
                    labels = labels[: seqlen]
                x_line, y_line = sentence, labels
                yield x_line, y_line, len(x_line)

    @abstractmethod
    def predict(self, data):
        pass

    @abstractmethod
    def eval(self, **kwargs):
        pass
