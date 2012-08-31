# vim: et:sta:bs=2:sw=4:
from datetime import datetime

# Returns the amount of seconds in the fiven amount of hours and minutes
def hm2s(h,m=0):
    return 60*(60*h+m)

BORREL_START = hm2s(20,30)
BORREL_FIRST_SWITCH = hm2s(23)
BORREL_SECOND_SWITCH = hm2s(25)  # 1.00 the next day
BORREL_END = hm2s(28)            # 4.00 the next day

# Listed below are the preferences of the workers.
# These preferences determine for each vacancy and worker a score.
# This score usually ranges from 0 to 100; the current interpretation is:
#
#   100 - The worker is OK with filling this vacancy
#    50 - The worker is willing to fill this vacancy if need be
#     0 - The worker is not willing to fill this vacancy
# False - Not set
#
# An exceptional score is:
#
#   101 - The workers preference is unknown.  Determining it has priority.
#
# 
# The score is computed using "preflets" for each worker.
# A preflet is a function which takes a vacancy and returns a score.
#
#
#   Example:
#
# The preflet  p_borrel(X,Y,Z)  takes a vacancy and determines
# if it is (like) a borrel-shift.  If it is (like) the first borrel shift,
# it returns the score X, if it is (like) the second Y 
# and Z if it is like the third.  If the vacancy is not like a borrel-shift
# (for instance, if it is a Karpe Rockt'em) it returns False.
#
#
# Below is a tuple (p_1, ... , p_N) of preflets for each worker.
# If  v  is some vacancy, then the score of the worker for v is determined
# by calling p_1 on v.  If p_1(v) returns a sensible score (i.e. not False)
# then this score is used, otherwise p_2 is consulted, and so on.
#
# If all p_i's return False, then the score is set to 0.
# If there was no tuple of p_i's to begin with, the score is set to 101.
#
#
# For examples,  see "preferences" below.
#


def timedelta_to_seconds(td):
    return td.days*hm2s(24)+td.seconds

def p_borrel_uncurried(first, second, third, not_after, vacancy):
    event = vacancy.event
    # Only give a score if this is a borrel
    if event.kind!="borrel":
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
    if len(scores) == 0:
        return False
    return min(scores)

def p_borrel(first, second, third, not_after=BORREL_END):
    return lambda v: p_borrel_uncurried(first, second, third, not_after, v)


def p_temporary_uc(begin, end, preflet, vacancy):
    event = vacancy.event
    if begin <= event.date <= end:
        return preflet(vacancy)
    return False

def p_temporary(begin, end, preflet):
    return lambda v: p_temporary_uc(begin, end, preflet, v)


preferences = {
"tappers": {
        "anne":     (p_borrel(100,  0,  0),),
        "annette":  (p_borrel(100,100,  0),),
        # In words:  Bas prefers the first and second shift,
        # but not the last shift and not after 12.00 PM.
        "bas":      (p_borrel(100,100,0,hm2s(24)),),
        "bente":    (p_borrel(100, 50,  0),),
        # In words:  Bram prefers the last shift,
        # except (as an example) from november first to november seventh,
        # in which period his prefers to do nothing.
        "bramw":    (p_temporary(
                        datetime(2011,11,1),datetime(2011,11,7), 
                        p_borrel(0,0,0)), 
                     p_borrel(  0,  0,100),),
        "carlien":  (p_borrel( 50, 50, 50),),
        "chaim":    (p_borrel(100,100,100),),
        "dennisi":  (p_borrel(100,100,  0),),
        "frits":    (p_borrel( 50,100,  0),),
        "hugo":     (p_borrel( 50,100,100),),
        "jean":     (p_borrel(  0,  0, 50),),
        "jille":    (p_borrel(  0,  0,  0),),
        "judithvds":(p_borrel(100,100,  0),),
        "jurrien":  (p_borrel( 50,100,100),),
        "koen":     (p_borrel( 50, 50, 50),),
        "lisa":     (p_borrel(  0,100,100),),
        "loesje":   (p_borrel(100,100,  0),),
        "loesje":   (p_borrel(100,100,  0),),
        "louise":   (p_borrel( 50, 50, 50),),
        "manon":    (p_borrel(  0,  0, 50),),
        "niek":     (p_borrel(100,100,  0),),
        "nieks":    (p_borrel(  0,100,  0),),
        "olivier":  (p_borrel(100, 50,  0),),
        "petervdv": (p_borrel(100,100,100),),
        "remco":    (p_borrel( 50, 50, 50),),
        "rik":      (p_borrel(100,100, 50),),
        "robin":    (p_borrel( 50, 50,  0),),
        "sara":     (p_borrel(  0, 50, 50),),
        "shane":    (p_borrel(100,100,  0),),
        "simon":    (p_borrel(100,100, 50),),
        "steef":    (p_borrel(100,100,100),),
        "tijn":     (p_borrel(100,100,  0),),
        "timj":     (p_borrel(  0,100,  0),),
        "tomn":     (p_borrel(100,100,  0),),
},
"draai": {
        "bart":       (p_borrel(100,100,  0),),
        "barts":      (p_borrel(100,100,  0),),
        "bas":        (p_borrel(100,100,  0),),
        "daansp":     (p_borrel(100,100, 50),),
        "felix":      (p_borrel(100,100,  0),),
        "ids":        (p_borrel(100,100,  0),),
        "jille":      (p_borrel(100,100, 50),),
        "koen":       (p_borrel(  0,  0,  0),),
        "lisettevdl": (p_borrel(  0,  0,  0),),
        "marjolijn":  (p_borrel(  0,  0,  0),),
        "michiel":    (p_borrel(  0,100,100),),
        "mikel":      (p_borrel(  0,  0,  0),),
        "pp":         (p_borrel(100,  0,  0),),
        "rik":        (p_borrel(100,100, 50),),
        "robert":     (p_borrel(  0,  0,  0),),
        "sjorsg":     (p_borrel(100,100,100),),
        "stan":       (p_borrel(100,100,  0),),
        "vincentp":   (p_borrel(100,100,100),),
        "yurre":      (p_borrel(100,100,100),),
}}

def planning_vacancy_worker_score(vacancy, worker):
    un = worker.username
    pn = vacancy.pool.name
    if pn not in preferences or un not in preferences[pn]:
        # If the preferences of a worker have not been set,
        # asume (s)he is available so that we'll get his/her preferences asap.
        return 101
    for preflet in preferences[pn][un]:
        score = preflet(vacancy)
        if score!=False:
            return score
    # If nothing has been set, assume the worker is not available
    return 0
