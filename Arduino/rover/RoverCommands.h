#ifndef RoverCommands_h
#define RoverCommands_h

#include "SchedulerQueue.h"

#define MAXCOMMANDLENGTH 15


// Behaviour for the robot when it receives a serial command:
// - act on the command
class RoverCommands
{
  public:


    enum COMMANDS {
      CMD_FORWARD,
      CMD_BACKWARD,
      CMD_LEFT,
      CMD_RIGHT,
      CMD_SPINLEFT,
      CMD_SPINRIGHT,
      CMD_SLIDELEFT,
      CMD_SLIDERIGHT,
      CMD_STOP,
      CMD_NAME,
      CMD_SPEED,
      CMD_NOOP
    };

    struct CommandDef {
      char *commandStr;
      COMMANDS cmd;
    }; 
  
  

  RoverCommands();

  // lookup the command and execute it
  int execCommand(char *commandStr);

  // Start executing a robot movement command
  int execute(COMMANDS& cmd);

  // Continue executing a robot movement command
  int continueExecute();

  // Finish off executing a robot movement command
  int completeExecute();

  char *getName();
  int getSpeed();

private:
    char cmd[MAXCOMMANDLENGTH + 1];
    char buffer[MAXCOMMANDLENGTH + 1];
    char name[MAXCOMMANDLENGTH + 1];
    int speed;
    char *last;
    CommandDef defs[16];
    COMMANDS currentCmd;
    int turnTime;
    int spinTime;
    int slideTime;
  
    char *getNextToken();
    int getInt();
    float adjustDelay(int delay);
};

#endif
