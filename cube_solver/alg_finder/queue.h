#ifndef _QUEUE_H
#define _QUEUE_H

#include <pthread.h>


typedef struct Queue_entry{
	const void *value;
	struct Queue_entry *_Atomic next;
} Queue_entry;

typedef struct {
	Queue_entry *_Atomic head;
	Queue_entry *_Atomic tail;
	pthread_mutex_t lock;
} _Queue;

typedef _Queue *Queue;


Queue create_queue();
void delete_queue(Queue queue);
static bool is_queue_empty(Queue queue);
int push(Queue queue, const void *value);
void *pop(Queue queue);

#endif
