# Run docker compose file. 
if [[ $1 == up ]]
then
    echo '--> running app on docker' 
    docker-compose -f docker-compose.yml up -d

elif [[ $1 == down ]]
then
    echo '--> closing app on docker' 
    docker-compose -f docker-compose.yml down

elif [[ $1 == build ]]
then
    echo '--> building docker image' 
    docker-compose -f docker-compose.yml build
fi 
