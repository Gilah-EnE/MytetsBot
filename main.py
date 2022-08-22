import re
import sqlite3
import aiogram
import json
import logging
import random
import string
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)

with open("config.json", "r") as conf_file:
    conf = json.load(conf_file)

bot = aiogram.Bot(token=conf['api']['token'])
dp = aiogram.Dispatcher(bot)


def get_all_phrases() -> dict:
    rows = dict()
    try:
        connection = sqlite3.connect("phrases.db")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM phrases")
        rows = cursor.fetchall()
    except Exception as e:
        print(e)
        exit(1)

    return rows


def random_phrase(phrases: dict):
    return random.choice(phrases)


@dp.inline_handler(lambda query: len(query.query) == 0)
async def inline_echo(inline_query: aiogram.types.InlineQuery):
    i1 = aiogram.types.InlineQueryResultArticle(
        id=1,
        title="Випадкова цитата",
        description="Цитат в боті, як масла, тобто, дохуя!",
        input_message_content=aiogram.types.InputTextMessageContent(random_phrase(get_all_phrases())[1],
                                                                    parse_mode=aiogram.types.ParseMode.HTML)
    )
    i2 = aiogram.types.InlineQueryResultArticle(
        id=2,
        title="Пошук цитати",
        description="Для пошуку введіть уривок, назву твору або ключові слова",
        input_message_content=aiogram.types.InputTextMessageContent("Test")
    )

    await bot.answer_inline_query(inline_query.id, results=[i1, i2])


@dp.inline_handler(lambda query: len(query.query) > 0)
async def search_echo(inline_query: aiogram.types.InlineQuery):
    articles = list()
    subs = inline_query.query or 'random'
    found_phrases = [_ for _ in get_all_phrases() if re.search(subs, _[1])]
    for phrase in found_phrases:
        soup = BeautifulSoup(phrase[1], features="html.parser")
        articles.append(
            aiogram.types.InlineQueryResultArticle(id=phrase[0], title=soup.i.string, description=soup.b.string,
                                                   input_message_content=aiogram.types.InputTextMessageContent(
                                                       phrase[1], parse_mode=aiogram.types.ParseMode.HTML)))

    await bot.answer_inline_query(inline_query.id, results=articles)


if __name__ == '__main__':
    aiogram.executor.start_polling(dp, skip_updates=True)
