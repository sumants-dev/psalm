dev:
	uvicorn main:app --reload
gen:
	sqlc generate
migration:
	goose create $(name) sql --dir migrations
up:
	goose up
up_by_one:
	goose 
down_by_one:
	goose postgres $(database_url) down
