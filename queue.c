#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAX 50  // Max size of the queue
#define FILENAME "queue_data.txt"  // File to store/load queue data

typedef struct {
	char name[50];
	int priority;  // 1 for VIP, 2 for regular
	int id;
	time_t timestamp; // Timestamp when enqueued
} Passenger;

typedef struct {
	Passenger passengers[MAX];
	int front, rear;
	int vip_count;       // Count of VIP passengers (1-10)
	int regular_count;   // Count of regular passengers (11 onward)
} PriorityQueue;

void initializeQueue(PriorityQueue *q) {
	q->front = -1;
	q->rear = -1;
	q->vip_count = 0;
	q->regular_count = 10;  // Start regular IDs from 11
}

int isEmpty(PriorityQueue *q) {
	return q->front == -1;
}

int isFull(PriorityQueue *q) {
	return q->rear == MAX - 1;
}

void enqueue(PriorityQueue *q, char *name, int priority) {
	if (isFull(q)) {
		printf("Queue is full. Cannot enqueue\n");
		return;
	}

	Passenger newPassenger;
	strcpy(newPassenger.name, name);
	newPassenger.priority = priority;
	newPassenger.timestamp = time(NULL);

	if (priority == 1 && q->vip_count < 10) {
		newPassenger.id = ++q->vip_count;
	} else {
		newPassenger.id = ++q->regular_count;
	}

	if (isEmpty(q)) {
		q->front = 0;
		q->rear = 0;
		q->passengers[q->rear] = newPassenger;
	} else {
		int i;
		for (i = q->rear; i >= q->front; i--) {
			if (q->passengers[i].priority > newPassenger.priority) {
				q->passengers[i + 1] = q->passengers[i];
			} else {
				break;
			}
		}
		q->passengers[i + 1] = newPassenger;
		q->rear++;
	}
	printf("Passenger %s with priority %d and ID %d enqueued at %s", name, priority, newPassenger.id, ctime(&newPassenger.timestamp));
}

void dequeue(PriorityQueue *q) {
	if (isEmpty(q)) {
		printf("Queue is empty. Cannot dequeue\n");
		return;
	}

	Passenger removedPassenger = q->passengers[q->front];
	printf("Passenger %s with priority %d and ID %d dequeued.\n", removedPassenger.name, removedPassenger.priority, removedPassenger.id);

	if (q->front == q->rear) {
		q->front = q->rear = -1;
	} else {
		q->front++;
	}
}

void peek(PriorityQueue *q) {
	if (isEmpty(q)) {
		printf("Queue is empty. No passenger to peek.\n");
	} else {
		Passenger nextPassenger = q->passengers[q->front];
		printf("Next passenger: %s with priority %d and ID %d enqueued at %s", nextPassenger.name, nextPassenger.priority, nextPassenger.id, ctime(&nextPassenger.timestamp));
	}
}

void showQueue(PriorityQueue *q) {
	if (isEmpty(q)) {
		printf("Queue is empty. No passengers to display\n");
		return;
	}

	printf("Passengers in list:\n");
	for (int i = q->front; i <= q->rear; i++) {
		printf("Passenger name: %s\tPriority level: %d\tID: %d\tEnqueued at: %s", 
			   q->passengers[i].name, q->passengers[i].priority, q->passengers[i].id, ctime(&q->passengers[i].timestamp));
	}
}

// Function to store queue to file
void storeQueueToFile(PriorityQueue *q) {
	FILE *file = fopen(FILENAME, "w");
	if (!file) {
		printf("Error opening file for writing\n");
		return;
	}

	for (int i = q->front; i <= q->rear; i++) {
		fprintf(file, "%s %d %d %ld\n", q->passengers[i].name, q->passengers[i].priority, q->passengers[i].id, q->passengers[i].timestamp);
	}
	fclose(file);
	printf("Queue stored successfully to %s\n", FILENAME);
}

// Function to load queue from file
void loadQueueFromFile(PriorityQueue *q) {
	FILE *file = fopen(FILENAME, "r");
	if (!file) {
		printf("Error opening file for reading\n");
		return;
	}

	initializeQueue(q);
	Passenger p;
	while (fscanf(file, "%s %d %d %ld\n", p.name, &p.priority, &p.id, &p.timestamp) != EOF) {
		if (p.priority == 1) {
			q->vip_count = p.id > q->vip_count ? p.id : q->vip_count;
		} else {
			q->regular_count = p.id > q->regular_count ? p.id : q->regular_count;
		}
		q->passengers[++q->rear] = p;
		if (q->front == -1) q->front = 0;
	}
	fclose(file);
	printf("Queue loaded successfully from %s\n", FILENAME);
}

int main() {
	PriorityQueue queue;
	initializeQueue(&queue);

	int choice;
	char name[50];
	int priority;

	while (1) {
		printf("\nMenu:\n");
		printf("1. Enqueue Passenger\n");
		printf("2. Dequeue Passenger\n");
		printf("3. Peek Next Passenger\n");
		printf("4. Check if Queue is Empty\n");
		printf("5. Check if Queue is Full\n");
		printf("6. Display passengers and their priorities\n");
		printf("7. Store current queue to file\n");
		printf("8. Load queue from saved file\n");
		printf("9. Exit\n");
		printf("Enter your choice: ");
		scanf("%d", &choice);

		switch (choice) {
		case 1:
			printf("Enter passenger name: ");
			scanf("%s", name);
			printf("Enter priority (1-VIP, 2-Regular): ");
			scanf("%d", &priority);
			enqueue(&queue, name, priority);
			break;
		case 2:
			dequeue(&queue);
			break;
		case 3:
			peek(&queue);
			break;
		case 4:
			if (isEmpty(&queue))
				printf("Queue is empty\n");
			else
				printf("Queue is not empty\n");
			break;
		case 5:
			if (isFull(&queue))
				printf("Queue is full\n");
			else
				printf("Queue is not full\n");
			break;
		case 6:
			showQueue(&queue);
			break;
		case 7:
			storeQueueToFile(&queue);
			break;
		case 8:
			loadQueueFromFile(&queue);
			break;
		case 9:
			exit(0);
		default:
			printf("Invalid choice\n");
		}
	}

	return 0;
}
