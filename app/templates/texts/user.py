def load(cpu_percent: float, ram_usage: tuple) -> str:
    cpu_bars = int(cpu_percent / 5)
    ram_bars = int(ram_usage[2] / 5)     
    return USAGE % (
        '|' * cpu_bars,
        ' ' * (20 - cpu_bars),
        cpu_percent,
        '|' * ram_bars,
        ' ' * (20 - ram_bars),
        ram_usage[2],
    )


START = '''
Привет 👋🏻
Я @%s - с моей помощью ты сможешь оплатить доступ к нашему API!
'''

NOT_SUBBED = '''
<i><b>✅Чтобы пользоваться ботом, вы должны подписаться на наши каналы</b>

Подпишиcь и нажми «Продолжить»!</i>
'''

PROFILE = '''
Ваш ID: <code>%i</>
Ваш баланс: <code>%i</> (хватит на <code>%i</> ген.)
Ваш токен: <code>%s</>

<a href="https://telegra.ph">Как внедрить API?</a>
'''
PRICES = '''
Цена одной генерации - 4р

Ваш баланс: <code>%i</> (хватит на <code>%i</> ген.)
'''
REF = '''
Вы сможете получать 10%% от пополнения знакомого, пригласив его по этой ссылке:

<code>https://t.me/%s?start=%i</>

Ваш реф. баланс: %i
Вывести его можно через @le_bifle
'''

USAGE = '''
Статистика сервера:

<code>CPU</>: <code>[%s%s]</> %s%%
<code>RAM</>: <code>[%s%s]</> %s%%
'''
