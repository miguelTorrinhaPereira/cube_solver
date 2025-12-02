#include <stdatomic.h>
#include <stdlib.h>
#include <stdbool.h>

#include "queue.h"

Queue create_queue() {
	Queue queue = malloc(sizeof(_Queue));
	if(queue == NULL)
		return NULL;

	Queue_entry *dummy = malloc(sizeof(Queue_entry));
	if(dummy == NULL) {
		free(queue);
		return NULL;
	}
	dummy->next = NULL;

	queue->head = dummy;
	queue->tail = dummy;

	return queue;
}


void delete_queue(Queue queue) {
	free(queue->head);
	free(queue);
}


int push_queue(Queue queue, void *value) {
	Queue_entry *new_entry = malloc(sizeof(Queue_entry));
	if(new_entry == NULL)
		return 1;

	new_entry->value = value;
	new_entry->next = NULL;

	Queue_entry *old_tail;
	Queue_entry *old_next;
	while(true) {
		old_tail = queue->tail;
		old_next = old_tail->next;

		if(old_next == NULL) {
			if(atomic_compare_exchange_weak(&old_tail->next, &old_next, new_entry)) {
				atomic_compare_exchange_weak(&queue->tail, &old_tail, new_entry);
				break;
			}
		}
		else
			atomic_compare_exchange_weak(&queue->tail, &old_tail, old_next);
	}

	return 0;
}


void *pop_queue(Queue queue) {
	Queue_entry *old_head;
	do {
		if(queue->head->next == NULL)
			return NULL;
		old_head = queue->head;
	} while(!atomic_compare_exchange_weak(&queue->head, &old_head, queue->head->next));

	void *value = old_head->next->value;
	free(old_head);
	return value;
}

