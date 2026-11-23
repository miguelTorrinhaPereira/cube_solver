MAX_TARGET_DEPTH = 7
BIN_DIR = ../bin
BIN_NAME = alg_finder
FILES = alg_finder.c hash_table.c queue.c turn_data.c
CCFLAGS = -march=native -lm -mavx512f -mavx512bw -mavx512vl
TEST_FILE = ../test.in

all: $(FILES) | $(BIN_DIR)
	gcc -O3 -DMAX_TARGET_DEPTH=$(MAX_TARGET_DEPTH) $(FILES) $(CCFLAGS)  -o $(BIN_DIR)/$(BIN_NAME)

run: all
	$(BIN_DIR)/$(BIN_NAME) test.in

time: all
	/bin/time -v $(BIN_DIR)/$(BIN_NAME) $(TEST_FILE)

debug:
	gcc -O0 -g -fno-inline -DMAX_TARGET_DEPTH=$(MAX_TARGET_DEPTH) $(FILES) $(CCFLAGS) -o $(BIN_DIR)/$(BIN_NAME)

profile: | $(BIN_DIR)
	gcc -O2 -g -fno-inline -DMAX_TARGET_DEPTH=$(MAX_TARGET_DEPTH) $(FILES) $(CCFLAGS) -o $(BIN_DIR)/$(BIN_NAME)
	gprofng collect app -o run.er ../bin/alg_finder $(TEST_FILE)
	gprofng display text run.er

clean:
	rm $(BIN_DIR)/$(BIN_NAME)
	rmdir $(BIN_DIR)

$(BIN_DIR):
	mkdir ../bin
