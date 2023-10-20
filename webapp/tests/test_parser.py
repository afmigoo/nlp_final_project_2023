import unittest

from pasta_parser._parser import get_text_trigrams
from pasta_parser._data_structures import Token, Trigram

class TestTrigramParser(unittest.TestCase):

    def test_none_trigram(self):
        with self.assertRaises(ValueError):
            _ = Trigram((None, None, None))

    def test_zerogram(self):
        input_text = ','
        output = []
        result = list(get_text_trigrams(input_text))
        self.assertListEqual(output, result)

        input_text = ', : ! ! ! ! !.....---'
        output = []
        result = list(get_text_trigrams(input_text))
        self.assertListEqual(output, result)

    def test_unigram(self):
        input_text = 'падаю'
        out_unigram = Token((0, 5), 'падаю', 'падать', 'verb')
        output = [
            Trigram((None, None, out_unigram)),
            Trigram((None, out_unigram, None)),
            Trigram((out_unigram, None, None))
        ]
        result = list(get_text_trigrams(input_text))
        self.assertListEqual(output, result)

        result = list(get_text_trigrams("падаю!!!! :)"))
        self.assertListEqual(output, result)

    def test_bigram(self):
        input_text = 'падаю столбом'
        token1 = Token((0, 5), 'падаю', 'падать', 'verb')
        token2 = Token((6, 13), 'столбом', 'столб', 'noun')
        output = [
            Trigram((None, None, token1)),
            Trigram((None, token1, token2)),
            Trigram((token1, token2, None)),
            Trigram((token2, None, None)),
        ]
        result = list(get_text_trigrams(input_text))
        self.assertListEqual(output, result)

    def test_trigram(self):
        input_text = 'быстро падаю столбом'
        token1 = Token((0, 6), 'быстро', 'быстро', 'adv')
        token2 = Token((7, 12), 'падаю', 'падать', 'verb')
        token3 = Token((13, 20), 'столбом', 'столб', 'noun')
        output = [
            Trigram((None, None, token1)),
            Trigram((None, token1, token2)),
            Trigram((token1, token2, token3)),
            Trigram((token2, token3, None)),
            Trigram((token3, None, None))
        ]
        result = list(get_text_trigrams(input_text))
        self.assertListEqual(output, result)

        input_text = '- быстро, падаю столбом!!!!'
        token1 = Token((2, 8), 'быстро', 'быстро', 'adv')
        token2 = Token((10, 15), 'падаю', 'падать', 'verb')
        token3 = Token((16, 23), 'столбом', 'столб', 'noun')
        output = [
            Trigram((None, None, token1)),
            Trigram((None, token1, token2)),
            Trigram((token1, token2, token3)),
            Trigram((token2, token3, None)),
            Trigram((token3, None, None))
        ]
        result = list(get_text_trigrams(input_text))
        self.assertListEqual(output, result)

    def test_adp(self):
        input_text = 'у за под в'
        token1 = Token((0, 1), 'у', 'у', 'adp')
        token2 = Token((2, 4), 'за', 'за', 'adp')
        token3 = Token((5, 8), 'под', 'под', 'adp')
        token4 = Token((9, 10), 'в', 'в', 'adp')
        output = [
            Trigram((None, None, token1)),
            Trigram((None, token1, token2)),
            Trigram((token1, token2, token3)),
            Trigram((token2, token3, token4)),
            Trigram((token3, token4, None)),
            Trigram((token4, None, None)),
        ]
        result = list(get_text_trigrams(input_text))
        self.assertListEqual(output, result)

if __name__ == '__main__':
    unittest.main()
