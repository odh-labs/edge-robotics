#include "SchedulerQueue.h"

// there will be only one event at any one time
#define QUEUE_SIZE_ITEMS 5

SchedulerQueue* SchedulerQueue::instance = NULL;



  SchedulerQueue *SchedulerQueue::getInstance() {
    if (instance == NULL) {
      instance = new SchedulerQueue();
    }
      return instance;
  }


  SchedulerQueue::SchedulerQueue() {
    eventQueue = new ArduinoQueue<Event>(QUEUE_SIZE_ITEMS);
  }

  ArduinoQueue<Event> *SchedulerQueue::getEventQueue() {
    return eventQueue;
  }

  // convenience method to put an Event structure in the queue
  void SchedulerQueue::scheduleEvent(unsigned long time, Actions action) {
    Event event;
    event.action = action;
    event.time = millis() + time;

    ArduinoQueue<Event> * queue = getInstance()->getEventQueue();
    queue->enqueue(event);
  }