docker build -t server-local .

docker run -p 5000:5000 --env-file=.env server-local 
