A Django app to view simulation traces (VCD) with a responsive HTML5 interface.

Development
===========

After cloning the repository, create a virtualenv environment, install
the prerequisites, create the database, then run the testsite webapp.

    $ virtualenv-2.7 _installTop_
    $ source _installTop_/bin/activate
    $ pip install -r requirements.txt
    $ python manage.py syncdb
    $ python manage.py runserver

    # Browse http://localhost:8000/

