#include <stdio.h>
#include <limits.h>

void buuble_Sort(int arr[], int n);

static void print_array(const int arr[], int n) {
    for (int i = 0; i < n; i++) {
        printf("%d ", arr[i]);
    }
    printf("\n");
}

int main(void) {
    int a[] = {
    INT_MAX, 0, -1, INT_MIN, 5, -999, 42, INT_MAX, INT_MIN, 7,
    -7, 7, 0, 0, 123456789, -123456789
    };
    int n = sizeof(a) / sizeof(a[0]);

    printf("Before: ");
    print_array(a, n);

    buuble_Sort(a, n);

    printf("After : ");
    print_array(a, n);

    return 0;
}

void buuble_Sort(int arr[], int n) {
    int i, j;

    for (i = 0; i < n - 1; i++) {
        int swapped = 0;

        for (j = 0; j < n - 1 - i; j++) {
            if (arr[j] > arr[j + 1]) {
                int tmp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = tmp;
                swapped = 1;
            }
        }

        if (!swapped) {
            break;
        }
    }
}
