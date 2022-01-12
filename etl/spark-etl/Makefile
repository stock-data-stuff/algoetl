.PHONY=all clean clean-all login status pyspark up run

# Force make to run targets sequentially
.NOTPARALLEL:

# Directory containing this makefile. Includes trailing /
MAKEFILE_PATH=$(dir $(realpath $(firstword $(MAKEFILE_LIST))))

all: run

clean:
	$(info Clean)
	./run -d

# Remove Docker resources and Spark metastore & warehouse files
clean-all:
	$(info Clean All)
	./run -c
	cd ./scripts && rm -rf ./metastore_db ./derby.log ./spark-warehouse

status:
	$(info Show docker status)
	./run -s

up:
	$(info Running docker-compose up)
	./run -u

login: up
	$(info Log into master node)
	./run -l

pyspark: up
	$(info Run Pyspark on master node)
	./run -p

run: up
	$(info Run the initial load)
	sleep 4
	./run -i

