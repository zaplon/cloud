ssh doktor.misal.pl <<'ENDSSH'
cd app/frontend
git pull
npm run build
cd ..
git pull
docker-compose stop
docker-compose pull
docker-compose -f production.yml up -d
docker-compose run web ./manage.py migrate
ENDSSH
