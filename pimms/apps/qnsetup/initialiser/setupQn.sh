# This shell script executes the necessary setup for the questionnaire

# comment out the following line for deployment
# source ~/proj/metafor/venv/bin/activate
#source ~/meta4q/bin/activate 

# only do this in testing
rm -f sqlite.db

# reset the model in sql storage
${PYTHON:-python} manage.py syncdb --noinput

# initialise questionnaire values
${PYTHON:-python} setupQn.py
