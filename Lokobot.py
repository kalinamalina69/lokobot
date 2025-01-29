import logging
import asyncio
from datetime import datetime, timedelta
from aiogram import Bot
import pytz
from dotenv import load_dotenv
import os
import random  # Импортируем random

load_dotenv()  # Загружаем переменные окружения из .env
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Получаем токен из переменных окружения
CHAT_ID = -1002311755846  # Числовой идентификатор чата/группы (замените на реальный)
print(TOKEN)  # Выведет значение токена

# Данные пользователей (даты в формате DD.MM с ведущими нулями)
users = [
    {"first_name": "Иван", "last_name": "Иванов", "birthday": "29.01"},
    {"first_name": "Мария", "last_name": "Петрова", "birthday": "15.03"},
    {"first_name": "Алексей", "last_name": "Сидоров", "birthday": "20.05"},
]

# Список поздравлений
congratulations = [
    "🎉 Поздравляем с днем рождения! Пусть в жизни будет много радости, счастья и успехов! 🥳🎊",
    "🎂 С днем рождения! Желаем здоровья, любви и исполнения всех желаний! 🎉🎁",
    "🎊 Пусть этот день принесет много улыбок, подарков и теплых слов! С днем рождения! 🎉🎂",
    "🥳 Желаем, чтобы каждый день был наполнен радостью и вдохновением! С днем рождения! 🎉🎊",
    "🎉 Пусть сбудутся все мечты и желания! С днем рождения! 🎂🎁",
]

# Логирование
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Создаем бота
bot = Bot(token=TOKEN)

# Московский часовой пояс
MOSCOW_TZ = pytz.timezone("Europe/Moscow")

async def check_birthdays():
    """Проверяет дни рождения и отправляет сообщение, если сегодня чей-то праздник."""
    try:
        # Получаем текущую дату с учетом ведущих нулей (по московскому времени)
        today = datetime.now(MOSCOW_TZ).strftime("%d.%m")
        celebrants = [
            f"🎂 {user['first_name']} {user['last_name']}"
            for user in users if user["birthday"] == today
        ]

        if celebrants:
            # Выбираем случайное поздравление
            congratulation_message = random.choice(congratulations)

            # Формируем сообщение в зависимости от количества именинников
            if len(celebrants) == 1:
                message = f"🎉 Сегодня день рождения празднует {celebrants[0]}! {congratulation_message}"
            else:
                message = "🎉 Сегодня день рождения празднуют:\n" + "\n".join(celebrants) + f"\n{congratulation_message}"

            await bot.send_message(chat_id=CHAT_ID, text=message)
            logging.info(f"Отправлено сообщение для {len(celebrants)} пользователей.")
        else:
            logging.info("Сегодня нет именинников.")

    except Exception as e:
        logging.error(f"Ошибка при проверке дней рождения: {e}", exc_info=True)


async def scheduler():
    """Планировщик, который запускает проверку каждый день в 9:00 утра по московскому времени."""
    while True:
        try:
            now = datetime.now(MOSCOW_TZ)
            target_time = now.replace(hour=9, minute=0, second=0, microsecond=0)

            # Если текущее время уже после 9:00, планируем на следующий день
            if now >= target_time:
                target_time += timedelta(days=1)

            # Ждем до следующего 9:00 утра
            seconds_until_target = (target_time - now).total_seconds()
            logging.info(f"Ожидаем следующего запуска в 9:00 утра по Москве (через {seconds_until_target // 3600:.0f} ч. {(seconds_until_target % 3600) // 60:.0f} мин.).")
            await asyncio.sleep(seconds_until_target)

            # Запускаем проверку
            await check_birthdays()

        except Exception as e:
            logging.error(f"Ошибка в планировщике: {e}", exc_info=True)
            await asyncio.sleep(60)  # Подождать минуту перед повторной попыткой


async def main():
    """Запускает бота и планировщик."""
    logging.info("Бот запущен! Ожидаем следующего 9:00 утра по московскому времени...")
    await scheduler()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот остановлен.")
    except Exception as e:
        logging.error(f"Ошибка при запуске бота: {e}", exc_info=True)
