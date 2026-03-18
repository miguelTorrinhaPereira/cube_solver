all:
	gcc -O3 alg_finder2.c hash_table.c queue.c -lm -o alg_finder2

run: all
	./alg_finder2 test.in

time: all
	/bin/time -v ./alg_finder2 test.in

profile:
	gcc -O1 -pg alg_finder2.c hash_table.c queue.c -lm -o alg_finder2
	./alg_finder2 test.in 
	gprof alg_finder2 | batcat

clean:
	rm alg_finder*
