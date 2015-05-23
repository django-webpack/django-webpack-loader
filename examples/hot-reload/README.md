## Usage

Setup virtualenv (optional)
```bash
virtualenv ve
. ve/bin/activate
```

Install dependencies
```bash
pip install -r requirements.txt
npm install
```

Run django server
```bash
./manage.py runserver
```

Run webpack dev server
```bash
node server.js
```

Now you can make changes to `assets/js/app.jsx` and the changes will show up in the browser automagically.
