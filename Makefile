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
	$(COMPOSE) rm -f -v

dump:
	$(COMPOSE) exec database mysqldump -unerdhelp -p nerdhelp
