dev:
	uvicorn api.main:app --reload
gen:
	sqlc generate
migration:
	goose create $(name) sql
up:
	goose up
up_by_one:
	goose 
down_by_one:
	goose down
