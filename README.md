## In name of Allah

This project is a bundle of 5 different services which are explained thoroughly in documentation. Here we will review how to run codebase.

To run project, first you have to install the requirements:
```
pip install -r requirements.txt
```

Then you need to apply the migrations on your db:
```
python manage.py makemigrations
```
and
```
python manage.py migrate
```

Now create a directory named "keys" alongside project.

At the end run the below command:
```
python manage.py runserver_plus --key-file ../keys/ca.key --cert-file ../keys/ca.crt 8090
```

Now you are ready to use the project.

To initiate CA, call init request ("https://127.0.0.1:8090/ca/init") and you are good to go as the doc instructs!
