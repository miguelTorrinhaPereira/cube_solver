#include <pthread.h>
#include <stdlib.h>
#include <stdbool.h>

#include "queue.h"


Queue create_queue() {
	Queue queue = malloc(sizeof(_Queue));
	if(queue == NULL)
		return NULL;

	queue->head = NULL;
	queue->tail = NULL;
	pthread_mutex_init(&queue->lock, NULL);

	return queue;
}


void delete_queue(Queue queue) {
	free(queue);
}


static bool is_queue_empty(Queue queue) {
	return queue->head == NULL;
}


int push_queue(Queue queue, void *value) {
	Queue_entry *new_entry = malloc(sizeof(Queue_entry));
	if(new_entry == NULL)
		return 1;

	new_entry->value = value;
	new_entry->next = NULL;

	pthread_mutex_lock(&queue->lock);
	if(is_queue_empty(queue))
		queue->head = new_entry;
	else
		queue->tail->next = new_entry;
	queue->tail = new_entry;
	pthread_mutex_unlock(&queue->lock);

	return 0;
}


void *pop_queue(Queue queue) {
	if(is_queue_empty(queue))
		return NULL;

	Queue_entry *old_head;
	pthread_mutex_lock(&queue->lock);
	old_head = queue->head;
	queue->head = queue->head->next;
	pthread_mutex_unlock(&queue->lock);

	void *value = old_head->value;
	free(old_head);
	return value;
}
