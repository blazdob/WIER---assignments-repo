# install anaconda dependencies into proper environment
`conda install nltk`

# run boostrap.py program that downloads nltk data before any other programs
`python bootstrap.py`

# running indexing
- navigate to `implementation-indexing` folder
- run `python run-indexing.py`

# running search
- search with sqlite index: `python run-sqlite-search.py "QUERY"`
- search without index: `python run-basic-search.py "QUERY"`