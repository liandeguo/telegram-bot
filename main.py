from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
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
    await update.message.reply_text(f"Current Energy Consumption: {json.loads(consumption.content)}")
def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("ping", ping))
    application.add_handler(CommandHandler("ipscan", ipscan))
    application.add_handler(CommandHandler("energycon", energy_consumption))
    # application.add_handler(CommandHandler("speedtest", speed))

    application.run_polling()

if __name__ == '__main__':
    main()


