from datetime import datetime


def send_message():
    try:
        data = {
        "users": [
            {
                "id": 96,
                "user_id": 906478962,
                "chat_id": -1002195788409,
                "name": "Salam",
                "birthday": "2010-07-08"
            },
            {
                "id": 20,
                "user_id": 5888132516,
                "chat_id": -1002195788409,
                "name": "Zhal",
                "birthday": "2009-01-24"
            },
            {
                "id": 52,
                "user_id": 5888132516,
                "chat_id": -1002195788409,
                "name": "Lalra",
                "birthday": "2001-06-16"
            }
        ]
    }
    
    
        today = datetime.now()
        next_birthday = None
        min_days_diff = float("inf")
        # TODO доп проверка среди всех дней рождений какой самый ближайщий тот и выбрать
        # TODO по дню и по месяцу        
        for user in data["users"]:
            birthday_date = datetime.strptime(user["birthday"], '%Y-%m-%d')
            birthday_this_year = birthday_date.replace(year=today.year)
            
            if birthday_this_year < today:
                birthday_this_year = birthday_date.replace(year=today.year + 1)
            days_diff = (birthday_this_year - today).days

            if days_diff < min_days_diff:
                min_days_diff = days_diff
                next_birthday = user
            
        if next_birthday:
            date = [int(part) for part in next_birthday["birthday"].split("-")]
            print(date)
            age = datetime.now().year - date[0]
            # month_of_birthday = names_of_months(date[1])
    
            print(f"Ближайший день рождения у {next_birthday['name']} - {date[2]}. \
                                \n(Исполняется {age})")
        else:
            print("Информация о днях рождения отсутствует")
    
    except Exception as e:
        print(e)
        
send_message()