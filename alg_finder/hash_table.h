/** @file hash_table.h

	@brief Header of hash_table.c.

	@author ist1113667 (Miguel Torrinha)
*/

#ifndef _HASH_TABLE_H
#define _HASH_TABLE_H

#include <stdint.h>

/**  @struct HT_entry
	@brief A hash table entry.

	@var HT_entry::key
	the key of the entry.
	@var HT_entry::value
	the value associated with the key.
	@var HT_entry::hash
	the hash of the key. 
	Unnecessary, but makes the hash table 25% faster.
	@var HT_entry::next
	a pointer to the next entry.
*/
typedef struct HT_entry {
	char *key;
	void *value;
	uint32_t hash;
	struct HT_entry *next;
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
	uint32_t count;
	HT_entry **table;
} Hash_table;


/** @enum Deletion_mode
	@brief Used to control how much is deleted in the `delete_hash_table`
	and `remove_by_key` functions.

	See the documentation of this functions for more details.
*/
typedef enum { CLEAR, DELETE ,PURGE } Deletion_mode;


Hash_table *create_hash_table(uint32_t capacity);
void resize_hash_table(Hash_table *hash_table, uint32_t new_capacity);
void delete_hash_table(Hash_table *hash_table, Deletion_mode mode);

int insert_ht(Hash_table *hash_table, char *key, void *value);
int remove_by_key(Hash_table *hash_table, char *key, Deletion_mode mode);
void *get_value(Hash_table *hash_table, char *key);
int exists_key(Hash_table *hash_table, char *key);
int change_entry(Hash_table *hash_table, char *key, void *new_value);

HT_entry *next_entry(Hash_table *hash_table, HT_entry *entry);
HT_entry *first_entry(Hash_table *hash_table);
#endif
