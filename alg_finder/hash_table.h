#ifndef _HASH_TABLE_H
#define _HASH_TABLE_H

#include <stdint.h>
#include <stdatomic.h>


#define STATE_SIZE 20


typedef struct HT_entry {
	uint8_t key[STATE_SIZE];
	uint32_t value;
	uint32_t hash;
	_Atomic(struct HT_entry *) next;
} HT_entry;


/** @struct Hash_table
	@brief A dynamic hash table.

	@var Hash_table::capacity
	the size of the vector `table`.
	@var Hash_table::count
	The number of entries stored in the hash table.
	It is needed to calculate the load factor.
	The load factor is the number of entries divided by the capacity.
	@var Hash_table::table
	a pointer to a vector of size `capacity`
	of pointers to the entries of the hash table.
*/
typedef struct {
	uint32_t capacity;
	_Atomic uint32_t count;
	_Atomic(HT_entry *)*table;
} _Hash_table;

typedef _Hash_table *Hash_table;


/** @enum Deletion_mode
	@brief Used to control how much is deleted in the `delete_hash_table`
	and `remove_by_key` functions.

	See the documentation of this functions for more details.
*/

typedef enum { CLEAR, DELETE } Deletion_mode;

Hash_table create_hash_table(uint32_t capacity);
void resize_hash_table(Hash_table hash_table, uint32_t new_capacity);
void delete_hash_table(Hash_table hash_table, Deletion_mode mode);

int insert_ht(Hash_table hash_table, const uint8_t *key, uint32_t value);
int remove_by_key(Hash_table hash_table, const uint8_t *key, Deletion_mode mode);
uint32_t get_value(Hash_table hash_table, const uint8_t *key);
int change_entry(Hash_table hash_table, const uint8_t *key, uint32_t new_value);

// should be statis, but exists_key is basically a wrapper to this function and it is being calling literally a billion times
HT_entry *get_entry(Hash_table hash_table, const uint8_t *key);
inline int exists_key(Hash_table hash_table, const uint8_t *key) {
	return get_entry(hash_table, key) != NULL;
}

HT_entry *next_entry(Hash_table hash_table, HT_entry *entry);
HT_entry *first_entry(Hash_table hash_table);

uint32_t get_hash_table_count(Hash_table hash_table);
uint32_t get_hash_table_capacity(Hash_table hash_table);
#endif
