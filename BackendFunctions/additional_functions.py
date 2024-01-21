def sustainability_score(data):
    score = 75
    if data['solar']:
        score += 25

    if data['water_check']:
        score -= 15

    pollution_num = 50
    while data['pollution'] > pollution_num:
        score -= 2
        pollution_num += 30
    
    return score
# solar and water_check are boolean vals
# pollution is average pollution over x amount of days

