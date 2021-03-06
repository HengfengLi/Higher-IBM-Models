from __future__  import division
from collections import defaultdict
from nltk.align  import AlignedSent
from nltk.align  import Alignment
from nltk.corpus import comtrans

class IBMModel1(object):
    """
    This class implements the algorithm of Expectation Maximization for 
    the IBM Model 1. 

    Step 1 - Collect the evidence of a English word being translated by a 
             foreign language word.

    Step 2 - Estimate the probability of translation according to the 
             evidence from Step 1. 

    >>> bitexts = comtrans.aligned_sents()[:100]
    >>> ibm = IBMModel1(bitexts, 20)

    >>> aligned_sent = ibm.align(bitexts[6])
    >>> aligned_sent.alignment
    Alignment([(0, 0), (1, 1), (2, 2), (3, 7), (4, 7), (5, 8)])
    >>> bitexts[6].precision(aligned_sent)
    0.5555555555555556
    >>> bitexts[6].recall(aligned_sent)
    0.8333333333333334
    >>> bitexts[6].alignment_error_rate(aligned_sent)
    0.33333333333333337
    
    """
    def __init__(self, alignSents, num_iter):
        self.probabilities = self.train(alignSents, num_iter)

    def train(self, alignSents, num_iter):
        """
        Return the translation probability model trained by IBM model 1. 

        Arguments:
        alignSents   -- A list of instances of AlignedSent class, which 
                        contains sentence pairs. 
        num_iter     -- The number of iterations.

        Returns:
        t_ef         -- A dictionary of translation probabilities. 
        """

        # Vocabulary of each language
        fr_vocab = set()
        en_vocab = set()
        for alignSent in alignSents:
            en_vocab.update(alignSent.words)
            fr_vocab.update(alignSent.mots)
        # Add the Null token
        fr_vocab.add(None)

        # Initial probability
        init_prob = 1 / len(en_vocab)

        # Create the translation model with initial probability
        t_ef = defaultdict(lambda: defaultdict(lambda: init_prob))

        total_e = defaultdict(lambda: 0.0)

        for i in range(0, num_iter):
            count_ef = defaultdict(lambda: defaultdict(lambda: 0.0))
            total_f = defaultdict(lambda: 0.0)

            for alignSent in alignSents:
                en_set = alignSent.words
                fr_set = [None] + alignSent.mots  

                # Compute normalization
                for e in en_set:
                    total_e[e] = 0.0
                    for f in fr_set:
                        total_e[e] += t_ef[e][f]

                # Collect counts
                for e in en_set:
                    for f in fr_set:
                        c = t_ef[e][f] / total_e[e]
                        count_ef[e][f] += c
                        total_f[f] += c

            # Compute the estimate probabilities
            for f in fr_vocab:
                for e in en_vocab:
                    t_ef[e][f] = count_ef[e][f] / total_f[f]

        return t_ef

    def align(self, alignSent):
        """
        Returns the alignment result for one sentence pair. 
        """

        if self.probabilities is None:
            raise ValueError("The model does not train.")

        alignment = []

        for j, en_word in enumerate(alignSent.words):
            
            # Initialize the maximum probability with Null token
            max_alignProb = (self.probabilities[en_word][None], None)
            for i, fr_word in enumerate(alignSent.mots):
                # Find out the maximum probability
                max_alignProb = max(max_alignProb,
                    (self.probabilities[en_word][fr_word], i))

            # If the maximum probability is not Null token,
            # then append it to the alignment. 
            if max_alignProb[1] is not None:
                alignment.append((j, max_alignProb[1]))

        return AlignedSent(alignSent.words, alignSent.mots, alignment)

# run doctests
if __name__ == "__main__":
    import doctest
    doctest.testmod()
