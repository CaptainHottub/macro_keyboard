from setup import logger, send_notification
import sys
from macro_driver import MacroDriver

"""
This will be a wrapper for 

Event_handler in macro_driver, where I can put in specific buttons and layers so i can test stuff before my ssd arrives


todo that I will have to rewrite event_handler and macros and encoders, so self.app, self.mode, self.button, self.layers is passed through and not a global var in the class
"""
def main():
    macro_driver = MacroDriver()
    print("Whatever you input next will be redirected to macro_driver.Event_handler()")
    
    while True:
        print("\nLayout is: event_type, button, layers")
        print('Example: Button, 2, []\n')

        cmd_to_send = input("What is your input: ")
        cmd_to_send = cmd_to_send.replace(' ','')
        event_type, button, *layers = cmd_to_send.split(',')
        button = int(button)
        
        if layers == ['[]']:
            layers = []
        else: 
            temp_list = []
            layers[0] = layers[0][1:]
            layers[-1] = layers[-1][:-1]

            for i in layers:
                if i not in ['Mode', 'mode']:
                    i = int(i)
                temp_list.append(i)
                
            layers = temp_list
            
        macro_driver.Event_handler(button, event_type, layers)
    

if __name__ == '__main__':
    
    plat = sys.platform.lower()
    if plat[:5] == 'linux':
        logger.warning("Some features may not work")
        #toaster.show_toast("Warning", "Some features may not work on Linux", duration=2, threaded=True)
        send_notification(title='Warning', msg='Some features may not work on Linux')

    main()
