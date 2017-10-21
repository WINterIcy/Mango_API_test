import hashlib
import json
import requests
import time
import logging

class requests_to_Mango_API(object):
    logging.basicConfig(filename='Mango_API_exec.log',level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s:%(message)s')

    """Class contain methods ,which work with Mango API statisic module. """

    def __init__(self, vpbx_api_key, vpbx_api_salt,detailed_log = False):
        """Constructor
                parameters: vpbx_api_key(str) - API key,
                            vpbx_api_salt(str) - API salt,
                            detailed_log(bool) - Logging all actions"""
        self.vpbx_api_key = vpbx_api_key
        self.vpbx_api_salt = vpbx_api_salt
        self.additional_info = log
        self.url = ""
        self.jsn = ""
        self.start_date = ""
        self.end_date = ""
        self.sign = ""
    def sign_return_mango_office(self):
        """create sha256 sign bases on key + json + salt."""
        if(self.additional_info):
            logging.info('call method: sign_return_mango_office')
        if(type(self.jsn) == dict):
            self.jsn = json.dumps(self.jsn,separators=(',', ':'))
        self.sign = hashlib.sha256(self.vpbx_api_key.encode('UTF-8')+self.jsn.encode('UTF-8')+self.vpbx_api_salt.encode('UTF-8')).hexdigest()
        if(self.additional_info):
            logging.info('method sign_return_mango_office worked: sign - {}'.format(self.sign[0:15]))
    def request_to_mango(self):
        """send reqest to mango with json and sign.
                return a request object"""
        if(self.additional_info):
            logging.info('call method: request_to_mango')
        self.sign_return_mango_office()
        response = requests.post(self.url,data={'vpbx_api_key': self.vpbx_api_key, 'sign':self.sign,'json':self.jsn})
        if(self.additional_info):
            logging.info('method request_to_mango worked: response_code - {}'.format(response.status_code))
        return response
    def request_call_log_one_query(self):
        """send reqest to get call log in one query (less than one month).
                return CSV string with \n ',' , ';' separators"""
        if(self.additional_info):
            logging.info('call method request_call_log_one_query')
            logging.info('From {} to {}'.format(self.start_date,self.end_date))
        self.jsn = {'date_from' : self.start_date, 'date_to' : self.end_date}
        self.url = 'https://app.mango-office.ru/vpbx/stats/request'
        response_w1 = self.request_to_mango()
        if(self.additional_info):
            logging.info('Current response: status_code - {},text - {}'.format(str(response_w1.status_code),str(response_w1.text[0:15])))
        self.jsn = response_w1.json()
        self.url = 'https://app.mango-office.ru/vpbx/stats/result'
        i = 0
        tries = 50
        if (response_w1.status_code == 200):
            while(i<tries):
                response_w = self.request_to_mango()
                if(self.additional_info):
                    logging.info('Try №{} to get answer'.format(str(i+1)))
                if(response_w.status_code == 200):
                    i = tries
                    if(self.additional_info):
                        logging.info('Ok answer is return with status code 200')
                        logging.info('method request_call_log_one_query worked: response_code - {} text - {}...'.format(response_w.status_code,response_w.text[0:30]))
                    return response_w.text
                elif(response_w.status_code == 404):
                    i = tries
                    if(self.additional_info):
                        logging.error('Wrong answer. Status_code - {} text - {}'.format(str(response_w.status_code),str(response_w.text)))
                        logging.info('method request_call_log_one_query worked: response_code - {} text - {}...'.format(response_w.status_code,response_w.text[0:30]))
                    return 0
                elif(response_w.status_code == 204):
                    if(self.additional_info):
                        logging.info('Ok answer is return with status code 204:Wait a content. Wait 5 seconds before next try')
                    i = i + 1
                    time.sleep(5)
                else:
                    i = tries
                    if(self.additional_info):
                        logging.warning('Unknown answer. Status_code - {} text - {}'.format(str(response_w.status_code),str(response_w.text)))
                        logging.info('method request_call_log_one_query worked: response_code - {} text - {}...'.format(response_w.status_code,response_w.text[0:30]))
                    return 0
        else:
            if(self.additional_info):
                logging.warning('Unknown answer. Status_code:{} text:{}'.format(str(response_w1.status_code),str(response_w1.text)))
                logging.info('method request_call_log_one_query worked: response_code - {} text - {}...'.format(response_w.status_code,response_w.text[0:30]))
                return 0

    def request_call_log_multiple_query(self):
        """send reqest to get call log in multiple query (greater than one month). return CSV string with '\n' ',' , ';' separators"""
        if(self.additional_info):
            logging.info('call method: request_call_log_multiple_query')
        i = 0
        result_st = ""
        st = int(self.start_date)
        end = int(self.end_date)
        while ((end - st)/86400 > 30 & i < 25):
            st_t = st
            end_t = st + 2591999
            if(end_t >= end):
                end_t = end
            if(self.additional_info):
                logging.info('Query №{} with start in {} end in {}'.format(str(i+1), int(st_t),int(end_t)))

            self.start_date = str(int(st_t))
            self.end_date = str(int(end_t))
            curr_req = self.request_call_log_one_query()
            if(curr_req == 0):
                if(self.additional_info):
                    logging.info("Long time for wait answer, breaking")
                return 0
            else:
                result_st = result_st + str(curr_req)
            result_st = result_st + str(self.request_call_log_one_query())
            i = i + 1
            st = end_t
        logging.info('method worked: request_call_log_multiple_query: text - {}...'.format(result_st[0:30]))
        return result_st
    def request_call_log_query(self,start_date='',end_date=''):
        """send reqest to get call log start and end date must a POSIX value str example '1325376000'.
                return CSV string with '\n' ',' , ';' separators"""
        if(self.additional_info):
            logging.info('call method: request_call_log_query')
        if(type(start_date) == str and type(end_date) == str):
            try:
                if((int(start_date) < int(end_date)) and (int(start_date)>1325376000) and (int(end_date)<2208988800)):
                    self.start_date = start_date
                    self.end_date = end_date
                    st = int(self.start_date)
                    end = int(self.end_date)
                    result_st = "records;start;finish;answer;from_extension;from_number;to_extension;to_number;disconnect_reason;line_number;location\n"
                    if (end - st)/86400 < 30:
                        self.start_date = str(int(st))
                        self.end_date = str(int(end))
                        result_st = result_st + self.request_call_log_one_query()
                    else:
                        self.start_date = str(int(st))
                        self.end_date = str(int(end))
                        result_st = result_st + self.request_call_log_multiple_query()
                    if(self.additional_info):
                        logging.info('method request_call_log_query worked: text - {}'.format(result_st[0:30]))
                        return result_st
                else:
                    logging.error('Wrong date input!')
                    return 0
            except Exception:
                logging.error('Wrong date input!')
                return 0
