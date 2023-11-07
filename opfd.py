import logging
import json
import aiohttp
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

async def get_eth_data():
    url = "https://api.aevo.xyz/index?asset=ETH"
    headers = {"Accept": "application/json"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return data
            else:
                return None
            
async def get_alldata():
    url = "https://api.aevo.xyz/assets"
    headers = {"Accept": "application/json"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return data
            else:
                return None
            
async def get_crypto_price(asset):
    url = f"https://api.aevo.xyz/index?asset={asset}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data
            else:
                return None
            
async def get_crypto_funding(asset):
    url = f"https://api.aevo.xyz/funding?instrument_name={asset}-PERP"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data
            else:
                return None
            

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    markup_main = types.ReplyKeyboardMarkup(resize_keyboard= True)
    item1=types.KeyboardButton('📍About')
    item2=types.KeyboardButton('⚡Assets')
    item3=types.KeyboardButton('📈Price')
    item4=types.KeyboardButton('🖌Links')
    item5=types.KeyboardButton('📊Funding')
    markup_main.add(item1,item4,item2,item3, item5)
    await message.answer("Welcome to the helper bot for *AEVO*. Here you will find a lot of interesting information about this platform and more.\n\n💻 For a list of functions, click on - /help",reply_markup=markup_main, parse_mode=types.ParseMode.MARKDOWN)
    
@dp.message_handler(commands=['help'])
async def send_help(message: types.Message):
    await message.answer("🌐 All commands that the bot currently has: \n\n1) 📍*About* - useful information about the AEVO project.\n\n2) 🖌*Links* - official links to AEVO social networks and the website to avoid scams.\n\n3) ⚡*Assets* - list of cryptocurrencies that are available for trading on AEVO.\n\n4) 📈*Price* - view the price of a specific cryptocurrency in real time.\n\n 5) 📊*Funding* - finding out information about funding on the market.",parse_mode=types.ParseMode.MARKDOWN)

@dp.message_handler(regexp='⚡Assets')
async def send_assets(message: types.Message):
    await message.answer("We are collecting data, please wait...")
    all_data = await get_alldata()
    new_data = "\n".join(f"{i + 1}) {item}" for i, item in enumerate(all_data, start=0))
    if all_data:
        await message.answer(new_data)
    else:
        await message.answer("Oops, something went wrong. Try again!")

@dp.message_handler(regexp='📍About')
async def send_about(message: types.Message):
    await message.answer("*Aevo* is a high-performance decentralized options exchange.\n\n🔥 The exchange operates on a specialized version of the *Ethereum Virtual Machine (EVM)*.\n\n💻 It manages an off-chain order book, and once orders are matched, transactions are executed and settled using smart contracts.\n\n📚 In July 2023, a decisive vote took place, approving RGP-33, which advocated for the integration of *Ribbon* into *Aevo*.\n\n👨‍💻 This near-unanimous decision signifies the alignment of stakeholders' visions and the direction of Aevo's team efforts.", parse_mode=types.ParseMode.MARKDOWN)

@dp.message_handler(regexp='🖌Links')
async def send_links(message: types.Message):
    markup = types.InlineKeyboardMarkup()
    site= types.InlineKeyboardButton(text='Site', url='https://www.aevo.xyz/')
    twit= types.InlineKeyboardButton(text='Twitter', url='https://twitter.com/aevoxyz')
    disc= types.InlineKeyboardButton(text='Discord', url='https://discord.com/invite/aevo')
    git= types.InlineKeyboardButton(text='Github', url='https://github.com/aevoxyz')
    trade = types.InlineKeyboardButton(text='Trading', url='https://app.aevo.xyz/option/eth')
    markup.add(site,twit,disc,git,trade)
    await message.answer("Below are links to official AEVO data:", reply_markup=markup)
waiting_for_request = {}

@dp.message_handler(regexp='📈Price')
async def send_price(message: types.Message):
    waiting_for_request[message.from_user.id] = 'price'
    await message.answer("Write the short name of the cryptocurrency for which you want to find out the price on the Aevo platform (BTC, ETH and others)")

@dp.message_handler(regexp='📊Funding')
async def send_funding(message: types.Message):
    waiting_for_request[message.from_user.id] = 'funding'
    await message.answer("Write the short name of the cryptocurrency for which you want to find out the funding on the Aevo platform (BTC, ETH and others)")

@dp.message_handler()
async def process_request(message: types.Message):
    request_type = waiting_for_request.get(message.from_user.id)
    if request_type == 'price':
        asset = message.text
        await message.answer("We are collecting data, please wait...")
        asset_price = await get_crypto_price(asset)
        if asset_price:
            formatted_price = f"{asset} - {float(asset_price['price']):.2f}$"
            await message.answer(formatted_price)
        else:
            await message.answer("Oops, something went wrong. Try again!")
        waiting_for_request.pop(message.from_user.id, None)
    elif request_type == 'funding':
        asset = message.text
        await message.answer("We are collecting data, please wait...")
        asset_fund = await get_crypto_funding(asset)
        if asset_fund:
            formatted_fund = f"{asset} - {float(asset_fund['funding_rate']):f}"
            await message.answer(formatted_fund)
        else:
            await message.answer("Oops, something went wrong. Try again!")
        waiting_for_request.pop(message.from_user.id, None)
    else:
        await message.answer("You haven't initiated any process. Type '📈Price' or '📊Funding' to get started.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)