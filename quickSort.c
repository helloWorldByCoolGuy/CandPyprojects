#include <stdio.h>
#include <stdlib.h>


void swap(int* a, int*b);
int pivot(int array[],int lowest,int highest );
void quickSort(int array[],int lowest,int highest);
void printArray(const int *array, int n);
void showOriginalAndSorted(void);


int main(void){

    showOriginalAndSorted();

    return 0;
}

void swap(int* a, int*b){
    int temporary;

    temporary = *a;
    *a = *b;
    *b = temporary;
}


int pivot(int array[],int lowest,int highest ){

    int i, median;
    

    median = lowest + (highest - lowest)/2;
   
    if(array[lowest] > array[median]){
        swap(&array[lowest], &array[median]);
    }
    if(array[lowest] > array[highest]){
        swap(&array[lowest], &array[highest]);
    }
    if(array[median] > array[highest]){
        swap(&array[median], &array[highest]);
    }
    swap(&array[median], &array[highest]);



    int p = array[highest];


    for ( i = lowest ; i < highest; i++){
        if(array[i] < p){
            swap(&array[lowest], &array[i]);
            lowest ++;
        }
    }

    swap(&array[lowest], &array[highest]);
    
    return lowest;
}

void quickSort(int array[],int lowest, int highest){
    int partition;
    if(lowest < highest){
        partition = pivot(array, lowest, highest);

        quickSort(array, lowest, partition -1);
        quickSort(array, partition +1,  highest);
    }
}

void printArray(const int *array, int n){
    for (int i = 0; i < n; i++){
        printf("%d ", array[i]);
    }
    printf("\n");
}

void showOriginalAndSorted(void){
    int array[] = {
    2147483647, -2147483647, 0, 1, -1, 999999999, -999999999,
    123456789, -123456789, 500000000, -500000000, 42, -42,
    32767, -32768, 100000, -100000, 7777777, -7777777,
    2000000000, -2000000000, 31415926, -27182818, 8080, -8080,
    123, -456, 7890, -9876, 13579, -24680, 55555, -55555
    };
    int n = sizeof(array) / sizeof(array[0]);


    printf("Original: ");
    printArray(array, n);

    quickSort(array, 0, n - 1);

    printf("Sorted:   ");
    printArray(array, n);
}

