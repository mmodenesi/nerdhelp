until python /app/manage.py migrate; do
    echo "Waiting for mysql server to be available...";
    sleep 1;
done

python /app/manage.py createsuperuser
