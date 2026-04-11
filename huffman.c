/*
 * Mahmudunnabi Siam
 * ID : 25924388
 * Complete Huffman Compression/Decompression
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>

/* ----- Constants & types ----- */
#define NUM_SYMBOLS 256u
#define COMPOSITE_NODE (-1)
#define BUFFER_SIZE 8192

typedef unsigned long long count_Table;
typedef unsigned char byte_Table;

/* Frequency table structure */
struct frequency_table {
    count_Table freq[NUM_SYMBOLS];
};

/* Huffman tree node */
struct huffman_node {
    int value;
    count_Table freq;
    int level;
    int ignore;
    struct huffman_node* left;
    struct huffman_node* right;
    struct huffman_node* parent;
};

/* Code table for encoding */
struct code_table {
    char code[NUM_SYMBOLS][NUM_SYMBOLS];
    unsigned int length[NUM_SYMBOLS];
};

/* Bit buffer for bit-level I/O */
struct bit_buffer {
    unsigned char buffer;
    int count;
};

/* ----- Function Prototypes ----- */
int initialise_Frequency(struct frequency_table *ft);
int count_Freq(FILE *input, struct frequency_table *ft);
static struct huffman_node *create_leaf_node(int symbol, count_Table freq);
static int find_min_weight(struct huffman_node **pool, unsigned int limit);
static struct huffman_node *merge_tree(struct huffman_node *left, struct huffman_node *right);
static struct huffman_node *build_tree_from_freq(const struct frequency_table *ft);
int build_Tree(const struct frequency_table *ft, struct huffman_node **out_root);
int initialise_code_table(struct code_table *ct);
static void generate_codes_recursive(struct huffman_node *node, struct code_table *ct, 
                                     char *current_code, unsigned int depth);
int generate_codes(struct huffman_node *root, struct code_table *ct);
void print_codes(struct code_table *ct, struct frequency_table *ft);
void free_tree(struct huffman_node *root);

/* Compression/Decompression functions */
int write_frequency_header(FILE *output, struct frequency_table *ft);
int read_frequency_header(FILE *input, struct frequency_table *ft);
int compress_file(const char *input_filename, const char *output_filename);
int decompress_file(const char *input_filename, const char *output_filename);
static void write_bit(FILE *output, int bit, struct bit_buffer *bb);
static void flush_bits(FILE *output, struct bit_buffer *bb);
static int read_bit(FILE *input, struct bit_buffer *bb);

/* ----- Main Function ----- */
int main(int argc, char *argv[]) {
    
    if (argc < 4) {
        printf("Usage:\n");
        printf("  Compress:   %s -c input_file output_file\n", argv[0]);
        printf("  Decompress: %s -d input_file output_file\n", argv[0]);
        return 1;
    }
    
    if (strcmp(argv[1], "-c") == 0) {
        /* Compress */
        printf("Compressing %s to %s...\n", argv[2], argv[3]);
        if (compress_file(argv[2], argv[3]) == 0) {
            printf("Compression successful!\n");
        } else {
            printf("Compression failed!\n");
            return 1;
        }
    } else if (strcmp(argv[1], "-d") == 0) {
        /* Decompress */
        printf("Decompressing %s to %s...\n", argv[2], argv[3]);
        if (decompress_file(argv[2], argv[3]) == 0) {
            printf("Decompression successful!\n");
        } else {
            printf("Decompression failed!\n");
            return 1;
        }
    } else {
        printf("Invalid option. Use -c for compress or -d for decompress.\n");
        return 1;
    }
    
    return 0;
}

/* ----- Frequency Table Functions ----- */

int initialise_Frequency(struct frequency_table *ft) {
    unsigned int i;
    
    if (ft == NULL) {
        return -1;
    }
    
    for (i = 0U; i < NUM_SYMBOLS; i++) {
        ft->freq[i] = 0UL;
    }
    
    return 0;
}

int count_Freq(FILE *input, struct frequency_table *ft) {
    int character;
    
    if (input == NULL || ft == NULL) {
        return -1;
    }
    
    while ((character = fgetc(input)) != EOF) {
        ft->freq[(unsigned char)character]++;
    }
    
    return 0;
}

/* ----- Tree Building Functions ----- */

static struct huffman_node *create_leaf_node(int symbol, count_Table freq) {
    struct huffman_node *node;
    
    node = (struct huffman_node *)malloc(sizeof(struct huffman_node));
    if (node == NULL) {
        return NULL;
    }
    
    node->value = symbol;
    node->freq = freq;
    node->level = 0;
    node->ignore = 0;
    node->left = NULL;
    node->right = NULL;
    node->parent = NULL;
    
    return node;
}

static int find_min_weight(struct huffman_node **pool, unsigned int limit) {
    unsigned int i;
    int min_weight;
    count_Table min_freq;
    int min_level;
    
    min_weight = -1;
    
    for (i = 0U; i < limit; i++) {
        if (pool[i] != NULL && pool[i]->ignore == 0) {
            min_weight = (int)i;
            min_freq = pool[i]->freq;
            min_level = pool[i]->level;
            break;
        }
    }
    
    if (min_weight < 0) {
        return -1;
    }
    
    for (i = (unsigned int)(min_weight + 1); i < limit; i++) {
        if (pool[i] == NULL || pool[i]->ignore != 0) {
            continue;
        }
        if (pool[i]->freq < min_freq ||
            (pool[i]->freq == min_freq && pool[i]->level < min_level)) {
            min_weight = (int)i;
            min_freq = pool[i]->freq;
            min_level = pool[i]->level;
        }
    }
    
    return min_weight;
}

static struct huffman_node *merge_tree(struct huffman_node *left, struct huffman_node *right) {
    int max_level;
    struct huffman_node *parent;
    
    if (left == NULL || right == NULL) {
        return NULL;
    }
    
    parent = (struct huffman_node *)malloc(sizeof(struct huffman_node));
    if (parent == NULL) {
        return NULL;
    }
    
    parent->value = COMPOSITE_NODE;
    parent->freq = left->freq + right->freq;
    
    if (left->level > right->level) {
        max_level = left->level;
    } else {
        max_level = right->level;
    }
    parent->level = max_level + 1;
    
    parent->ignore = 0;
    parent->left = left;
    parent->right = right;
    parent->parent = NULL;
    
    left->parent = parent;
    right->parent = parent;
    left->ignore = 1;
    right->ignore = 1;
    
    return parent;
}

static struct huffman_node *build_tree_from_freq(const struct frequency_table *ft) {
    struct huffman_node *pool[NUM_SYMBOLS * 2];
    unsigned int pool_size = 0;
    unsigned int i;
    struct huffman_node *merged;
    int min1, min2;
    
    if (ft == NULL) {
        return NULL;
    }
    
    for (i = 0U; i < NUM_SYMBOLS; i++) {
        if (ft->freq[i] > 0UL) {
            pool[pool_size] = create_leaf_node((int)i, ft->freq[i]);
            if (pool[pool_size] == NULL) {
                while (pool_size > 0) {
                    free(pool[--pool_size]);
                }
                return NULL;
            }
            pool_size++;
        }
    }
    
    if (pool_size == 0) {
        return NULL;
    }
    if (pool_size == 1) {
        return pool[0];
    }
    
    while (pool_size > 1) {
        min1 = find_min_weight(pool, pool_size);
        if (min1 == -1) {
            break;
        }
        min2 = find_min_weight(pool, pool_size);
        if (min2 == -1) {
            break;
        }
        
        merged = merge_tree(pool[min1], pool[min2]);
        if (merged == NULL) {
            return NULL;
        }
        
        pool[pool_size] = merged;
        pool_size++;
    }
    
    for (i = 0U; i < pool_size; i++) {
        if (pool[i] != NULL && !pool[i]->ignore) {
            return pool[i];
        }
    }
    
    return NULL;
}

int build_Tree(const struct frequency_table *ft, struct huffman_node **out_root) {
    struct huffman_node *root;
    
    if (ft == NULL || out_root == NULL) {
        return -1;
    }
    *out_root = NULL;
    
    root = build_tree_from_freq(ft);
    if (root == NULL) {
        return -1;
    }
    *out_root = root;
    return 0;
}

/* ----- Code Generation Functions ----- */

int initialise_code_table(struct code_table *ct) {
    unsigned int i;
    
    if (ct == NULL) {
        return -1;
    }
    
    for (i = 0U; i < NUM_SYMBOLS; i++) {
        ct->length[i] = 0U;
        ct->code[i][0] = '\0';
    }
    
    return 0;
}

static void generate_codes_recursive(struct huffman_node *node, 
                                     struct code_table *ct,
                                     char *current_code, 
                                     unsigned int depth) {
    unsigned int i;
    int symbol;
    
    if (node == NULL) {
        return;
    }
    
    if (node->value != COMPOSITE_NODE) {
        symbol = node->value;
        
        for (i = 0U; i < depth; i++) {
            ct->code[symbol][i] = current_code[i];
        }
        ct->code[symbol][depth] = '\0';
        ct->length[symbol] = depth;
        
        return;
    }
    
    if (node->left != NULL) {
        current_code[depth] = '0';
        generate_codes_recursive(node->left, ct, current_code, depth + 1);
    }
    
    if (node->right != NULL) {
        current_code[depth] = '1';
        generate_codes_recursive(node->right, ct, current_code, depth + 1);
    }
}

int generate_codes(struct huffman_node *root, struct code_table *ct) {
    char current_code[NUM_SYMBOLS];
    
    if (root == NULL || ct == NULL) {
        return -1;
    }
    
    if (initialise_code_table(ct) != 0) {
        return -1;
    }
    
    if (root->value != COMPOSITE_NODE && root->left == NULL && root->right == NULL) {
        ct->code[root->value][0] = '0';
        ct->code[root->value][1] = '\0';
        ct->length[root->value] = 1U;
        return 0;
    }
    
    current_code[0] = '\0';
    generate_codes_recursive(root, ct, current_code, 0U);
    
    return 0;
}

void print_codes(struct code_table *ct, struct frequency_table *ft) {
    unsigned int i;
    
    printf("\nHuffman Codes:\n");
    printf("Symbol | Frequency | Code\n");
    printf("-------+-----------+------------------\n");
    
    for (i = 0U; i < NUM_SYMBOLS; i++) {
        if (ft->freq[i] > 0UL) {
            if (i >= 32 && i < 127) {
                printf("  '%c'  | %9llu | %s\n", 
                       (char)i, ft->freq[i], ct->code[i]);
            } else {
                printf(" 0x%02X | %9llu | %s\n", 
                       i, ft->freq[i], ct->code[i]);
            }
        }
    }
}

/* ----- Bit-Level I/O Functions ----- */

static void write_bit(FILE *output, int bit, struct bit_buffer *bb) {
    bb->buffer = (bb->buffer << 1) | (bit & 1);
    bb->count++;
    
    if (bb->count == 8) {
        fputc(bb->buffer, output);
        bb->buffer = 0;
        bb->count = 0;
    }
}

static void flush_bits(FILE *output, struct bit_buffer *bb) {
    if (bb->count > 0) {
        bb->buffer <<= (8 - bb->count);
        fputc(bb->buffer, output);
        bb->buffer = 0;
        bb->count = 0;
    }
}

static int read_bit(FILE *input, struct bit_buffer *bb) {
    int bit;
    
    if (bb->count == 0) {
        int byte = fgetc(input);
        if (byte == EOF) {
            return -1;
        }
        bb->buffer = (unsigned char)byte;
        bb->count = 8;
    }
    
    bit = (bb->buffer >> 7) & 1;
    bb->buffer <<= 1;
    bb->count--;
    
    return bit;
}

/* ----- Header I/O Functions ----- */

int write_frequency_header(FILE *output, struct frequency_table *ft) {
    unsigned int i;
    unsigned char bytes[8];
    int j;
    
    if (output == NULL || ft == NULL) {
        return -1;
    }
    
    for (i = 0U; i < NUM_SYMBOLS; i++) {
        count_Table freq = ft->freq[i];
        
        for (j = 7; j >= 0; j--) {
            bytes[j] = (unsigned char)(freq & 0xFF);
            freq >>= 8;
        }
        
        if (fwrite(bytes, 1, 8, output) != 8) {
            return -1;
        }
    }
    
    return 0;
}

int read_frequency_header(FILE *input, struct frequency_table *ft) {
    unsigned int i;
    unsigned char bytes[8];
    int j;
    
    if (input == NULL || ft == NULL) {
        return -1;
    }
    
    for (i = 0U; i < NUM_SYMBOLS; i++) {
        if (fread(bytes, 1, 8, input) != 8) {
            return -1;
        }
        
        ft->freq[i] = 0UL;
        for (j = 0; j < 8; j++) {
            ft->freq[i] = (ft->freq[i] << 8) | bytes[j];
        }
    }
    
    return 0;
}

/* ----- Compression Function ----- */

int compress_file(const char *input_filename, const char *output_filename) {
    FILE *input, *output;
    struct frequency_table ft;
    struct huffman_node *root;
    struct code_table ct;
    int character;
    unsigned int i;
    struct bit_buffer bb;
    count_Table total_chars = 0UL;
    
    input = fopen(input_filename, "rb");
    if (input == NULL) {
        printf("Error: Cannot open input file\n");
        return -1;
    }
    
    if (initialise_Frequency(&ft) != 0) {
        fclose(input);
        return -1;
    }
    
    if (count_Freq(input, &ft) != 0) {
        fclose(input);
        return -1;
    }
    
    for (i = 0U; i < NUM_SYMBOLS; i++) {
        total_chars += ft.freq[i];
    }
    
    if (total_chars == 0UL) {
        printf("Error: Input file is empty\n");
        fclose(input);
        return -1;
    }
    
    if (build_Tree(&ft, &root) != 0) {
        fclose(input);
        return -1;
    }
    
    if (generate_codes(root, &ct) != 0) {
        free_tree(root);
        fclose(input);
        return -1;
    }
    
    output = fopen(output_filename, "wb");
    if (output == NULL) {
        printf("Error: Cannot create output file\n");
        free_tree(root);
        fclose(input);
        return -1;
    }
    
    if (write_frequency_header(output, &ft) != 0) {
        free_tree(root);
        fclose(input);
        fclose(output);
        return -1;
    }
    
    if (fwrite(&total_chars, sizeof(count_Table), 1, output) != 1) {
        free_tree(root);
        fclose(input);
        fclose(output);
        return -1;
    }
    
    rewind(input);
    
    bb.buffer = 0;
    bb.count = 0;
    
    while ((character = fgetc(input)) != EOF) {
        unsigned char sym = (unsigned char)character;
        char *code = ct.code[sym];
        
        for (i = 0; code[i] != '\0'; i++) {
            write_bit(output, code[i] == '1' ? 1 : 0, &bb);
        }
    }
    
    flush_bits(output, &bb);
    
    free_tree(root);
    fclose(input);
    fclose(output);
    
    return 0;
}

/* ----- Decompression Function ----- */

int decompress_file(const char *input_filename, const char *output_filename) {
    FILE *input, *output;
    struct frequency_table ft;
    struct huffman_node *root, *current;
    struct bit_buffer bb;
    count_Table total_chars, decoded_chars;
    int bit;
    
    input = fopen(input_filename, "rb");
    if (input == NULL) {
        printf("Error: Cannot open input file\n");
        return -1;
    }
    
    if (read_frequency_header(input, &ft) != 0) {
        fclose(input);
        return -1;
    }
    
    if (fread(&total_chars, sizeof(count_Table), 1, input) != 1) {
        fclose(input);
        return -1;
    }
    
    if (build_Tree(&ft, &root) != 0) {
        fclose(input);
        return -1;
    }
    
    output = fopen(output_filename, "wb");
    if (output == NULL) {
        printf("Error: Cannot create output file\n");
        free_tree(root);
        fclose(input);
        return -1;
    }
    
    bb.buffer = 0;
    bb.count = 0;
    
    decoded_chars = 0UL;
    current = root;
    
    while (decoded_chars < total_chars) {
        if (current->value != COMPOSITE_NODE) {
            fputc(current->value, output);
            decoded_chars++;
            current = root;
            continue;
        }
        
        bit = read_bit(input, &bb);
        if (bit == -1) {
            break;
        }
        
        if (bit == 0) {
            current = current->left;
        } else {
            current = current->right;
        }
        
        if (current == NULL) {
            break;
        }
    }
    
    free_tree(root);
    fclose(input);
    fclose(output);
    
    return 0;
}

/* ----- Memory Management ----- */

void free_tree(struct huffman_node *root) {
    if (root == NULL) {
        return;
    }
    
    free_tree(root->left);
    free_tree(root->right);
    free(root);
}