COMPOSE=fades -d 'docker-compose' -x docker-compose

build:
	$(COMPOSE) build

bootstrap:
	$(COMPOSE) run --rm --entrypoint bash web /app/scripts/bootstrap.sh

run:
	$(COMPOSE) up

stop:
	$(COMPOSE) stop

clean:
	$(COMPOSE) rm -f

dump:
	$(COMPOSE) exec database mysqldump -unerdhelp -pnerdhelp nerdhelp

shell:
	$(COMPOSE) run --rm web python manage.py shell
