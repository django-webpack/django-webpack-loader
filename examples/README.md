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

Run webpack compiler

```bash
npx webpack --mode=development --watch
```
