#ifndef _QUEUE_H
#define _QUEUE_H

#include <stdbool.h>


typedef struct Queue_entry{
	void *value;
	struct Queue_entry *_Atomic next;
} Queue_entry;

typedef struct {
	Queue_entry *_Atomic head;
	Queue_entry *_Atomic tail;
} _Queue;

typedef _Queue *Queue;


Queue create_queue();
void delete_queue(Queue queue);
int push_queue(Queue queue, void *value);
void *pop_queue(Queue queue);

#endif
