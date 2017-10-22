import bz2
import logging
import multiprocessing
import os
import subprocess

import gensim
import pkg_resources
from gensim.corpora import WikiCorpus
from gensim.models.word2vec import Word2Vec

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

    working_dir = os.getcwd()
    prefix = 'wiki_nl_'
    threads = multiprocessing.cpu_count() * 2
    result_folder = pkg_resources.resource_filename('resources', 'results')
    dump_name = 'nlwiki-20170920-pages-articles.xml.bz2'
    wiki_dump_url = 'https://dumps.wikimedia.org/nlwiki/20170920/nlwiki-20170920-pages-articles.xml.bz2'
    saved_model_name = pkg_resources.resource_filename('resources', 'word2vec.model')

    if not pkg_resources.resource_exists('resources', dump_name):
        print('Please provide a wiki dump. For example {}'.format(wiki_dump_url))
        raise FileNotFoundError('No wiki dump found')
    wiki_dump = pkg_resources.resource_filename('resources', dump_name)

    corpus_generated = False

    for dirpath, dirnames, files in os.walk(result_folder):
        if files:
            corpus_generated = True
        else:
            os.makedirs(result_folder)

    if not corpus_generated:
        subprocess.run(['python', '-m', 'gensim.scripts.make_wiki', wiki_dump, result_folder])

    bz2_file = bz2.BZ2File('{}/{}wordids.txt.bz2'.format(result_folder, prefix))
    id2word = gensim.corpora.Dictionary.load_from_text(bz2_file)
    sentences = WikiCorpus(wiki_dump, dictionary=id2word).get_texts()

    model = Word2Vec(size=200, window=5, min_count=10, workers=threads)
    model.build_vocab(sentences)
    model.train(sentences, total_examples=model.corpus_count, epochs=model.iter)
    model.save(saved_model_name)
