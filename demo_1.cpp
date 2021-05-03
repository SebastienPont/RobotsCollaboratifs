#include "mbed.h"
#include "m3pi.h"


m3pi m3pi;
//static float voltage;
//static float position;
float position_of_line;

//LocalFileSystem local("file");
//Ticker Timer;
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

//unsigned char Ticker_flag = 0;
unsigned char Button_flag = 0;
unsigned char stable_flag = 0;
unsigned char time_flag = 0;
unsigned char speed_level = 1;

// les valeurs initiales.
float correction = 0.1;  
float speed = 0.1;
float threshold = 0.5;

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
    if(stable_flag == 2){
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

// Y deux façons de réaliser l'interruption de Timer.
    
void time_event_2(){
    m3pi.leds(0xE0 | speed_level);
    timeout.attach(&time_event_1,0.07);
}

void time_event_1(){
    m3pi.leds(0x00 | speed_level);
    timeout.attach(&time_event_2,0.07);
}

/*
void ticker_event(){
        if(Ticker_flag == 2)
            Ticker_flag = 0;
        if(Ticker_flag == 0){
            m3pi.leds(0x00);
            m3pi.leds(0xAA);
            }
        if(Ticker_flag == 1){
            m3pi.leds(0x00);
            m3pi.leds(0x55);
            }
        Ticker_flag += 1;
}
*/
    

int main() {
 
    // Parameters that affect the performance 
    position_of_line = 0.0;
    m3pi.leds(0x55);
 
    m3pi.locate(0,1);
    m3pi.printf("Line 1");
    button_def.mode(PullUp);   // important.
 
    wait(2.0);
    button.fall(&event);
    timeout.attach(&time_event_1,2);
    
    // faire attention a le gestion des interruptions.
    //Timer.attach(&ticker_event,2);
    m3pi.leds(0x50 | speed_level);
    
    m3pi.sensor_auto_calibrate();
    
    while (1) {
            
        // -1.0 is far left, 1.0 is far right, 0.0 in the middle
        position_of_line = m3pi.line_position();
        //position = m3pi.line_position();
 
        // Line is more than the threshold to the right, slow the left motor
        if (position_of_line > threshold) {
            m3pi.right_motor(speed);
            m3pi.left_motor(speed-correction);
        }
 
        // Line is more than 50% to the left, slow the right motor
        else if (position_of_line < -threshold) {
            m3pi.left_motor(speed);
            m3pi.right_motor(speed-correction);
        }
 
        // Line is in the middle
        else {
            m3pi.forward(speed);
        }
            
    }

}
