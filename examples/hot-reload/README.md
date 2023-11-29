## Usage

Setup virtualenv (optional)

```bash
python -m venv venv
. venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
npm install
```

Run migrations

```bash
./manage.py migrate
```

Run django server

```bash
./manage.py runserver
```

Run webpack dev server

```bash
npx webpack serve --mode=development --hot
```

Now you can make changes to `assets/js/app.jsx` and the changes will show up in the browser automagically.
