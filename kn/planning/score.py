# vim: et:sta:bs=2:sw=4:

# Returns the amount of seconds in the fiven amount of hours and minutes
def hm2s(h,m=0):
    return 60*(60*h+m)

BORREL_START = hm2s(20,30)
BORREL_FIRST_SWITCH = hm2s(23)
BORREL_SECOND_SWITCH = hm2s(25)
BORREL_END = hm2s(28)

def timedelta_to_seconds(td):
    return td.days*hm2s(24)+td.seconds

def p_borrel_uncurried(first, second, third, not_after, vacancy):
    event = vacancy.event
    # Only give a score on a monday
    if event.date.weekday()!=0:
        return False
    # the moment the vacancy starts (ends) in seconds after the 
    # start of the monday.
    vbegin = timedelta_to_seconds(vacancy.begin-event.date)
    vend = timedelta_to_seconds(vacancy.end-event.date)
    # Only give a score for vacancies within the BORREL-interval
    if vbegin < BORREL_START:
        return False
    if vend > BORREL_END:
        return False
    if vend > not_after:
        return 0
    # The list of scores of the shifts the vacancy intersects
    scores = []
    if vbegin < BORREL_FIRST_SWITCH:
        scores.append(first)
    if vbegin < BORREL_SECOND_SWITCH and vend > BORREL_FIRST_SWITCH:
        scores.append(second)
    if vend > BORREL_SECOND_SWITCH:
        scores.append(third)
    return min(scores)

def p_borrel(first, second, third, not_after=BORREL_END):
    return lambda v: p_borrel_uncurried(first, second, third, not_after, v)

preferences = {
        "bas":      (p_borrel(100,100,0,hm2s(24)),),
        "bente":    (p_borrel(100, 50, 50),),
        "bramw":    (p_borrel(  0,  0,100),),
        "chaim":    (p_borrel(100,100,100),),
        "dennisi":   (p_borrel(100,100,100),),
        "hugo":     (p_borrel(100,100,100),),
        "jean":     (p_borrel(100, 50,  0),),
        "jille":    (p_borrel(100,100,100),),
        "judithvs": (p_borrel(  0,  0,  0),),
        "koen":     (p_borrel(100,100,100),),
        "lisa":     (p_borrel(  0,100,100),),
        "loesje":   (p_borrel(100,100,  0),),
        "louise":   (p_borrel(  0,  0,  0),),
        "loesje":   (p_borrel(100,100,  0),),
        "niek":     (p_borrel(100,100,  0),),
        "nieks":    (p_borrel(100,100,  0),),
        "olivier":  (p_borrel(100,100, 50),),
        "petervdv": (p_borrel(100,100,100),),
        "remco":    (p_borrel(100,100,100),),
        "robin":    (p_borrel(100,100,100),),
        "rik":      (p_borrel(100,100, 50),),
        "sara":     (p_borrel(  0,  0,  0),),
        "shane":    (p_borrel(100,100, 50),),
        "steef":    (p_borrel(100,100,100),),
        "tijn":     (p_borrel(100,100,100),)
}

def planning_vacancy_worker_score(vacancy, worker):
    un = worker.username
    if un not in preferences:
        # If the preferences of a worker have not been set,
        # asume (s)he is available so that we'll get his/her preferences asap.
        return 101
    for preflet in preferences[un]:
        score = preflet(vacancy)
        if preflet!=False:
            return score
    # If nothing has been set, assume the worker is not available
    return 0
