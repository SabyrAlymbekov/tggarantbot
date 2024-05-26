#
# root = 688136452
#
# # Хэндлер для команды "Просмотр сообщений"
# @bot.message_handler(func=lambda message: message.text == 'Просмотр сообщений')
# def view(message):
#     """
#     Просмотр всех сообщений
#     :param message: types.Message
#     :return: None
#     """
#     if root == message.from_user.id:
#         all_question = new_sql.get_question()
#         for question in all_question:
#             bot.send_message(message.chat.id, question)
#
# # Хэндлер для команды "Просмотреть кол-во пользователей"
# @bot.message_handler(func=lambda message: message.text == 'Просмотреть ко-во пользователей')
# def count_people(message):
#     """
#     Просмотр кол-во пользователей
#     :param message: types.Message
#     :return: None
#     """
#     if root == message.from_user.id:
#         users = new_sql.get_all_id()
#         count = len(users)
#         bot.send_message(message.chat.id, f'Всего пользователей: {count}')
#
# # Хэндлер для команды "Ответить на сообщение"
# @bot.message_handler(func=lambda message: message.text == 'Ответить на сообщение')
# def answer(message):
#     """
#     Вводим ID человека, которому хотим ответить на сообщение
#     :param message: types.Message
#     :return: None
#     """
#     if root == message.from_user.id:
#         msg = bot.send_message(message.chat.id, 'Введите ID человека, которому хотите ответить:')
#         bot.register_next_step_handler(msg, process_id_step)
#
# def process_id_step(message):
#     chat_id = message.chat.id
#     user_id = message.text
#     bot.send_message(chat_id, 'Введите сообщение с ответом:')
#     bot.register_next_step_handler(message, process_answer_step, user_id)
#
# def process_answer_step(message, user_id):
#     answer = message.text
#     try:
#         bot.send_message(user_id, answer)
#         bot.send_message(message.chat.id, 'Сообщение отправлено!')
#         print(f'Отправлено сообщение с ответом пользователю: {user_id}')
#     except Exception as exc:
#         print(f'Ошибка: {exc}. ID: {user_id}')
#         bot.send_message(message.chat.id, 'Данные об ID указаны не верно, перепроверьте, или пользователь заблокировал бота.')
#
# # Хэндлер для команды "Сделать рекламный пост"
# @bot.message_handler(func=lambda message: message.text == 'Сделать рекламный пост')
# def add_post(message):
#     """
#     Активация рекламного поста, прием заголовка
#     :param message: types.Message
#     :return: None
#     """
#     if message.from_user.id == root:
#         msg = bot.send_message(message.chat.id, 'Введите заголовок рекламного поста:')
#         bot.register_next_step_handler(msg, process_post_title)
#
# def process_post_title(message):
#     chat_id = message.chat.id
#     title = message.text
#     msg = bot.send_message(chat_id, 'Введите основной текст:')
#     bot.register_next_step_handler(msg, process_post_text, title)
#
# def process_post_text(message, title):
#     chat_id = message.chat.id
#     text = message.text
#     msg = bot.send_message(chat_id, 'Вставьте фотографию для привлечения внимания:')
#     bot.register_next_step_handler(msg, process_post_image, title, text)
#
# def process_post_image(message, title, text):
#     chat_id = message.chat.id
#     if message.content_type == 'photo':
#         img = message.photo[-1].file_id
#         msg = bot.send_message(chat_id, 'Введите ссылку рекламируемый объект:')
#         bot.register_next_step_handler(msg, process_post_href, title, text, img)
#     else:
#         bot.send_message(chat_id, 'Пожалуйста, отправьте фотографию.')
#
# def process_post_href(message, title, text, img):
#     chat_id = message.chat.id
#     href = message.text
#     inline_post_kb = types.InlineKeyboardButton('Перейти к источнику', url=href)
#     post_keyboard = types.InlineKeyboardMarkup().add(inline_post_kb)
#     users_id = new_sql.get_all_id()
#     for user_id in users_id:
#         try:
#             bot.send_photo(user_id, img, f'<b>{title}</b>\n\n{text}', parse_mode='HTML', reply_markup=post_keyboard)
#         except Exception as exc:
#             print(f"Пользователь {user_id} заблокировал бота.|{exc}|")
#     bot.send_message(chat_id, 'Рекламный пост отправлен!')
