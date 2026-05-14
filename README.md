# Python autotests for db lessons

Landing:

http://web.mahenzon.ru/


## How To

### Write code

Copy-paste full `tasks` folder to your new project and rename it to `solutions`.

Run `uv sync` once to install the `solutions` package to make it discoverable by pytest.


### Run tests


**Minimal run:**

```shell
uv run \
  --with "py-db-autotests@git+https://github.com/mahenzon/breakthrough-db-autotests.git" \
  pytest --pyargs testing
```

#### Recipes

**With coverage:**


```shell
uv run \
  --with "py-db-autotests@git+https://github.com/mahenzon/breakthrough-db-autotests.git" \
  pytest --pyargs testing \
    --cov=solutions \
    --cov-report=term-missing \
    --cov-report=html
```


**For SQLite only:**

```shell
uv run \
  --with "py-db-autotests@git+https://github.com/mahenzon/breakthrough-db-autotests.git" \
  pytest --pyargs testing -m sqlite
```

**For SQLite + coverage:**

```shell
uv run \
  --with "py-db-autotests@git+https://github.com/mahenzon/breakthrough-db-autotests.git" \
  pytest --pyargs testing -m sqlite \
    --cov=solutions \
    --cov-report=term-missing \
    --cov-report=html
```
