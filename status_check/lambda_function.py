import json
import time

def get_current_time_utc():
    '''
    Return the current date and time
    date : DD/MM/YYY
    time: HH:MM:SS - 24 hour time
    '''
    frmt = '%d/%m/%Y %H:%M:%S'
    return time.strftime(frmt,time.gmtime())

def lambda_handler(event, context):
    '''
    Checks if the API is live, returning its version
    and current UTC time
    '''
    current_time = get_current_time_utc()

    return {
        'statusCode' : 200,
        'body' : f"Music API V0.1 as of {current_time}"

    }