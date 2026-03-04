all:
	gcc -O3 alg_finder2.c hash_table.c queue.c -lm -o alg_finder2

run: all
	./alg_finder2 test.in

time: all
	time ./alg_finder2 test.in

time2:
	gcc -O3 alg_finder.c hash_table.c  -lm -o alg_finder1
	time ./alg_finder1

clean:
	rm alg_finder*
