import logging
from telegram.ext import Application, MessageHandler, filters, ConversationHandler
from config import BOT_TOKEN
import requests
import pytz
import datetime
from telegram.ext import CommandHandler
from telegram import ReplyKeyboardMarkup


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)
api_key = "227ba7d5f47c6eb6857061d76a7611a9"
base_url = "http://api.openweathermap.org/data/2.5/weather?"


async def start(update, context):
    """Отправляет сообщение когда получена команда /start"""
    user = update.effective_user
    reply_keyboard = [['weather'],
                      ['weather forecast'],
                      ['weather in other cities']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    await update.message.reply_html(
        rf"Hello, {user.mention_html()}! I am a weather-forecast-bot. With my help, you will find out the weather in any corner of the world!", reply_markup=markup)
    await update.message.reply_text("Choose a command.")
    return 1

async def message(update, context):
    messages = update.message.text
    print(messages)
    await update.message.reply_text("Ok!")
    chat_id = update.effective_message.chat_id
    if messages == 'weather':
        await context.bot.send_message(chat_id=chat_id, text='Write the city where you want to find out the weather.')
        return 2
    elif messages == 'weather forecast':
        await context.bot.send_message(chat_id=chat_id,
                                       text='Write the city in which you want to find out the weather forecast.')
        return 3
    elif messages == 'weather in other cities':
        res = requests.get(
            f'http://api.openweathermap.org/data/2.5/group?id=524901,498817,491422,501175,472757,520555,1496747&units=metric&appid={api_key}')

        weather = res.json()
        town = ['🌍Weather in other cities.\n    ']
        data = weather['list']
        print(data)
        chat_id = update.effective_message.chat_id
        for index, value in enumerate(data):
            city = data[index]['name']
            temperature = int(round(data[index]['main']['temp'], 0))
            temp = f'+{temperature}' if temperature > 0 else temperature
            im = data[index]['weather'][0]['icon']
            if 'n' in im:
                im = int(im.split('n')[0])
            else:
                im = int(im.split('d')[0])
            if im == 1:
                im = '☀️'
            elif im == 2:
                im = '⛅'
            elif im in [3, 4]:
                im = '☁️'
            elif im == 13:
                im = '❄️'
            elif im == 11:
                im = '⛈️'
            elif im == 10:
                im = '🌦️'
            elif im == 9:
                im = '🌧️'
            elif im == 50:
                im = '🌫️'
            town.append(f'  {im} {temp}°C {city}\n    ')
        town = "".join(town)

        await context.bot.send_message(chat_id=chat_id, text=town)
        return 1


async def weather_city(update, context):
    city = update.message.text
    print(city)
    res = requests.get(base_url, params={'q': city, 'type': 'like', 'units': 'metric', 'APPID': api_key})
    weather = res.json()
    print(weather)
    try:
        filename = f"static/img/{weather['weather'][0]['icon']}.png"
        town = weather['name']
        time = datetime.datetime.now(pytz.timezone('Europe/Moscow')).strftime('%I:%M %p')
        temperature = int(round(weather['main']['temp'], 0))
        descriptions = weather['weather'][0]['description'].capitalize()
        feels_like = int(round(weather['main']['feels_like'], 0))
        speed_wind = weather['wind']['speed']
        humidity = weather['main']['humidity']
        pressure = weather['main']['pressure']
        chat_id = update.effective_message.chat_id
        if int(feels_like) > 0:
            feels_like = f'+{feels_like}'
        if int(temperature) > 0:
            temperature = f'+{temperature}'

        await context.bot.send_photo(chat_id=chat_id, photo=filename, caption=f'🌍The weather is now in {town}.\n    '\
                f'  🕛Time: {time}\n    '                                                    
                f'  🏙️City:{town}\n    '\
                f'  🥶Feels like: {feels_like}°C\n    '                          
                f'  🌡️Temperature: {temperature}°C\n    '\
                f'  ☂️Descriptions: {descriptions}\n    '\
                f'  🌪️Wind speed: {speed_wind}m/s\n    '\
                f'  💧Humidity: {humidity}%\n    '
                f'  🌀Pressure: {pressure}mm Hg')
    except KeyError:
        await update.message.reply_text("The city wasn't found.")
    finally:
        return 1


async def weather_forecast(update, context):
    city = update.message.text
    print(city)
    chat_id = update.effective_message.chat_id
    response = requests.get("http://api.openweathermap.org/data/2.5/forecast",
                            params={'q': city, 'units': 'metric', 'APPID': api_key, 'cnt': 15})
    data = response.json()
    try:
        town = data['city']['name']
        table = [f'Weather forecast in {town}.\n    ']
        for i in data['list']:
            im = i['weather'][0]['icon']
            if 'n' in im:
                im = int(im.split('n')[0])
            else:
                im = int(im.split('d')[0])
            if im == 1:
                im = '☀️'
            elif im == 2:
                im = '⛅'
            elif im in [3, 4]:
                im = '☁️'
            elif im == 13:
                im = '❄️'
            elif im == 11:
                im = '⛈️'
            elif im == 10:
                im = '🌦️'
            elif im == 9:
                im = '🌧️'
            elif im == 50:
                im = '🌫️'
            temp = int(round(i['main']['temp'], 0))
            if temp > 0:
                temp = f"+{temp}"
            time2 = i['dt_txt'].split()
            time2 = time2[1].split(':')
            time2 = f"{time2[0]}:00"
            table.append(f'  {time2} {im} {temp}°C\n    ')
        table = ''.join(table)
        await context.bot.send_message(chat_id=chat_id, text=table)
    except KeyError:
        await update.message.reply_text("The city wasn't found.")
    finally:
        return 1

async def stop(update, context):
    await update.message.reply_text("Ok!")
    return 1

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    conv_handler = ConversationHandler(
        # Точка входа в диалог.
        # В данном случае — команда /start. Она задаёт первый вопрос.
        entry_points=[CommandHandler('start', start)],

        # Состояние внутри диалога.
        # Вариант с двумя обработчиками, фильтрующими текстовые сообщения.
        states={
            # Функция читает ответ на первый вопрос и задаёт второй.
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, message)],
            # Функция читает ответ на второй вопрос и завершает диалог.
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, weather_city)],
            3: [MessageHandler(filters.TEXT & ~filters.COMMAND, weather_forecast)]
        },

        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[CommandHandler('stop', stop)]
    )

    application.add_handler(conv_handler)
    # Регистрируем обработчик в приложении.

    # Запускаем приложение.
    application.run_polling()


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()