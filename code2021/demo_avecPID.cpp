#include "mbed.h"
#include "m3pi.h"

#define MOTOR_MAX 0.4
#define MOTOR_MIN 0.05


m3pi m3pi;
//static float voltage;
//static float position;
float position_of_line;

InterruptIn button(p21);
DigitalIn button_def(p21);
Timeout timeout;

/*
int main() {

    m3pi.locate(0,1);
    m3pi.printf("Pololu World");
    m3pi.leds(0xAA);

    wait (2.0);

    m3pi.forward(0.5); // Forward half speed
    wait (0.5);        // wait half a second
    m3pi.left(0.5);    // Turn left at half speed
    wait (0.5);        // wait half a second
    m3pi.backward(0.5);// Backward at half speed 
    wait (0.5);        // wait half a second
    m3pi.right(0.5);   // Turn right at half speed
    wait (0.5);        // wait half a second

    m3pi.stop();
    
    while(1){
        voltage = m3pi.pot_voltage();
        m3pi.printf("Vol:%f",voltage);
        wait (0.5); 
        m3pi.leds(0x55); 
        wait (0.5); 
        m3pi.leds(0xAA); 
        }     
}
*/
void time_event_1();
float PID_corrector(float exceptPosition,float linePosition);

unsigned char Button_flag = 0;
unsigned char stable_flag = 0;
unsigned char time_flag = 0;
unsigned char speed_level = 1;

float correction = 0.1;  
float speed = 0.1;
float threshold = 0.1;

// les parametres de PID.
float linePosition;
float linePositionOld;
float error;
float errorOld;

float integral;
float derivative;

// important.
static float KP = 0.01;
static float KI = 0.002;
static float KD = 0.002;

// pour changer la vitesse du robot.
// utilisez le "Button P21".
void event(){
        /*
        if(Button_flag == 2)
            Button_flag = 0;
        if(Button_flag == 0){
            m3pi.leds(0x00);
            m3pi.leds(0xAA);
            }
        if(Button_flag == 1){
            m3pi.leds(0x00);
            m3pi.leds(0x55);
            }
        Button_flag += 1;
        */
    if(stable_flag == 3){
        speed += 0.05;
        speed_level = 2*speed_level + 1;
        if(speed >= 0.35)
            speed = 0.1;
        if(speed_level > 31)
            speed_level = 1;
        m3pi.leds(speed_level);
        stable_flag = 0;
    }
    stable_flag++;
}
    
void time_event_2(){
    m3pi.leds(0xE0 | speed_level);
    correction = PID_corrector(0.0,position_of_line);
    //m3pi.printf("%4.2f \n",position_of_line);
    timeout.attach(&time_event_1,0.02);
}

void time_event_1(){
    m3pi.leds(0x00 | speed_level);
    timeout.attach(&time_event_2,0.02);
}

// PID corrector.
float PID_corrector(float exceptPosition,float linePosition){
    
    float controlVariable;
    error = linePosition - exceptPosition;
    //proportional = linePosition ;
    integral += error;
    derivative = error - errorOld;

    controlVariable = error * KP;
    controlVariable += integral * KI;
    controlVariable += derivative * KD;

    //linePositionOld = linePosition;
    errorOld = error;

    return controlVariable;  
}

void toRange(float &var) {
  if (var > MOTOR_MAX)
    var = MOTOR_MAX;
  else if (var < MOTOR_MIN)
    var = MOTOR_MIN;
}
    
int main() {
 
    float motorR = 0.05;
    float motorL = 0.05;
 
    // Parameters that affect the performance 
    position_of_line = 0.0;
    m3pi.leds(0x55);
 
    m3pi.locate(0,1);
    m3pi.printf("Line Flw");
    button_def.mode(PullUp);   // important.
 
    wait(2.0);
    button.fall(&event);
    timeout.attach(&time_event_1,2);
    m3pi.leds(0x50 | speed_level);
    m3pi.sensor_auto_calibrate();
    m3pi.printf("Keep Go");
    
    while (1) {
            
        // -1.0 is far left, 1.0 is far right, 0.0 in the middle
        position_of_line = m3pi.line_position();
        //position = m3pi.line_position();
        
        // Line is more than the threshold to the right
        
        if (error > threshold) {
            //m3pi.printf("Go Right");
            //m3pi.right_motor(speed);
            //m3pi.left_motor(speed-PID_corrector(position_of_line));
            motorR = speed+0.2*correction;
            motorL = speed-0.2*correction;
            toRange(motorR);
            toRange(motorL);
            m3pi.left_motor(motorL);
            m3pi.right_motor(motorR);
        }
 
        // Line is more than 50% to the left, slow the right motor
        else if (error < -threshold) {
            //m3pi.printf("Go Left");
            //m3pi.left_motor(speed);
            //m3pi.right_motor(speed-PID_corrector(position_of_line));
            motorR = speed-0.2*correction;
            motorL = speed+0.2*correction;
            toRange(motorR);
            toRange(motorL);
            m3pi.left_motor(motorL);
            m3pi.right_motor(motorR);
        }
        
 
        // Line is in the middle
        
        else {
            //m3pi.printf("Go!");
            m3pi.forward(speed);
        }
        
        
            
    }

}