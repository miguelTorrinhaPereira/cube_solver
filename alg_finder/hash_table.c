//TODO: improve atomic exchange memory ordering
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdatomic.h>

#include "hash_table.h"


// hash function constants
#define HASH_SEED 0x9747b28c
#define HASH_MULT_FACTOR 0x5bd1e995
#define HASH_SHIFT_FACTOR 15


/**
	Biggest power of two that fits into a uint32_t int.
	Works even if int is 16 bits.
*/
#define MAX_POWER_OF_2 ((~0U) ^ (~0U >> 1))

#define MAX_LOAD_FACTOR 1.0F
#define MIN_LOAD_FACTOR 0.25F
#define RESIZING_FACTOR 2



/**
	@brief Calculates the hash of a string (a key).

	Based on the murmurOAAT hash function.
	@param str the string to be hashed.

	@return the hash of the string.
*/
static uint32_t hash_function(uint8_t *key) {
	uint32_t h = HASH_SEED;

	uint8_t *end = key + STATE_SIZE;
	for (; key < end; key++) {
		h ^= *key;
		h *= HASH_MULT_FACTOR;
		h ^= h >> HASH_SHIFT_FACTOR;
	}

	return h;
}


/**
	@brief Calculates the index of a key given its hash.

	@param hash the hash of a key.
	@param capacity the capacity of the hash table.

	@return the index were the key with the given hash belongs.

*/
static inline uint32_t get_index(uint32_t hash, uint32_t capacity) {
	// capacity is always a power of two,
	// so this is equivalent to h % capacity but 10 times faster
	return hash & (capacity - 1);
}


static int keys_equal(uint8_t *key1, uint8_t *key2) {
	uint32_t *p1 = (uint32_t *) key1, *p2 = (uint32_t *) key2;
	uint32_t *end = (uint32_t *)(key1 + STATE_SIZE);

	while(p1 < end)
		if(*p1++ != *p2++)
			return 0;

	return 1;
}


/**
	@brief Inserts an already created entry into a hash table.

	@param table the table of a hash table, it may not belong to a hash table.
	@param capacity the capacity (or size) of the table.
	@param new_entry a pointer to the entry to be inserted.
*/
static int insert_entry(Hash_table hash_table, HT_entry *new_entry) {
	uint32_t index = get_index(new_entry->hash, hash_table->capacity);
	HT_entry *entry = hash_table->table[index], *next;

	if(entry == NULL && atomic_compare_exchange_strong(&hash_table->table[index], &entry, new_entry))
		return 0;

	next = entry->next;
	while(1) {
		if(new_entry->hash == entry->hash && keys_equal(new_entry->key, entry->key))
			return 1;  // entry already exists

		if(next == NULL && atomic_compare_exchange_strong(&entry->next, &next, new_entry))
			break;

		entry = next;
		next = entry->next;
	}

	return 0;
}


/**
	@brief Creates a new hash table.

	@param capacity the initial capacity of the hash table.

	@return a pointer to the new hash table, NULL if it couldn't be create.
*/
Hash_table create_hash_table(uint32_t capacity) {
	Hash_table hash_table;
	uint32_t old_capacity;
	// capacity must be a power of two.
	// this if check if it is a power of two by seeing if it is different
	// from it's less significant bit that is one
	if (capacity != (capacity&-capacity)) {
		// if capacity isn't a power of two,
		// it changes to the smallest power of two that
		// fits in an int variable that is equal or greater than it.
		old_capacity = capacity;
		capacity = 1;
		while (capacity < old_capacity && capacity < MAX_POWER_OF_2)
			capacity <<= 1;
	}

	hash_table = malloc(sizeof(Hash_table));
	if (hash_table == NULL)
		return NULL;

	hash_table->capacity = capacity;
	hash_table->count = 0;
	hash_table->table = (_Atomic(HT_entry *)*) calloc(capacity, sizeof(HT_entry *));

	if (hash_table->table == NULL)
		return NULL;

	return hash_table;
}


/**
	@brief Resizes a hash table.

	@param hash_table the hash table to be resized.
	@param new_capacity the new capacity for the hash table.
*/
void resize_hash_table(Hash_table hash_table, uint32_t new_capacity) {
	Hash_table new_hash_table;
	HT_entry *current = first_entry(hash_table), *next;

	// Should never give an error because of lack of memory,
	// since the hash table is still functional.

	new_hash_table = create_hash_table(new_capacity);
	if (new_hash_table == NULL)
		return;

	while (current != NULL) {
		next = next_entry(hash_table, current);
		insert_entry(new_hash_table, current);
		current = next;
	}

	free(hash_table->table);
	hash_table->table = new_hash_table->table;
	hash_table->capacity = new_hash_table->capacity;
	free(new_hash_table);
}


/**
	@brief Deletes all entries of the hash table.

	It has 2 deletion modes:
	- CLEAR: only deletes the entries.
	- DELETE: also deletes the hash table itself.

	@param hash_table the hash table.
	@param mode the deletion mode to be used.
*/
void delete_hash_table(Hash_table hash_table, Deletion_mode mode) {
	HT_entry *current = first_entry(hash_table), *next;

	while (current != NULL) {
		next = next_entry(hash_table, current);
		free(current);
		current = next;
	}

	if (mode == DELETE) {
		free(hash_table->table);
		free(hash_table);
	}
	else {  // CLEAR
		hash_table->count = 0;
		// the pointers of the table must be set to NULL,
		// since the entries no longer exist
		memset(hash_table->table, 0, hash_table->capacity * sizeof(void *));
	}
}


/**
	@brief Calculates the load factor of a hash table.

	@param hash_table the hash table.

	@return the load factor of the hash table.
*/
static inline float load_factor(Hash_table hash_table) {
	return (float) hash_table->count / hash_table->capacity;
}


/**
	@brief Inserts a new key value pair in a hash table.

	@param hash_table the hash table were the new entry will be inserted.
	@param key the key of the new entry.
	@param value the value of the new entry.

	@return 1 if the new entry couldn't be created, 0 otherwise.
*/
int insert_ht(Hash_table hash_table, uint8_t *key, uint32_t value) {
	HT_entry *new_entry = (HT_entry *) malloc(sizeof(HT_entry));
	if (new_entry == NULL)
		return 1;

	memcpy(new_entry->key, key, STATE_SIZE);
	new_entry->value = value;
	new_entry->hash = hash_function(key);

	if(insert_entry(hash_table, new_entry)) {
		free(new_entry);
		return 2;  // already exists
	}

	hash_table->count++;
	// doesn't work with paralelism without expensive locks
	// if (load_factor(hash_table) > MAX_LOAD_FACTOR)
	// 	resize_hash_table(hash_table, hash_table->capacity * RESIZING_FACTOR);

	return 0;
}


/**
	@brief Removes an entry from a hash table.

	In PURGE mode, the value of the entry is freed.
	In CLEAR and DELETE mode only deletes the entry itself.

	@param hash_table the hash_table.
	@param key the key of the entry to be removed.
	@param mode the deletion mode to be used.

	@return 1 if no entry with the provided key exists, 0 otherwise.
*/
int remove_by_key(Hash_table hash_table, uint8_t *key, Deletion_mode mode) {
	uint32_t hash = hash_function(key);
	uint32_t index = get_index(hash, hash_table->capacity);
	HT_entry *previous, *curr = hash_table->table[index];

	if (curr == NULL) // there isn't a single entry with this index
		return 1;

	if(hash == curr->hash && keys_equal(key, curr->key))  // is it the first entry?
		hash_table->table[index] = curr->next;
	else {  // cycles to the remaining entries
		do {  // the first entry has already been checked
			previous = curr;
			curr = curr->next;

			if(curr == NULL)
				return 1;
		} while (hash != curr->hash || !keys_equal(key, curr->key));

		previous->next = curr->next;
	}

	free(curr);

	hash_table->count--;
	// doesn't work with paralelism without expensive locks
	// if (load_factor(hash_table) < MIN_LOAD_FACTOR)
	// 	resize_hash_table(hash_table, hash_table->capacity / RESIZING_FACTOR);

	return 0;
}


/**
	@brief Finds the entry of a hash table that has a given key.

	@param hash_table the hash_table.
	@param key the key.

	@return a pointer to the entry, NULL if no entry with the key exists.
*/
static HT_entry *get_entry(Hash_table hash_table, uint8_t *key) {
	uint32_t hash = hash_function(key);
	uint32_t index = get_index(hash, hash_table->capacity);
	HT_entry *entry = hash_table->table[index];

	for (; entry != NULL; entry = entry->next)
		if (hash == entry->hash && keys_equal(key, entry->key))
			return entry;

	return NULL;
}


/**
	@brief Gets the value associated with a key in a hash_table.

	@param hash_table the hash table.
	@param key the key.
*/
uint32_t get_value(Hash_table hash_table, uint8_t *key) {
	HT_entry *entry = get_entry(hash_table, key);
	if (entry == NULL)
		return 0;

	return entry->value;
}


/**
	@brief Determines if a given key exists in a hash table.

	@param hash_table the hash table.
	@param key the key.

	@return 1 if the key exists, 0 if it doesn't.
*/
int exists_key(Hash_table hash_table, uint8_t *key) {
	return get_entry(hash_table, key) != NULL;
}


/**
	@brief Changes the value associated with a given key of a hash table.

	@param hash_table the hash table.
	@param key the key associated with the value that will be changed.
	@param new_value the new value.

	@return 0 if the key exists, 1 if it doesn't.
*/
int change_entry(Hash_table hash_table, uint8_t *key, uint32_t new_value) {
	HT_entry *entry = get_entry(hash_table, key);
	if (entry == NULL)
		return 1;

	entry->value = new_value;
	return 0;
}


/**
	@brief Returns the first entry of a hash table.

	The order of the entries of the hash table doesn't have any meaning.

	@param hash_table the hash table.

	@return a pointer to the first entry of the hash table,
		or NULL if it is empty.
*/
HT_entry *first_entry(Hash_table hash_table) {
	return next_entry(hash_table, NULL);
}


/**
	@brief Returns the entry of a hash table that is after a given entry.

	The order of the entries of the hash table doesn't have any meaning.

	@param hash_table the hash table.
	@param entry an entry of the hash table.

	@return the next entry, or NULL if there isn't a next entry.
*/
HT_entry *next_entry(Hash_table hash_table, HT_entry *entry) {
	uint32_t index;
	if (entry == NULL)
		index = 0;
	else if (entry->next == NULL)
		index = get_index(entry->hash, hash_table->capacity) + 1;
	else
		return entry->next;

	for (; index < hash_table->capacity; index++)
		if (hash_table->table[index] != NULL)
			return hash_table->table[index];

	return NULL;
}


uint32_t get_hash_table_count(Hash_table hash_table) {
	return hash_table->count;
}


uint32_t get_hash_table_capacity(Hash_table hash_table) {
	return hash_table->capacity;
}
