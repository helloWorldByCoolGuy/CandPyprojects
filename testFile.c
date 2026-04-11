#include <stdio.h>
#include <stdlib.h>
#include <string.h>


typedef struct
{
    int row_id;
    int movie_id;

    char title[256];

    long long lifetime_gross;
    int year;

    char studio[128];
    char rating[16];

    double runtime;
    double budget;

    char release_date[16];

    double vote_avg;
    int vote_count;
    int franchise_id;
} Movies_Record;




int main(void){

    FILE * Moviefile;
    char line[10000];


    char *sp;

    Moviefile = fopen("MovieFranchises.csv","r");

    if (Moviefile == NULL){
        printf("File have issue opening.\n");
        exit(0);
    }

    while(fgets(line, 10000, Moviefile) != NULL){

        

    }


    fclose(Moviefile);


    return 0;
}


