dev:
	uvicorn main:app --reload
gen:
	sqlc generate

brew_update:
	brew update

pyenv_install:
	brew install pyenv

pipenv_install:
	brew install pipenv

prereqs: brew_update pyenv_install pipenv_install
	echo "Installed"

python_shell:
	pyenv shell 3.10 && python -m venv .venv && pipenv install

migration:
	goose create $(name) sql --dir migrations
up:
	goose up
up_by_one:
	goose 
down_by_one:
	goose postgres $(database_url) down
