#ifndef SCHEDULERQUEUE_h
#define SCHEDULERQUEUE_h

#include "RoverC.h"
#include <ArduinoQueue.h>

// possible actions
enum Actions {UNKNOWN, CONTINUE, COMPLETE };

// The Event queue element
struct Event {
  unsigned long time;
  Actions action;
};

class SchedulerQueue
{
public:
  static SchedulerQueue* instance;
  static SchedulerQueue *getInstance();

  // convenience method to put an Event structure in the schedulerQueue
  static void scheduleEvent(unsigned long time, Actions action);

  ArduinoQueue<Event> *getEventQueue();

private:
  // there will be only one event at any one time obviating the need to use a priority queue
  ArduinoQueue<Event> *eventQueue;

  SchedulerQueue();




};
#endif