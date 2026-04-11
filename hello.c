#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(void) {
    FILE *Moviefile = fopen("MovieFranchises.csv", "r");
    if (!Moviefile) {
        perror("MovieFranchises.csv");
        return 1;
    }

    char line[10000];

    // 1) Skip header
    if (!fgets(line, sizeof(line), Moviefile)) {
        fclose(Moviefile);
        return 0;
    }

    // 2) Read rows
    while (fgets(line, sizeof(line), Moviefile)) {
        // remove newline
        line[strcspn(line, "\r\n")] = '\0';

        // tokenise
        char *sp = strtok(line, ","); // token 0: row index (or MovieID)
        if (!sp) continue;

        sp = strtok(NULL, ",");       // token 1: MovieID (if token 0 was row index)
        if (!sp) continue;

        sp = strtok(NULL, ",");       // token 2: Title
        if (!sp) continue;

        printf("%s\n", sp);            // Title
    }

    fclose(Moviefile);
    return 0;
}
