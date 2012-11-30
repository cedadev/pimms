# This windows batch file executes the necessary setup for the questionnaire

# only do this in testing
del sqlite.db

# reset the model in sql storage
python manage.py syncdb --noinput

# initialise questionnaire values
python setupQn.py