MAX_TARGET_DEPTH = 7
BIN_DIR = ../bin
BIN_NAME = alg_finder
FILES = alg_finder.c hash_table.c queue.c turn_data.c

all: $(FILES) | $(BIN_DIR)
	gcc -O3  -DMAX_TARGET_DEPTH=$(MAX_TARGET_DEPTH) $(FILES) -lm -o $(BIN_DIR)/$(BIN_NAME)

run: all
	$(BIN_DIR)/$(BIN_NAME) test.in

time: all
	/bin/time -v $(BIN_DIR)/$(BIN_NAME) test.in

debug:
	gcc -O0 -g -DMAX_TARGET_DEPTH=$(MAX_TARGET_DEPTH) $(FILES) -lm -o $(BIN_DIR)/$(BIN_NAME)

profile: | $(BIN_DIR)
	gcc -O3 -pg DMAX_TARGET_DEPTH=$(MAX_TARGET_DEPTH) $(FILES) -lm -o $(BIN_DIR)/$(BIN_NAME)
	./alg_finder test.in
	gprof alg_finder | batcat

clean:
	rm $(BIN_DIR)/$(BIN_NAME)
	rmdir $(BIN_DIR)

$(BIN_DIR):
	mkdir ../bin
