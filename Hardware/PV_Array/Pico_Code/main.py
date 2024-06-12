import uasyncio as asyncio
from machine import Pin
from irradiance import irradiance_simulation  # Assuming this is still needed
from IncrCond_Server import start_mppt_mode  # Import the server interaction function
#from mppt import mppt_incremental_conductance

async def irradiance_task():
    print("Switched to Irradiance Simulation Mode")
    await asyncio.sleep_ms(100)  # Placeholder delay to yield control
    irradiance_simulation()

async def mppt_task():
    print("Switched to MPPT Mode")
    await asyncio.sleep_ms(100)  # Placeholder delay to yield control
    
    # Assuming start_mppt_mode handles interaction with your server
    await start_mppt_mode()

async def main():
    while True:
        try:
            print("Press 'i' for Irradiance Simulation Mode, 'm' for MPPT Mode, or 'q' to quit")
            
            # Prompt for mode selection every 5 seconds
            for _ in range(5):
                print("Next input in {} seconds...".format(5 - _), end='\r')
                await asyncio.sleep(1)
            
            print("\n")
            
            choice = input("Your choice: ").strip().lower()
            
            if choice == 'i':
                await irradiance_task()
            elif choice == 'm':
                await mppt_task()
            elif choice == 'q':
                print("Exiting the program...")
                break
            else:
                print("Invalid input. Please enter 'i', 'm', or 'q'.")
        
        except KeyboardInterrupt:
            print("\nExiting the program...")
            break

if __name__ == "__main__":
    asyncio.run(main())

