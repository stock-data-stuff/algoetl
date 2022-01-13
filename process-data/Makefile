.PHONY=all clean clean-all status up run

# Force make to run targets sequentially
.NOTPARALLEL:

# Directory containing this makefile. Includes trailing /
MAKEFILE_PATH=$(dir $(realpath $(firstword $(MAKEFILE_LIST))))

all: run

clean:
	$(info Clean)
	./run -d

clean-all:
	$(info Clean All)
	./run -c
	echo "Remove Docker resources and Spark metastore & warehouse files"
	cd ./spark/scripts && sudo rm -rf ./metastore_db ./derby.log ./spark-warehouse
	echo "Remove Postgresql database files"
	cd ./postgresql && sudo rm -rf ./postgres-data

status:
	$(info Show docker status)
	./run -s

up:
	$(info Running docker-compose up)
	./run -u
run: up
	$(info Run the initial load)
	sleep 2
	./run -i
	./run --test-postgresql

