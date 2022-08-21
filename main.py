import hashlib
import aiosqlite
import aiogram
import aiogram.types
import json
import logging
import random
import string

logging.basicConfig(level=logging.INFO)

with open("config.json", "r") as conf_file:
    conf = json.load(conf_file)

bot = aiogram.Bot(token=conf['api']['token'])
dp = aiogram.Dispatcher(bot)

@dp.inline_handler()
async def inline_echo(inline_query: aiogram.types.InlineQuery):
    # id affects both preview and content,
    # so it has to be unique for each result
    # (Unique identifier for this result, 1-64 Bytes)
    # you can set your unique id's
    # but for example i'll generate it based on text because I know, that
    # only text will be passed in this example

    rows = list()
    async with aiosqlite.connect("phrases.db") as db:   
        async with db.execute("SELECT * FROM phrases") as cursor:
            async for row in cursor:
                rows.append(row)

    text = inline_query.query or 'echo'
    input_content = aiogram.types.InputTextMessageContent(random.choice(rows)[1], parse_mode=aiogram.types.ParseMode.HTML)
    result_id: str = hashlib.md5(''.join(random.choice(string.ascii_letters) for i in range(24)).encode()).hexdigest()
    item = aiogram.types.InlineQueryResultArticle(
        id=result_id,
        title=f'Result {text!r}',
        input_message_content=input_content,
    )
    # don't forget to set cache_time=1 for testing (default is 300s or 5m)
    await bot.answer_inline_query(inline_query.id, results=[item], cache_time=1)


if __name__ == '__main__':
    aiogram.executor.start_polling(dp, skip_updates=True)