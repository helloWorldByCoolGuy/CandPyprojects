/*******************************************************************************
 * 48430 Fundamentals of C Programming - Assignment 2
 * Name:
 * Student ID:
 * Date of submission:
 * A brief statement on what you could achieve (<=50 words):
 *
 * A brief statement on what you could NOT achieve (<=50 words):
 *
*******************************************************************************/

/* Allowed headers only.
 * List of used functions:
 *  stdio.h  : printf, scanf, fgets, getchar, fopen, fclose, fprintf, fscanf
 *             sscanf
 *  stdlib.h : strtol
 *  string.h : strlen, strcpy, strcmp
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Preprocessing directives (widths are per spec). */
#define MAX_LIBRARY_SIZE 20
#define MAX_TITLE_SIZE   15
#define MAX_AUTHOR_SIZE  15
#define MAX_ISBN_SIZE    12   /* up to 11 digits + '\0' */
#define MAX_GENRE_SIZE   11   /* up to 10 chars + '\0' */

/* Data structures (nested struct: book_t contains date_t). */
typedef struct {
    unsigned int month; /* 1..12 */
    unsigned int year;  /* 1950..2024 */
} date_t;

typedef struct {
    char title[MAX_TITLE_SIZE + 1];
    char author[MAX_AUTHOR_SIZE + 1];
    char isbn[MAX_ISBN_SIZE];
    date_t publication_date;
    char genre[MAX_GENRE_SIZE];
} book_t;

/* Given prototype. */
void printMenu(void);

/* Helpers */
static void clear_stdin(void);
static void rstrip_newline(char *s);
static int  read_line(char *buf, size_t cap);
static int  safe_read_uint(const char *prompt, unsigned int *out);
static int  safe_read_menu_choice(int *choice);
static int  is_digits(const char *s);
static void clamp_copy(char *dst, size_t cap, const char *src);

/* Validation per spec */
static int valid_month(unsigned int m);
static int valid_year(unsigned int y);
static int valid_isbn(const char *s);

/* Features */
static int  addBook(book_t *list, int *count);
static int  deleteLast(book_t *list, int *count);
static void displayBooks(const book_t *list, int count);
static int  saveDB(const char *fname, const book_t *list, int count);
static int  loadDB(const char *fname, book_t *list, int *count);

/* Formatting constants (for display) */
#define H_TITLE  "Title"
#define H_AUTHOR "Author"
#define H_ISBN   "ISBN"
#define H_PDATE  "Publication Date"
#define H_GENRE  "Genre"

int main(void)
{
    const char *dbFileName = "library";
    book_t booklist[MAX_LIBRARY_SIZE];
    int count = 0;
    int running = 1;

    printMenu();

    while (running) {
        int choice;
        if (!safe_read_menu_choice(&choice)) {
            printf("Invalid choice.\n");
            continue;
        }

        if (choice < 1 || choice > 6) {
            printf("Invalid choice.\n");
            continue;
        }

        switch (choice) {
        case 1:
            addBook(booklist, &count);
            break;
        case 2:
            deleteLast(booklist, &count);
            break;
        case 3:
            displayBooks(booklist, count);
            break;
        case 4:
            if (saveDB(dbFileName, booklist, count)) {
                /* silent or brief confirmation is fine */
            } else {
                /* do not spam; brief failure notice */
                printf("Failed to save.\n");
            }
            break;
        case 5:
            if (loadDB(dbFileName, booklist, &count) < 0) {
                printf("Failed to load.\n");
            }
            break;
        case 6:
            running = 0;
            break;
        default:
            /* already range-checked */
            break;
        }
    }

    return 0;
}

/*******************************************************************************
 * Menu printing (must match assignment text exactly).
*******************************************************************************/
void printMenu(void)
{
    printf("\nLibrary Management System \n"
           "1. Add book\n"
           "2. Delete last book\n"
           "3. Display book list\n"
           "4. Save the book list to the database\n"
           "5. Read the book list from the database\n"
           "6. Exit the program\n");
}

/*******************************************************************************
 * Utility helpers
*******************************************************************************/
static void clear_stdin(void)
{
    int ch = 0;
    while ((ch = getchar()) != '\n' && ch != EOF) {
        /* discard */
    }
}

static void rstrip_newline(char *s)
{
    size_t n;
    if (!s) return;
    n = strlen(s);
    if (n > 0 && s[n - 1] == '\n') s[n - 1] = '\0';
}

static int read_line(char *buf, size_t cap)
{
    if (fgets(buf, (int)cap, stdin) == NULL) return 0;
    rstrip_newline(buf);
    return 1;
}

/* Menu choice: prompt and read an integer safely. */
static int safe_read_menu_choice(int *choice)
{
    char line[64];
    printf("\nEnter option (1-6): ");
    if (!read_line(line, sizeof line)) return 0;

    /* strip leading spaces */
    {
        char *p = line;
        char *end;
        long v;
        while (*p == ' ' || *p == '\t') p++;
        if (*p == '\0') return 0;
        v = strtol(p, &end, 10);
        while (*end == ' ' || *end == '\t') end++;
        if (*end != '\0') return 0;
        *choice = (int)v;
    }
    return 1;
}

static int safe_read_uint(const char *prompt, unsigned int *out)
{
    char line[64];
    char *p, *end;
    long v;

    printf("%s", prompt);
    if (!read_line(line, sizeof line)) return 0;
    p = line;
    while (*p == ' ' || *p == '\t') p++;
    if (*p == '\0') return 0;

    v = strtol(p, &end, 10);
    while (*end == ' ' || *end == '\t') end++;
    if (*end != '\0' || v < 0) return 0;

    *out = (unsigned int)v;
    return 1;
}

/* Ensure only digits (used for ISBN) and length >0. */
static int is_digits(const char *s)
{
    size_t i, n;
    if (!s) return 0;
    n = strlen(s);
    if (n == 0) return 0;
    for (i = 0; i < n; ++i) {
        if (s[i] < '0' || s[i] > '9') return 0;
    }
    return 1;
}

/* Copy with truncation to fit cap-1 and always null-terminate. */
static void clamp_copy(char *dst, size_t cap, const char *src)
{
    size_t n, i;
    if (cap == 0) return;
    n = strlen(src);
    if (n >= cap) n = cap - 1;
    for (i = 0; i < n; ++i) dst[i] = src[i];
    dst[n] = '\0';
}

/*******************************************************************************
 * Validation
*******************************************************************************/
static int valid_month(unsigned int m)
{
    return (m >= 1U && m <= 12U);
}

static int valid_year(unsigned int y)
{
    return (y >= 1950U && y <= 2024U);
}

static int valid_isbn(const char *s)
{
    size_t len;
    if (!s) return 0;
    len = strlen(s);
    if (len == 0 || len > 11) return 0;
    return is_digits(s);
}

/*******************************************************************************
 * Features
*******************************************************************************/
static int addBook(book_t *list, int *count)
{
    char line[256];
    unsigned int m, y;
    book_t b;

    if (*count >= MAX_LIBRARY_SIZE) {
        printf("Database is full. Cannot add more books.\n");
        return 0;
    }

    printf("Title: >");
    if (!read_line(line, sizeof line) || line[0] == '\0') {
        printf("Invalid title.\n");
        return 0;
    }
    clamp_copy(b.title, sizeof b.title, line);

    printf("Author: >");
    if (!read_line(line, sizeof line) || line[0] == '\0') {
        printf("Invalid author.\n");
        return 0;
    }
    clamp_copy(b.author, sizeof b.author, line);

    printf("ISBN: >");
    if (!read_line(line, sizeof line) || !valid_isbn(line)) {
        printf("Invalid ISBN.\n");
        return 0;
    }
    clamp_copy(b.isbn, sizeof b.isbn, line);

    if (!safe_read_uint("Publication date(month): >", &m) || !valid_month(m)) {
        printf("Invalid month.\n");
        return 0;
    }

    if (!safe_read_uint("Publication date(year): >", &y) || !valid_year(y)) {
        printf("Invalid year.\n");
        return 0;
    }

    printf("Genre: >");
    if (!read_line(line, sizeof line) || line[0] == '\0') {
        printf("Invalid genre.\n");
        return 0;
    }
    clamp_copy(b.genre, sizeof b.genre, line);

    b.publication_date.month = m;
    b.publication_date.year = y;

    list[*count] = b;
    (*count)++;
    return 1;
}

static int deleteLast(book_t *list, int *count)
{
    (void)list; /* list unused; count tracks logical size. */
    if (*count <= 0) {
        printf("No books to delete.\n");
        return 0;
    }
    (*count)--;
    return 1;
}

/* Print table with strict widths; left aligned text fields. */
static void displayBooks(const book_t *list, int count)
{
    int i;

    if (count <= 0) {
        printf("No books in the list.\n");
        return;
    }

    /* Header */
    printf("%-15s  %-15s  %-11s  %-18s  %-10s\n",
           H_TITLE, H_AUTHOR, H_ISBN, H_PDATE, H_GENRE);
    printf("---------------  ---------------  -----------  ------------------  "
           "----------\n");

    for (i = 0; i < count; ++i) {
        const book_t *b = &list[i];
        printf("%-15s  %-15s  %-11s  %02u-%04u            %-10s\n",
               b->title,
               b->author,
               b->isbn,
               b->publication_date.month,
               b->publication_date.year,
               b->genre);
    }
}

static int saveDB(const char *fname, const book_t *list, int count)
{
    FILE *fp;
    int i;

    fp = fopen(fname, "w");
    if (!fp) return 0;

    /* Simple, deterministic text format:
     * First line: count
     * Then per book: title, author, isbn, month, year, genre (each on own line)
     */
    if (fprintf(fp, "%d\n", count) < 0) {
        fclose(fp);
        return 0;
    }

    for (i = 0; i < count; ++i) {
        const book_t *b = &list[i];
        if (fprintf(fp, "%s\n", b->title) < 0) { fclose(fp); return 0; }
        if (fprintf(fp, "%s\n", b->author) < 0) { fclose(fp); return 0; }
        if (fprintf(fp, "%s\n", b->isbn) < 0) { fclose(fp); return 0; }
        if (fprintf(fp, "%u\n", b->publication_date.month) < 0) {
            fclose(fp); return 0;
        }
        if (fprintf(fp, "%u\n", b->publication_date.year) < 0) {
            fclose(fp); return 0;
        }
        if (fprintf(fp, "%s\n", b->genre) < 0) { fclose(fp); return 0; }
    }

    fclose(fp);
    return 1;
}

static int loadDB(const char *fname, book_t *list, int *count)
{
    FILE *fp;
    char line[256];
    long want;
    char *end;
    int i, to_load;

    fp = fopen(fname, "r");
    if (!fp) return -1;

    if (fgets(line, sizeof line, fp) == NULL) {
        fclose(fp);
        return -1;
    }
    rstrip_newline(line);
    want = strtol(line, &end, 10);
    while (*end == ' ' || *end == '\t') end++;
    if (*end != '\0' || want < 0) {
        fclose(fp);
        return -1;
    }

    to_load = (int)want;
    if (to_load > MAX_LIBRARY_SIZE) to_load = MAX_LIBRARY_SIZE;

    for (i = 0; i < (int)want; ++i) {
        book_t b;
        unsigned int m, y;

        if (fgets(line, sizeof line, fp) == NULL) { fclose(fp); return -1; }
        rstrip_newline(line);
        clamp_copy(b.title, sizeof b.title, line);

        if (fgets(line, sizeof line, fp) == NULL) { fclose(fp); return -1; }
        rstrip_newline(line);
        clamp_copy(b.author, sizeof b.author, line);

        if (fgets(line, sizeof line, fp) == NULL) { fclose(fp); return -1; }
        rstrip_newline(line);
        if (!valid_isbn(line)) { fclose(fp); return -1; }
        clamp_copy(b.isbn, sizeof b.isbn, line);

        if (fgets(line, sizeof line, fp) == NULL) { fclose(fp); return -1; }
        rstrip_newline(line);
        m = (unsigned int)strtol(line, &end, 10);
        while (*end == ' ' || *end == '\t') end++;
        if (*end != '\0' || !valid_month(m)) { fclose(fp); return -1; }

        if (fgets(line, sizeof line, fp) == NULL) { fclose(fp); return -1; }
        rstrip_newline(line);
        y = (unsigned int)strtol(line, &end, 10);
        while (*end == ' ' || *end == '\t') end++;
        if (*end != '\0' || !valid_year(y)) { fclose(fp); return -1; }

        if (fgets(line, sizeof line, fp) == NULL) { fclose(fp); return -1; }
        rstrip_newline(line);
        clamp_copy(b.genre, sizeof b.genre, line);

        b.publication_date.month = m;
        b.publication_date.year  = y;

        if (i < to_load) {
            list[i] = b;
        }
    }

    *count = to_load;
    fclose(fp);
    return to_load;
}