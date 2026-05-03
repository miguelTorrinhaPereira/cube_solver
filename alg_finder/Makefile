MAX_TARGET_DEPTH = 7

all:
	gcc -O3 -DMAX_TARGET_DEPTH=$(MAX_TARGET_DEPTH) alg_finder.c hash_table.c queue.c -lm -o alg_finder

run: all
	./alg_finder test.in

time: all
	/bin/time -v ./alg_finder test.in

profile:
	gcc -O1 -pg alg_finder.c hash_table.c queue.c -lm -o alg_finder
	./alg_finder test.in 
	gprof alg_finder | batcat

clean:
	rm alg_finder*
