def formatNb(number: int) -> str:
    split_number = str(number).split('.')
    
    if len(split_number) == 1:
        return '{:.0%}'.format(number)

    try:
        if int(split_number[1]) == 0:
            return '{:.0%}'.format(number)
    except:
        pass

    nb_zero = 0

    for char in split_number[1]:
        if char == '0':
            nb_zero += 1
        else:
            break

    if nb_zero <4:
        return f'{number:.{nb_zero}%}'
    else:
        return f'{number:.{nb_zero*2}%}'