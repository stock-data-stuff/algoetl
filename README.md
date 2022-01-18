# Goal
Fetch each feed defined in the config file into the feed-history directory.
Then process all files in the feed-history directory; then:
- create a table that unifies (denormalizes) all data in the feed-history directory.
- export the denormalized data as a CSV file (in ~/Downloads/)

# Usage
Run the code using something like the following:
make START=2022-01-08 END=2022-01-20

If the START and END are omitted, the code will run with default values
as defined in the Makefile.

See the Makefiles in ./get-data and ./process-data for more details.


