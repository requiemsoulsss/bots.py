import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, filters

# Токен бота
TOKEN = 'TOKEN'

# Настройки логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Функция-обработчик команды /start
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text='Привет! Я бот для игры в крестики-нолики. Чтобы начать игру, используй команду /play.')

# Функция-обработчик команды /play
def play(update, context):
    global board
    board = [' ' for _ in range(9)]
    display_board(update)
    context.bot.send_message(chat_id=update.effective_chat.id, text='Игра началась! Ты играешь крестиками. Чтобы сделать ход, используй команду /move и номер ячейки (1-9)')

# Функция-обработчик команды /move
def move(update, context):
    try:
        cell = int(context.args[0])
        if cell < 1 or cell > 9:
            raise ValueError
        if board[cell-1] != ' ':
            raise Exception('Ячейка уже занята!')
        board[cell-1] = 'X'
        display_board(update)
        if not check_game_over(update):
            bot_move(update)
            check_game_over(update)
    except (IndexError, ValueError):
        context.bot.send_message(chat_id=update.effective_chat.id, text='Неверный формат команды. Используй команду /move и номер ячейки (1-9)')
    except Exception as e:
        context.bot.send_message(chat_id=update.effective_chat.id, text=str(e))

# Функция для совершения хода ботом
def bot_move(update):
    global board
    empty_cells = [i for i in range(9) if board[i] == ' ']
    cell = random.choice(empty_cells)
    board[cell] = 'O'
    display_board(update)

# Функция для проверки окончания игры
def check_game_over(update):
    global board
    for combo in win_combinations:
        if board[combo[0]] == board[combo[1]] == board[combo[2]] != ' ':
            context.bot.send_message(chat_id=update.effective_chat.id, text=f'Победил {board[combo[0]]}!')
            display_board(update)
            return True
    if ' ' not in board:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Ничья!')
        display_board(update)
        return True
    return False

# Функция для вывода игрового поля
def display_board(update):
    global board
    board_message = ''
    for i in range(9):
        if i % 3 == 0:
            board_message += '\n'
        board_message += f'{board[i]}|'
    context.bot.send_message(chat_id=update.effective_chat.id, text=board_message)

# Функция-обработчик команды /stats
def stats(update, context):
    user = update.effective_user
    stats = get_user_stats(user.id)
    text = f'Статистика игрока {user.username}:\n' \
           f'Всего игр: {stats["total"]}\n' \
           f'Побед: {stats["wins"]}\n' \
           f'Ничьих: {stats["draws"]}\n' \
           f'Поражений: {stats["losses"]}'
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)

# Функция для получения статистики игрока
def get_user_stats(user_id):
    stats = {
        'total': 0,
        'wins': 0,
        'draws': 0,
        'losses': 0
    }
    if user_id in user_stats:
        stats = user_stats[user_id]
    return stats

# Функция-обработчик неизвестных команд
def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Извините, я не понимаю эту команду. Используйте /start, /play, /move, /stats, /stop")

def main():
    # Создаем объект Updater и передаем ему токен бота
    updater = Updater('TOKEN', use_context=True)

    # Получаем диспетчер сообщений
    dp = updater.dispatcher

    # Добавляем обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("play", play))
    dp.add_handler(CommandHandler("move", move))
    dp.add_handler(CommandHandler("stats", stats))
    dp.add_handler(CommandHandler("stop", stop))

    # Добавляем обработчик неизвестных команд
    dp.add_handler(MessageHandler(Filters.command, unknown))

    # Запускаем бота
    updater.start_polling()

    # Останавливаем бота при нажатии Ctrl+C
    updater.idle()


if __name__ == "__main__":
    main()
