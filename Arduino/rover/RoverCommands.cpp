#include <string.h>
#include "RoverCommands.h"
#include "RoverC.h"


// List of Remote Commands
//    static CommandDef RoverCommands::defs[] = {
//      { "forward",    CMD_FORWARD },
//      { "backward" ,  CMD_BACKWARD },
//      { "left",       CMD_LEFT },
//      { "right",      CMD_RIGHT },
//      { "spinLeft",   CMD_SPINLEFT },
//      { "spinRight",  CMD_SPINRIGHT },
//      { "slideLeft",  CMD_SLIDELEFT },
//      { "slideRight", CMD_SLIDERIGHT },
//      { "stop",       CMD_STOP },
//      { "name",       CMD_NAME },
//      { "speed",      CMD_SPEED },
//      { NULL,         CMD_NOOP }
//    };

// the following are delays calibrated at speed=55
#define TURN_TIME   40
#define SPIN_TIME   900
#define SLIDE_TIME  300


  RoverCommands::RoverCommands() {
    speed = 50;
    turnTime = adjustDelay(TURN_TIME);
    spinTime = adjustDelay(SPIN_TIME);
    slideTime = adjustDelay(SLIDE_TIME);
    cmd[0] = buffer[0] = 0;
    strcpy(name, "dummy");
    currentCmd = CMD_STOP;

    // init command definitions
    defs[0].commandStr = "forward";     defs[0].cmd = CMD_FORWARD;
    defs[1].commandStr = "backward";    defs[1].cmd = CMD_BACKWARD;
    defs[2].commandStr = "left";        defs[2].cmd = CMD_LEFT;
    defs[3].commandStr = "right";       defs[3].cmd = CMD_RIGHT;
    defs[4].commandStr = "spinLeft";    defs[4].cmd = CMD_SPINLEFT;
    defs[5].commandStr = "spinRight";   defs[5].cmd = CMD_SPINRIGHT;
    defs[6].commandStr = "slideLeft";   defs[6].cmd = CMD_SLIDELEFT;
    defs[7].commandStr = "slideRight";  defs[7].cmd = CMD_SLIDERIGHT;
    defs[8].commandStr = "stop";        defs[8].cmd = CMD_STOP;
    defs[9].commandStr = "name";        defs[9].cmd = CMD_NAME;
    defs[10].commandStr = "speed";      defs[10].cmd = CMD_SPEED;
    defs[11].commandStr = NULL;         defs[11].cmd = CMD_NOOP;
  }

  // lookup the command and execute it
  int RoverCommands::execCommand(char *commandStr) {
    int i = 0;
    while (defs[i].commandStr != NULL ) {
      strncpy(buffer, commandStr, MAXCOMMANDLENGTH);

      // Identify and execute the commandStr
      char *cmd = strtok_r(buffer, " ", &last); 
      if (strncmp(cmd, defs[i].commandStr, MAXCOMMANDLENGTH) == 0) {
        execute(defs[i].cmd);
        // Serial.println("Success.");
        return 0;
      }
      i++;
    }
    Serial.println("Failed.");
    return 1;
  }

  // Start execute a robot movement command
  // Not using Arduino delay() function as it will make the remote control response laggy.
  // Using an event model instead  
  int RoverCommands::execute(COMMANDS& cmd) {
    currentCmd = cmd;

    switch (cmd) {
      case CMD_SPEED:
        speed = getInt();
        turnTime = adjustDelay(TURN_TIME);
        spinTime = adjustDelay(SPIN_TIME);
        slideTime = adjustDelay(SLIDE_TIME);
        break;
      case CMD_NAME:
        strncpy(name, getNextToken(), MAXCOMMANDLENGTH);
        break;
      case CMD_FORWARD:
        Move_forward(speed);
        break;
      case CMD_BACKWARD:
        Move_back(speed);
        break;
      case CMD_RIGHT:
        Move_turnright(speed);
        SchedulerQueue::scheduleEvent(turnTime, COMPLETE);
        break;
      case CMD_LEFT:
        Move_turnleft(speed);
        SchedulerQueue::scheduleEvent(turnTime, COMPLETE);
        break;
      case CMD_SPINRIGHT:
        Move_turnright(speed);
        SchedulerQueue::scheduleEvent(adjustDelay(spinTime), COMPLETE);
        break;
      case CMD_SPINLEFT:
        Move_turnleft(speed);
        SchedulerQueue::scheduleEvent(adjustDelay(spinTime), COMPLETE);
        // Serial.println("spinleft complete scheduled.");
        break;
      case CMD_SLIDELEFT:
        Move_left(speed);
        SchedulerQueue::scheduleEvent(slideTime, COMPLETE);
        break;
      case CMD_SLIDERIGHT:
        Move_right(speed);
        SchedulerQueue::scheduleEvent(slideTime, COMPLETE);
        break;
      case CMD_STOP:
        Move_stop(speed);
        break;
      default:
        break;
    }
    return 0;
  }

  // retreive name specified in "name" command
  char *RoverCommands::getName() {
    return name;
  }

  // retreive the speed setting of movements
  int RoverCommands::getSpeed() {
    return speed;
  }

  // get next token in command string
  char *RoverCommands::getNextToken() {
    return strtok_r(NULL, " ", &last);
  }

  // convert next token in command string to an integer
  int RoverCommands::getInt() {
    int aNumber;
    char *arg;
    arg = getNextToken();
    if (arg != NULL) {
      aNumber = atoi(arg);    // Converts a char string to an integer
    }
    else {
      aNumber = 0;
    }
  
    return aNumber;
  }

  // Continue executing a robot movement command
  // not currently used in this robot application
  int  RoverCommands::continueExecute() {
    Serial.print("ContinueCmd: ");
    Serial.println(currentCmd);

    // Not needed

    return 0;
  }

  // Finish off executing a robot movement command
  // this may be due to normal completion or
  // abortion due to a new command being received
  int  RoverCommands::completeExecute() {
    Serial.print("CompleteCmd: ");
    Serial.println(currentCmd);
    Move_stop(speed);
    return 0;    
  }

// vary the delay according to the speed of the robot
// to make the turning angle relatively constant at different speeds
float RoverCommands::adjustDelay(int delay) {
  float adjustedDelay = float(delay) * 330. / (6. * float(speed));
  Serial.print(delay);
  Serial.print(" -> ");
  Serial.println(adjustedDelay);
  return adjustedDelay;
}
