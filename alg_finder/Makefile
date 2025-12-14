all:
	gcc -O3 alg_finder2.c hash_table.c queue.c -lm

run: all
	./a.out

time: all
	time ./a.out

time2:
	gcc -O3 alg_finder.c hash_table.c  -lm
	time ./a.out

clean:
	rm a.out
