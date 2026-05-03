MAX_TARGET_DEPTH = 7
BIN_DIR = ../bin
BIN_NAME = alg_finder
FILES = alg_finder.c hash_table.c queue.c

all: $(FILES) | $(BIN)
	gcc -O3 -DMAX_TARGET_DEPTH=$(MAX_TARGET_DEPTH) $(FILES) -lm -o $(BIN_DIR)/$(BIN_NAME)

run: all
	$(BIN_DIR)/$(BIN_NAME) test.in

time: all
	/bin/time -v $(BIN_DIR)/$(BIN_NAME) test.in

profile: | $(BIN)
	gcc -O3 -pg alg_finder.c hash_table.c queue.c -lm -o $(BIN_DIR)/$(BIN_NAME)
	./alg_finder test.in
	gprof alg_finder | batcat

clean:
	rm $(BIN_DIR)/$(BIN_NAME)
	rmdir $(BIN_DIR)

$(BIN_DIR):
	mkdir ../bin
