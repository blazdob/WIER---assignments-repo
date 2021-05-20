# install anaconda dependencies into proper environment
`conda install nltk`

# navigate to implementation-indexing folder when running any of the following programs

# run boostrap.py program that downloads nltk data before running any other programs
`python bootstrap.py`

# run indexing
`python run-indexing.py`

# run search
- search with sqlite index (need to run indexing first): `python run-sqlite-search.py "QUERY"`
- search without index: `python run-basic-search.py "QUERY"`

# number of results and snippets
To change number of results and number of snippets, change `NUM_RESULTS` and `NUM_SNIPPETS`
constants in processing module respectively.