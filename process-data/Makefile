.PHONY=all clean clean-all status up run

# Force make to run targets sequentially
.NOTPARALLEL:

# Directory containing this makefile. Includes trailing slash
MAKEFILE_PATH=$(dir $(realpath $(firstword $(MAKEFILE_LIST))))

all: run

clean:
	$(info Clean)
	./run --docker-compose-down

clean-all:
	$(info Clean All)
	./run --clean-all
	echo "Remove Docker resources and Spark metastore & warehouse files"
	cd ./spark/scripts/test && sudo rm -rf ./metastore_db ./derby.log ./spark-warehouse
	cd ./spark/scripts && sudo rm -rf ./metastore_db ./derby.log ./spark-warehouse
	echo "Remove Postgresql database files"
	cd ./postgresql && sudo rm -rf ./pg_data

status:
	$(info Show docker status)
	./run --status

up:
	$(info Running docker-compose up)
	./run --docker-compose-up

run-spark: up
	$(info Running spark initial load job)
	./run -i

run-postgresql: up
	$(info Running postgres setup)
	./run -g

run: run-spark run-postgresql
