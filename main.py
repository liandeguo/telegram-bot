from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import os
import subprocess
import nmap
import requests
import json

TOKEN = '7005517970:AAFeiPKO48bOAekVx_CrwIJfuo17xLL-N5k' 

# Basic Functions
def online_ping(host):
    try:
        output = subprocess.run(
            ["ping", "-c", "1", "-t", "1", host],
            stdout=subprocess.DEVNULL,  
            stderr=subprocess.DEVNULL
        )
        return output.returncode == 0
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

def run_ipscan(ip_range: str) -> list:
    nm = nmap.PortScanner()
    nm.scan(hosts=ip_range, arguments='-sn')  # '-sn' for a ping scan

    results = []
    for host in nm.all_hosts():
        if nm[host].state() == 'up':
            host_info = f"Host: {host} ({nm[host].hostname()}) is up"
            results.append(host_info)
    
    return results

# Telegram Commands

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        online = False

        if online_ping(context.args[0]):
            online = True
        await update.message.reply_text(f'{"✅" if online else "❌"} {context.args[0]} is {'online' if online else 'offline'}')
    else: 
        # fujitsu = False
        rpi3 = False
        rpi4 = False
        lxc_network_mgmt = False
        lxc_jellyfin = False
        lxc_minecraft = False
        lxc_ansible = False

        if online_ping("192.168.1.32"):
            fujitsu = True 
        if online_ping("192.168.1.184"):
            rpi3 = True
        if online_ping("192.168.1.174"):
            rpi4 = True
        if online_ping("192.168.1.21"):
            lxc_network_mgmt = True 
        if online_ping("192.168.1.36"):
            lxc_jellyfin = True
        if online_ping("192.168.1.169"):
            lxc_minecraft = True
        if online_ping("192.168.1.8"):
            lxc_ansible = True
        
        # await update.message.reply_text(f'{"✅" if fujitsu else "❌"} Fujitsu Primergy is {"online" if fujitsu else "offline"}')
        await update.message.reply_text(f'{"✅" if rpi3 else "❌"} Raspberry Pi 3 is {"online" if rpi3 else "offline"}')
        await update.message.reply_text(f'{"✅" if rpi4 else "❌"} Raspberry Pi 4 is {"online" if rpi4 else "offline"}')
        await update.message.reply_text(f'{"✅" if lxc_network_mgmt else "❌"} LXC Network Managment is {"online" if lxc_network_mgmt else "offline"}')
        await update.message.reply_text(f'{"✅" if lxc_jellyfin else "❌"} Jellyfin is {"online" if lxc_jellyfin else "offline"}')
        await update.message.reply_text(f'{"✅" if lxc_ansible else "❌"} Minecraft Server is {"online" if lxc_minecraft else "offline"}')
        await update.message.reply_text(f'{"✅" if lxc_ansible else "❌"} Ansible is {"online" if lxc_ansible else "offline"}')

async def ipscan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Scanning IP range: 192.168.1.0/24. This may take a few moments...")
    
    scan_results = run_ipscan("192.168.1.0/24") 

    if not scan_results:
        await update.message.reply_text("No active hosts found.")
    else: 
        formatted_results = "\n".join(scan_results)
        await update.message.reply_text(f"Scan Results:\n{formatted_results}")

async def energy_consumption(update: Update, context: ContextTypes.DEFAULT_TYPE):
    consumption = requests.get(url="http://192.168.1.174:8123/api/states/sensor.total_energy_consumption", headers={'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI1MjVjMTZmMjY0NjY0OWY5ODRkMmVjNzk0OTc3YWNkYiIsImlhdCI6MTcyNDg3NDQ2MywiZXhwIjoyMDQwMjM0NDYzfQ.pG_yT4zGeFoIM6V8FH90rIbQkNW38uCdncNu0Zn4bKs'})
    data = json.loads(consumption.content)
   
    await update.message.reply_text(f"Current Energy Consumption: {data['state']}W")
    
async def temperature(update: Update, context: ContextTypes.DEFAULT_TYPE):
    thermostats = ['leander_temperature','kuche_temperature','wohnzimmer_temperature']
    for thermostat in thermostats:
        temperatures = requests.get(url=f"http://192.168.1.174:8123/api/states/sensor.{thermostat}", headers={'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI1MjVjMTZmMjY0NjY0OWY5ODRkMmVjNzk0OTc3YWNkYiIsImlhdCI6MTcyNDg3NDQ2MywiZXhwIjoyMDQwMjM0NDYzfQ.pG_yT4zGeFoIM6V8FH90rIbQkNW38uCdncNu0Zn4bKs'})    
        data = json.loads(temperatures.content)
        await update.message.reply_text(f"{thermostat} | {data['state']}°C ")
   

# Define the /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Create buttons
    button1 = KeyboardButton('🛜 Networking')
    button2 = KeyboardButton('💡 Smart Home')
    
    # Create reply markup with the buttons
    reply_markup = ReplyKeyboardMarkup([[button1, button2]], resize_keyboard=True)
    
    # Send a message with the keyboard
    await update.message.reply_text('Choose an option:', reply_markup=reply_markup)

async def handle_button_press(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.text == '🛜 Networking':
        button1 = KeyboardButton('Back')
        button2 = KeyboardButton('IP-Scan')
        button3 = KeyboardButton('Ping')
        await update.message.reply_text(f'Showing Smart Home Options',reply_markup=ReplyKeyboardMarkup([[button1, button2, button3]], resize_keyboard=True))
    elif update.message.text == '💡 Smart Home':
        button1 = KeyboardButton('Back')
        button2 = KeyboardButton('Energy Consumption')
        button3 = KeyboardButton('Temperatures')
        button4 = KeyboardButton('Lights')
        await update.message.reply_text(f'Showing Smart Home Options',reply_markup=ReplyKeyboardMarkup([[button1,button2],[button3, button4]], resize_keyboard=True))
    elif update.message.text == 'Back':
        await start(update, context)
    # Network
    if update.message.text == 'IP-Scan':
        await ipscan(update, context)
    elif update.message.text == 'Ping':
        await ping(update, context)

    # Smart Home
    if update.message.text == 'Energy Consumption':
        await energy_consumption(update, context)
    elif update.message.text == 'Temperatures':
        await temperature(update, context)
    elif update.message.text == 'Lights':
        back = KeyboardButton(f'Back')
        button1 = KeyboardButton(f'Leander')
        button2 = KeyboardButton(f'Wohnzimmer')
        await update.message.reply_text(f'Showing Lights', reply_markup=ReplyKeyboardMarkup([[back,button1,button2]], resize_keyboard=True))

def main():
    application = ApplicationBuilder().token(TOKEN).build()
     # Create the initial keyboard button
    button1 = KeyboardButton('Ping Hosts')
    
    # Create initial reply markup
    initial_reply_markup = ReplyKeyboardMarkup([[button1]], resize_keyboard=True)

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ping", ping))
    application.add_handler(CommandHandler("ipscan", ipscan))
    application.add_handler(CommandHandler("energycon", energy_consumption))
    # application.add_handler(CommandHandler("speedtest", speed))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_button_press))   
    application.run_polling()
    

if __name__ == '__main__':
    main()


