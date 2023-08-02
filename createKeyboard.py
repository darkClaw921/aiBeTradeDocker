import telebot
  
def create_menu_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    #keyboard.row('/addmodel')
    #keyboard.row('/addpromt')
    #keyboard.row('/context')
    #keyboard.row('/promt1') 
    #keyboard.row('/promt2')
    keyboard.row('Аналитика BTC на 5 дней')
    keyboard.row('Аналитика BTC на 15 дней')
    keyboard.row('Аналитика BTC на 30 дней')
    return keyboard