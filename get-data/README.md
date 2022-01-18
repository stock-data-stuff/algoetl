# Goal
Fetch data and store it in the feed-history directory.

# Usage
Run the code using something like the following:
make START=2022-01-08 END=2022-01-20

If the START and END are omitted, the code will run with default values
as defined in the Makefile.

# Details
- For each feed defined in the configuration file, 
  this creates a directory under .../algoetl/feed-history
- The feed-history directory can be a symlink to another directory. 
  It is ignored by git.

See the Makefile for more details.


